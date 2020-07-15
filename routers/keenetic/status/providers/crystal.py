import requests
from requests.exceptions import ConnectionError, HTTPError
from ..logger import warn, log


class CrystalISPParser:

    def __init__(self, username, password):
        log("Parsing crystal provider status")
        self.data = {"name": "crystal"}
        try:
            auth = requests.post("https://api.prosto.net/auth", json={
                "login": username,
                "password": password,
            }).json()

            resp = requests.get("https://api.prosto.net/objects", headers={
                'Authorization': 'Bearer '+auth["token"]
            }).json()
            self.data['account_id'] = resp[0]["id"]
            self.data['balance'] = float(resp[0]["balance"])
            self.data['bonus'] = float(resp[0]["bonus"])
            self.data['payment_fee'] = float(resp[0]["fee_to_pay"])
            self.data['next_payment_fee'] = float(resp[0]["fee_next_month"])
            self.data['subscription'] = resp[0]["tariff"]["name"]

        except ConnectionError:
            warn("Connection error happened during request to ISP")
            self.data["error"] = "connection"
        except HTTPError:
            warn("HTTP error happened during request to ISP")
            self.data["error"] = "http"
