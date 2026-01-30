
import requests
from bs4 import BeautifulSoup

def debug_udemy(url):
    print(f"Checking URL: {url}")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
    }
    try:
        response = requests.get(url, headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.title.string if soup.title else "No Title"
            print(f"Page Title: {title}")
            
            if "Certificate" in title:
                print("Match: 'Certificate' found in title.")
            else:
                print("No match in title.")
                
            if "Udemy" in response.text:
                print("Match: 'Udemy' found in body.")
            else:
                print("No match in body.")
                
            # Print a snippet to see what we got
            print(f"Content Snippet: {response.text[:500]}")
        else:
            print("Failed to get 200 OK")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_udemy("https://www.udemy.com/certificate/UC-011aea85-6526-4e68-ade5-02763e2f10a1/")
