import requests
import json

with open("ibm_creds.json", "r") as f:
    creds = json.loads(f.read())


def labels(note):
    url = creds["url"] + "/v1/analyze?version=2019-07-12"
    print(url)
    headers = {
        'Content-Type': 'application/json'
    }
    print(headers)
    print(note.content)
    payload = {
        "text": note.content,
        "features": {
            "categories": {}
        }
    }
    response = requests.request(
        "POST", url, headers=headers, data=json.dumps(payload), auth=('apikey', creds['apikey']))
    respJson = response.json()
    print(respJson)
    if("categories" in respJson):
        categories = list(
            set(map(lambda x: x["label"].split("/")[1], respJson['categories'])))
        return categories
    return []
