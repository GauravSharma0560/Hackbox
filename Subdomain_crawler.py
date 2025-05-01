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
discovered_subdomains = []

# Replace with your path or ensure Subdomain.txt exists in the same directory
with open("Subdomain.txt", "r") as wordlist_file:
    for line in wordlist_file:
        word = line.strip()
        test_url = word + "." + target_url
        response = request(test_url)
        if response:
            print(" [+] Discovered domain --> " + test_url)
            discovered_subdomains.append(test_url)

# ✅ Save discovered domains to JSON
with open("discovered_subdomains.json", "w") as outfile:
    json.dump(discovered_subdomains, outfile, indent=4)

print(f"\nTotal {len(discovered_subdomains)} subdomains found. Saved to 'discovered_subdomains.json'.")
