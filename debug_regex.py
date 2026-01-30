import re

url = "https://www.udemy.com/certificate/UC-123456"
pattern = r"https?://(www\.)?udemy\.com/certificate/UC-[a-zA-Z0-9-]+"

print(f"Pattern: {pattern}")
print(f"URL:     {url}")

match = re.match(pattern, url)
print(f"Match:   {match}")

if match:
    print("MATCHED!")
else:
    print("FAILED!")
