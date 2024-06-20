import requests

url = "http://127.0.0.1:5000/api/forecast"
key = "35b417e58b07f0148e2e8417d99a5b83af51e669"

# data = {"key": key,
#         "placeid": 1,
#         "date": "2024-06-22",
#         "condition": 4,
#         "temperature": 22.5,
#         "rain": 0,
#         "humidity": 40,
#         "wind": 2,
#         "wind_direction": "SO"}
#
# req = requests.put(url, data=data)
#
# print(req)
# print(req.text)

data = {"key": key,
        "forecastid": 8}
req = requests.delete(url, data=data)

print(req)
print(req.text)
