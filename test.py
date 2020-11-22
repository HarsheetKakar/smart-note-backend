import http.client

conn = http.client.HTTPSConnection("localhost", 5000)
payload = "{\r\n    \"first_name\":\"harsheet\",\r\n    \"last_name\":\"saxena\",\r\n    \"email\":\"harshsaxena1999@gmail.com\",\r\n    \"password\":\"123456\"\r\n}"
headers = {}
conn.request("POST", "/user/", payload, headers)
res = conn.getresponse()
data = res.read()
print(data.decode("utf-8"))
