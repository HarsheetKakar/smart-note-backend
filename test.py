import requests
import json
creds = json.loads(open('ibm_creds.json', "r").read())

url = "https://api.eu-gb.natural-language-understanding.watson.cloud.ibm.com/instances/7f0506cc-f5d7-44dc-9327-180348074542/v1/analyze?version=2019-07-12"

payload = "{\n  \"text\": \"The 2017 EFL Trophy Final was an association football match that was played on 2 April 2017 at Wembley Stadium, London, between League One teams Coventry City and Oxford United. The match decided the winner of the 2016–17 EFL Trophy, a 64-team knockout tournament comprising clubs from League One and League Two of the English Football League (EFL), as well as 16 Category One academy sides representing Premier League and Championship clubs. It was Coventry's first appearance in the final and the second for Oxford, who had been beaten by Barnsley in the previous season's match. The game was played in front of a crowd of 74,434, the highest attendance for the final since the opening of the new Wembley Stadium. Coventry won 2–1 to earn their first major trophy since their victory in the 1987 FA Cup Final. The win was a highlight for Coventry's supporters in what was otherwise a disappointing season, as they were relegated to League Two\",\n    \"features\": {\n        \"categories\": {},\n        \"concepts\": {}\n    }\n}".encode(
    'utf-8')
headers = {
    'Content-Type': 'application/json',
}

response = requests.request(
    "POST", url, headers=headers, data=payload))

print(response.text)
