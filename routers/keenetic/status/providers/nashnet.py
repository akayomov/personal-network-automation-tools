import requests
from requests.exceptions import ConnectionError, HTTPError
from html.parser import HTMLParser
from ..logger import warn, log


class NashnetISPParser(HTMLParser):

    def error(self, message):
        warn("NashnetISPParser error:", message)

    def __init__(self, username, password):
        log("Parsing nashnet provider status")
        super(NashnetISPParser, self).__init__()
        self.data = {"name": "nashnet"}
        url = "https://my.nashnet.ua/index.php?mod=profile"

        try:
            session = requests.Session()
            headers = {"Accept": "application/signed-exchange"}

            session.post(url, data={"login": username, "password": password}, headers=headers, timeout=10)
            profile = session.post(url, headers=headers)

            self.__parse = False
            self.__counter = 0
            self.feed(profile.text)
        except ConnectionError:
            warn("Connection error happened during request to ISP")
            self.data["error"] = "connection"
        except HTTPError:
            warn("HTTP error happened during request to ISP")
            self.data["error"] = "http"

    def handle_starttag(self, tag, attrs):
        if tag in ['a', 'b', 'td']:
            self.__counter += 1
            self.__parse = True

    def handle_endtag(self, tag):
        # if self.__parse and tag in ['font', 'td']:
        self.__parse = False

    # noinspection PyTypeChecker
    def handle_data(self, data):
        if self.__parse:
            # print(self.__counter)
            # print(data.strip())

            if self.__counter == 27:
                self.data["account_id"] = data.strip()
            if self.__counter == 60:
                self.data["balance"] = float(data.strip().split(" ")[0].replace(',', '.'))
            if self.__counter == 66:
                self.data["expiration_date"] = data.strip()
            if self.__counter == 73:
                self.data["subscription"] = data.strip()
            if self.__counter == 75:
                self.data["payment_fee"] = float(data.strip().split(" ")[0].replace(',', '.'))
