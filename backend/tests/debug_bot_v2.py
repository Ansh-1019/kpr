
import requests
from io import BytesIO
from PIL import Image
import os

def create_dummy_image():
    # Create a 100x100 RGB image
    img = Image.new('RGB', (100, 100), color = 'red')
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format='JPEG')
    img_byte_arr.seek(0)
    return img_byte_arr

def test_analyze():
    url = "http://127.0.0.1:8000/api/bot/analyze-image"
    print(f"Testing URL: {url}")
    
    try:
        img_data = create_dummy_image()
        files = {'file': ('test.jpg', img_data, 'image/jpeg')}
        
        response = requests.post(url, files=files)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Text: {response.text}")
        
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_analyze()
