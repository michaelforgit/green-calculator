import http.client

conn = http.client.HTTPSConnection("api.collectapi.com")

headers = {
    'content-type': "application/json",
    'authorization': "apikey 11cR6VdvfuCtgg9VuZ5BpM:4MGvw1IKe1LPtBCQwC2o6F"
    }

conn.request("GET", "/gasPrice/allUsaPrice", headers=headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))