import requests
from requests.exceptions import ConnectionError, HTTPError
from html.parser import HTMLParser
from ..logger import warn, log


class DomashkaISPParser(HTMLParser):

    def error(self, message):
        warn("DomashkaISPPareser error:", message)

    def __init__(self, username, password):
        log("Parsing domashkanet provider status")
        super(DomashkaISPParser, self).__init__(convert_charrefs=True)
        self.data = {"name": "domashkanet"}
        try:
            response = requests.post("https://stats.domashka.net/process.php", data={
                "dm_todo": "do_auth",
                "dm_data[username]": username,
                "dm_data[password]": password,
            }, stream=True)

            self.__parse = False
            self.__counter = 0
            self.feed(response.raw.read().decode('koi8_u'))
        except ConnectionError:
            warn("Connection error happened during request to ISP")
            self.data["error"] = "connection"
        except HTTPError:
            warn("HTTP error happened during request to ISP")
            self.data["error"] = "http"

    def handle_starttag(self, tag, attrs):
        if tag in ['font', 'td']:
            self.__counter += 1
            self.__parse = True

    def handle_endtag(self, tag):
        self.__parse = False

    # noinspection PyTypeChecker
    def handle_data(self, data):
        if self.__parse:
            # print(self.__counter)
            # print(data)

            if self.__counter == 15:
                self.data['balance'] = float(data.replace(',', '.'))
            if self.__counter == 16:
                [date, time] = data.split(" в ")
                date = list(date.split("-"))
                date.reverse()
                self.data['next_calculation'] = "-".join(date) + "T" + time + ".000Z"
            if self.__counter == 40:
                self.data['account_id'] = data.translate(str.maketrans('[]', '  ')).strip()
            if self.__counter == 60:
                self.data['payment_fee'] = int(data)
            if self.__counter == 62:
                self.data['subscription'] = data.strip()
