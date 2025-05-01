import requests
import json

web_name = input("Enter the website domain: ")

def request(url):
    try:
        return requests.get("http://" + url, timeout=5)
    except requests.exceptions.ConnectionError:
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error checking {url}: {e}")
        return None

target_url = web_name
discovered_urls = []

# Make sure 'url_filenames.txt' exists in the same directory
with open("url_filenames.txt", "r") as wordlist_file:
    for line in wordlist_file:
        word = line.strip()
        test_url = target_url + "/" + word
        response = request(test_url)
        if response:
            print(" [+] Discovered URL --> " + test_url)
            discovered_urls.append(test_url)

# ✅ Write results to a JSON file
with open("discovered_urls.json", "w") as outfile:
    json.dump(discovered_urls, outfile, indent=4)

print(f"\nTotal {len(discovered_urls)} URLs found. Saved to 'discovered_urls.json'.")
