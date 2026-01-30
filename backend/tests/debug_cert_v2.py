from playwright.sync_api import sync_playwright

def debug_udemy(url):
    print(f"Checking URL with Playwright: {url}")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Add user agent to look even more real (optional but good practice)
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        page = context.new_page()
        try:
            response = page.goto(url)
            print(f"Status Code: {response.status}")
            
            # Wait for some content to load if needed, but for now just get what we have
            try:
                page.wait_for_load_state("networkidle", timeout=10000)
            except:
                print("Timeout waiting for networkidle, proceeding anyway.")

            title = page.title()
            print(f"Page Title: {title}")
            
            content = page.content()
            
            if "Certificate" in title:
                print("Match: 'Certificate' found in title.")
            elif "Udemy" in title:
                 print("Match: 'Udemy' found in title.")
            else:
                print("No match in title.")
                
            if "Udemy" in content:
                print("Match: 'Udemy' found in body.")
            else:
                print("No match in body.")
                
        except Exception as e:
            print(f"Error: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    # Test link provided in the original file
    debug_udemy("https://www.udemy.com/certificate/UC-011aea85-6526-4e68-ade5-02763e2f10a1/")
