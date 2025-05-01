import re
import requests
import json
from urllib.parse import urljoin
from bs4 import BeautifulSoup

class Scanner:
    def __init__(self, url):
        self.session = requests.Session()
        self.target_url = url
        self.target_links = []
        self.vulnerabilities = []  # To store discovered vulnerabilities

    def extract_links_from(self, url):
        response = self.session.get(url)
        return re.findall('(?:href=")(.*?)"', response.content.decode(errors='ignore'))

    def crawl(self, url=None):
        if url is None:
            url = self.target_url
        href_links = self.extract_links_from(url)
        for link in href_links:
            link = urljoin(url, link)

            if "#" in link:
                link = link.split("#")[0]

            if self.target_url in link and link not in self.target_links:
                self.target_links.append(link)
                print(f"[+] Found link: {link}")
                self.crawl(link)

    def extract_forms(self, url):
        response = self.session.get(url)
        parsed_html = BeautifulSoup(response.content, 'html.parser')
        return parsed_html.find_all("form")

    def submit_form(self, form, value, url):
        action = form.get("action")
        post_url = urljoin(url, action)
        method = form.get("method")

        inputs_list = form.find_all("input")
        post_data = {}
        for input_item in inputs_list:
            input_name = input_item.get("name")
            input_type = input_item.get("type")
            input_value = input_item.get("value")
            if input_type == "text":
                input_value = value

            post_data[input_name] = input_value

        if method == "post":
            return self.session.post(post_url, data=post_data)
        
        return self.session.get(post_url, params=post_data)

    def run_scanner(self):
        for link in self.target_links:
            forms = self.extract_forms(link)
            for form in forms:
                print(f"[+] Testing Forms in {link}")
                # Test XSS in the form
                is_xss = self.test_xss_in_form(form, "<sCriPt>alert('test')</sCriPt>", link)
                if is_xss:
                    self.vulnerabilities.append({"url": link, "form": form, "vulnerability": "XSS"})
                    print(f"[*] XSS found in form on {link}")
                else:
                    print(f"[+] No XSS in form on {link}")

            if "=" in link:
                print(f"[+] Testing link: {link}")
                self.test_xss_in_link(link)

    def test_xss_in_form(self, form, value, url):
        xss_test_script = "<sCriPt>alert('test')</sCriPt>"
        response = self.submit_form(form, xss_test_script, url)
        if xss_test_script in response.content.decode():
            return True
        return False

    def test_xss_in_link(self, link):
        xss_test_script = "<sCriPt>alert('test')</sCriPt>"
        response = self.session.get(link + xss_test_script)
        if xss_test_script in response.content.decode():
            self.vulnerabilities.append({"url": link, "vulnerability": "XSS in link"})
            print(f"[*] XSS found in link: {link}")
        else:
            print(f"[+] No XSS in link: {link}")

    def save_to_json(self):
        with open("vulnerabilities.json", "w") as outfile:
            json.dump(self.vulnerabilities, outfile, indent=4)

def main():
    base_url = input("Enter the target URL: ").strip()
    scanner = Scanner(base_url)

    scanner.crawl()  # Start crawling the website
    scanner.run_scanner()  # Start scanning for vulnerabilities

    # Save discovered vulnerabilities to a JSON file
    scanner.save_to_json()

    print(f"\n[*] Vulnerabilities saved to 'vulnerabilities.json'.")

if __name__ == "__main__":
    main()

