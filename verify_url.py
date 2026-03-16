import requests

urls = [
    "https://priya-access.s3.ap-southeast-2.amazonaws.com/images/wallp.jpg",
    "https://priya-access.s3.ap-southeast-2.amazonaws.com/"
]

for url in urls:
    print(f"\nVerifying URL: {url}")
    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("Success! Access granted.")
        else:
            print(f"Failed! Content:\n{response.text[:200]}")
    except Exception as e:
        print(f"Error: {e}")
