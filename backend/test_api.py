import requests

url = "http://127.0.0.1:5000/api/chat"

res = requests.post(
    url,
    json={"prompt": "Photosynthesis"},
    cookies={"session": "test"}
)

print(res.status_code)
print(res.text)
 