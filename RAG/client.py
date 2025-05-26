import requests
from PIL import Image
from io import BytesIO
import matplotlib.pyplot as plt
# Send POST request to Flask server
response = requests.post(
    "http://127.0.0.1:5000/process_text",
    json={"prompt": "Show images about Algeria"}
)

# Check if the request was successful
if response.status_code == 200:
    image_urls = response.json()
    print(image_urls)
    # for url in image_urls:
    #     img_resp = requests.get(url)
    #     if img_resp.status_code == 200:
    #         img = Image.open(BytesIO(img_resp.content))
    #         img.show()  # Opens image in default image viewer
       
else:
    print("Error:", response.text)
