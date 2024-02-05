import requests
import json

url = "https://api.promulgateinnovations.com/api/v1/fetchYoutubeAnalytics"

payload = json.dumps({
  "channelId": "UCq-Fj5jknLsUf-MWSy4_brA"
})
headers = {
  'Authorization': 'Basic cHJvbXVsZ2F0ZTpwcm9tdWxnYXRl',
  'Content-Type': 'application/json'
}

response = requests.post(url, headers=headers, data=payload)

print(response.text)
