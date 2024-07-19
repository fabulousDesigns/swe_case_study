import http.client
import json


def send_sms(to: str, message: str):
    conn = http.client.HTTPSConnection("z16rz6.api.infobip.com")
    payload = json.dumps({
        "messages": [
            {
                "destinations": [{"to": to}],
                "from": "ServiceSMS",
                "text": message
            }
        ]
    })
    headers = {
        'Authorization': 'App ac9d986eb238795d6a795a9b91f9b3b7-99347ff5-6560-4d8f-84ee-323bd0d5064c',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    conn.request("POST", "/sms/2/text/advanced", payload, headers)
    res = conn.getresponse()
    data = res.read()
    return data.decode("utf-8")