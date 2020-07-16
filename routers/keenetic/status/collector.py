from requests.exceptions import ConnectionError, HTTPError
from subprocess import getoutput as shell
from .logger import warn, log
import requests
import time
import json
import os

from .cli_designer import CLIDesigner

from .providers.domashkanet import DomashkaISPParser
from .providers.crystal import CrystalISPParser
from .providers.nashnet import NashnetISPParser

from .features.redirect import RedirectChecker


class StatusCollector:
    def __init__(self, action="cli"):
        self.status = None
        self.start_time = time.time()
        status = {
            "info": self.info(),
            "system": self.system(),
            "internet": self.internet(),
            "provider": self.provider(),
            "tunnels": self.tunnels(),
            "devices": self.devices(),
            "features": self.features(),
        }
        # noinspection PyTypeChecker
        status['info']['duration'] = round(time.time() - self.start_time, 2)
        self.process(action, status)

    @staticmethod
    def rci(url: str):
        log('Requesting RCI:', url)
        response = None
        try:
            response = requests.get("http://localhost:79/rci" + url).json()
        except ConnectionError:
            warn("Connection error happened during request to router")
        except HTTPError:
            warn("HTTP error happened during request to router")
        finally:
            return response

    def process(self, action, status):
        log('Processing collected status with action:', action)
        if action == "store":
            t = time.localtime(self.start_time)
            path = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                '..',
                                                'data',
                                                time.strftime("%Y_%m_%d", t) + ".json"))
            if os.path.exists(path):
                log_data = json.loads(open(path, 'r').read())
            else:
                log_data = {}

            if not str(t.tm_hour) in log_data:
                log_data[str(t.tm_hour)] = {}
            if not str(t.tm_min) in log_data[str(t.tm_hour)]:
                log_data[str(t.tm_hour)][str(t.tm_min)] = {}
            log_data[str(t.tm_hour)][str(t.tm_min)][str(t.tm_sec)] = status

            open(path, 'w').write(json.dumps(log_data, indent=4))

            log("Status update saved to file: " + path)
        elif action == "cli":
            CLIDesigner(status)
        elif action == "return":
            self.status = status
        else:
            warn("Unknown action used for collector will be ignored")

    def info(self) -> object:
        log('Collecting info')
        return {
            'node': shell('uname -n'),
            'time': time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.localtime(self.start_time)),
        }

    def system(self) -> object:
        log('Collecting system')
        result = {}

        status = self.rci("/show/system")
        if status is not None:
            result['cpu'] = status['cpuload']
            result['ram'] = int(100 * int(status['memory'].split("/")[0]) / int(status['memory'].split("/")[1]))
            result['uptime'] = int(status['uptime'])

            ports = list(map(lambda l: " ".join(l.split()).split(" "), shell("netstat -tulpn").split("\n")))
            while ports[0][0] != "Proto":
                ports.pop(0)
            ports.pop(0)
            ports = list(filter(lambda l: l[5] == "LISTEN", ports))
            ports = list(filter(lambda l: l[6] != "-", ports))

            result['ssh'] = len(list(filter(lambda l: l[6].split("/")[1] == "dropbear", ports))) > 0
            result['ftp'] = len(list(filter(lambda l: l[6].split("/")[1] == "pure-ftpd (SERV", ports))) > 0

            fstats = list(map(lambda line: " ".join(line.split()).split(" "), shell("df -h").split("\n")))
            while fstats[0][0] != "Filesystem":
                fstats.pop(0)
            fstats.pop(0)

            hdd_line = list(filter(lambda l: l[5] == "/opt", fstats))
            result['hdd'] = int(hdd_line[0][4].split("%")[0]) if len(hdd_line) == 1 else 0

            tmp_line = list(filter(lambda l: l[5] == "/tmp", fstats))
            result['tmp'] = int(tmp_line[0][4].split("%")[0]) if len(tmp_line) == 1 else 0

            if len(tmp_line) == 1:
                backup_fs = "/dev/sda2" if hdd_line[0][0] == "/dev/sda1" else "/dev/sda1"
                bkp = list(filter(lambda line: line[0] == backup_fs, fstats))
                if len(bkp) == 1:
                    if os.listdir(bkp[0][5]) == ["install"]:
                        result['bkp'] = True if os.listdir(bkp[0][5] + "/install") == [
                            "core.firmware.tar.gz"] else False
                    else:
                        result['bkp'] = False
                else:
                    result['bkp'] = False
            else:
                result['bkp'] = False
        return result

    def internet(self) -> object:
        log('Collecting internet')
        result = {}
        internet_status = self.rci("/show/internet/status")
        interface_status = self.rci("/show/interface/ISP")
        if internet_status is not None and interface_status is not None:
            result["ip"] = interface_status["address"]
            result["uptime"] = interface_status["uptime"]
            result["link"] = interface_status["link"] == "up"
            result["gateway"] = internet_status["gateway-accessible"]
            result["dns"] = internet_status["dns-accessible"]
            result["access"] = internet_status["internet"]
        return result

    @staticmethod
    def provider() -> object:
        log('Collecting provider')
        path = "/storage/provider.info"
        if os.path.exists(path):
            provider = json.loads(open(path, 'r').read())

            case = {
                "domashkanet": DomashkaISPParser,
                "crystal": CrystalISPParser,
                "nashnet": NashnetISPParser,
            }
            current = case.get(provider['name'], lambda username, password: None)
            result = current(provider['login'], provider['password'])
            if result is None:
                return {}
            else:
                return result.data
        else:
            warn('No provider file found:', path)
            return {}

    def tunnels(self) -> list:
        log('Collecting tunnels')
        result = []

        tun_infos = self.rci('/show/rc/interface/Wireguard0/wireguard/peer')
        tun_statuses = self.rci('/show/interface/Wireguard0/wireguard/peer')

        for status in tun_statuses:
            result.append({
                "type": "wireguard",
                "name": list(filter(lambda t: t['key'] == status['public-key'], tun_infos))[0]['comment'],
                "online": status["online"],
            })
        return result

    def devices(self) -> list:
        log('Collecting devices')
        result = []

        devices = self.rci('/show/ip/hotspot/host')
        for device in devices:
            if device['active']:
                dev = {
                    'ip': device['ip'],
                    'mac': device['mac'],
                    'hostname': device['hostname'],
                }
                if 'speed' in device:
                    dev['connection'] = {
                        'type': 'wired',
                        'speed': int(device['speed']),
                    }
                elif 'mws' in device:
                    dev['connection'] = {
                        'type': 'wireless',
                        'mode': device['mws']['mode'],
                        'ht': device['mws']['ht'],
                        'gi': device['mws']['gi'],
                        'rssi': device['mws']['rssi'],
                    }
                else:
                    try:
                        dev['connection'] = {
                            'type': 'wireless',
                            'mode': device['mode'],
                            'ht': device['ht'],
                            'gi': device['gi'],
                            'rssi': device['rssi'],
                        }
                    except KeyError:
                        dev['connection'] = {
                            'type': 'unknown'
                        }
                result.append(dev)
        return result

    def features(self) -> object:
        log('Collecting features')
        path = "/storage/features.config"
        if os.path.exists(path):
            configuration = json.loads(open(path, 'r').read())

            result = {}
            case = {
                'redirect': RedirectChecker,
            }

            for config in configuration:
                checker = case.get(config['type'], lambda c, r: None)
                check = checker(config, self.rci)
                if check is None:
                    result[config['name']] = ''
                else:
                    result[config['name']] = check.data
            return result
        else:
            warn('No features file found:', path)
            return {}
