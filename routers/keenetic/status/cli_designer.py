import os
from functools import reduce


class CLIDesigner:
    def __init__(self, status):
        [self.width, self.height] = os.get_terminal_size(0)

        # # Color Matrix
        # f = ""
        # b = ""
        # for l in range(0, 6):
        #     for r in range(0, 36):
        #         code = 16 + (l * 36 + r)
        #         f += self.colorize(code, 255) + str(code).ljust(4) + self.decorate(0)
        #         b += self.colorize(255, code) + str(code).ljust(4) + self.decorate(0)
        #     f += "\n"
        #     b += "\n"
        # print(f)
        # print(b)

        output = ""

        output += self.info_line(status['info'], self.width) + "\n"
        if self.width > 60:
            half = int(self.width / 2)
            output += self.system_line(status['system'], half + (self.width % 2))
            output += self.internet_line(status['internet'], half) + "\n"
            output += self.provider_line(status['provider'], half + (self.width % 2))
            output += self.tunnels_line(status['tunnels'], half) + "\n"
        else:
            output += self.system_line(status['system'], self.width) + "\n"
            output += self.internet_line(status['internet'], self.width) + "\n"
            output += self.provider_line(status['provider'], self.width) + "\n"
            output += self.tunnels_line(status['tunnels'], self.width) + "\n"
        output += self.features_line(status['features'], self.width) + "\n"
        output += self.devices_line(status['devices'], self.width)

        lines = len(output.split("\n")) + 1
        output += "\n" * (self.height - lines)

        print(output)

    @staticmethod
    def colorize(foreground, background):
        dec = ""
        if foreground > 0:
            dec += "\x1b[38;5;" + str(foreground) + "m"
        if background > 0:
            dec += "\x1b[48;5;" + str(background) + "m"
        return dec

    @staticmethod
    def decorate(decorator):
        return "\x1b[" + str(decorator) + "m"

    @staticmethod
    def c(marker, message):
        cleaner = CLIDesigner.decorate(0)
        color = {
            '0t': CLIDesigner.colorize(220, -1) + CLIDesigner.decorate(1),
            '0c': CLIDesigner.colorize(208, -1),
            '1c': CLIDesigner.colorize(232, 255) + CLIDesigner.decorate(1),
            '1t': CLIDesigner.colorize(232, 255),
            '1l': CLIDesigner.colorize(245, 255),
            '1r': CLIDesigner.colorize(255, 160) + CLIDesigner.decorate(1),
            '1y': CLIDesigner.colorize(232, 214),
            '1g': CLIDesigner.colorize(28, 255),
            '2c': CLIDesigner.colorize(232, 248) + CLIDesigner.decorate(1),
            '2t': CLIDesigner.colorize(232, 248),
            '2l': CLIDesigner.colorize(238, 248),
            '2r': CLIDesigner.colorize(248, 124),
            '2g': CLIDesigner.colorize(248, 28),
            '2rt': CLIDesigner.colorize(248, 124) + CLIDesigner.decorate(1),
            '2gt': CLIDesigner.colorize(248, 28) + CLIDesigner.decorate(1),
            '3c': CLIDesigner.colorize(81, -1) + CLIDesigner.decorate(1),
            '3on': CLIDesigner.colorize(18, 81) + CLIDesigner.decorate(1),
            '3of': CLIDesigner.colorize(81, 18) + CLIDesigner.decorate(1),
            '3er': CLIDesigner.colorize(196, -1) + CLIDesigner.decorate(1),
            '4c': CLIDesigner.colorize(250, -1) + CLIDesigner.decorate(1),
            '4t': CLIDesigner.colorize(245, -1),
            '4l': CLIDesigner.colorize(240, -1) + CLIDesigner.decorate(1),
        }
        return color.get(marker, cleaner) + message + cleaner

    def info_line(self, info, size) -> str:
        space = size
        line = ""

        for key in info:
            i = key+": "+str(info[key])+' '
            if space > len(i):
                line += self.c('0c', key+": ")+self.c('0t', str(info[key])+" ")
                space -= len(i)

        if space > len("Info:"):
            if space > len("Information: "):
                line = self.c('0t', "Information: ")+line
                space -= len("Information: ")
            else:
                line = self.c('0t', "Info: ")+line
                space -= len("Info: ")

        if space > 0:
            line += self.c('other', ' ' * space)
        return line

    def system_line(self, system, size) -> str:
        space = size
        line = ""

        for item in ['cpu', 'ram', 'hdd', 'tmp']:
            if space > 4:
                if system[item] > 70:
                    marker = '1r'
                elif system[item] > 40:
                    marker = '1y'
                else:
                    marker = '1g'
                line += self.c(marker, item.upper().ljust(4))
                space -= 4

        for item in ['ssh', 'ftp', 'bkp']:
            if space > 4:
                marker = '1g' if system[item] else '1r'
                line += self.c(marker, item.upper().ljust(4))
                space -= 4

        if space > 0:
            line += self.c('1t', ' ')
            space -= 1

        uptime = str(system['uptime'])+" "
        if space > len(uptime):
            uptime_line = self.c('1l', uptime)
            space -= len(uptime)

            if space > len("Uptime:"):
                uptime_line = self.c('1c', "Uptime:")+uptime_line
                space -= len("Uptime:")
            line += uptime_line

        if space > len("SYS:"):
            if space > len("System: "):
                line = self.c('1c', "System: ")+line
                space -= len("System: ")
            else:
                line = self.c('1c', "SYS: ")+line
                space -= len("SYS: ")

        if space > 0:
            line += self.c('1t', ' ' * space)
        return line

    def internet_line(self, internet, size) -> str:
        space = size
        line = ""

        for item in ['access', 'link', 'gateway', 'dns']:
            i = item + ' '
            if space > len(i):
                marker = '1g' if internet[item] else '1r'
                line += self.c(marker, i)
                space -= len(i)

        if space > 0:
            line += self.c('1t', ' ')
            space -= 1

        ip = internet['ip'] + " "
        if space > len(ip):
            ip_line = self.c('1t', ip)
            space -= len(ip)

            if space > len('IP:'):
                ip_line = self.c('1c', "IP:") + ip_line
                space -= len("IP:")
            line += ip_line

        uptime = str(internet['uptime']) + " "
        if space > len(uptime):
            uptime_line = self.c('1l', uptime)
            space -= len(uptime)

            if space > len("Uptime:"):
                uptime_line = self.c('1c', "Uptime:")+uptime_line
                space -= len("Uptime:")
            line += uptime_line

        if space > len("NET:"):
            if space > len("Network: "):
                line = self.c('1c', "Network: ")+line
                space -= len("Network: ")
            else:
                line = self.c('1c', "NET: ")+line
                space -= len("NET: ")

        if space > 0:
            line += self.c('1t', ' ' * space)
        return line

    def provider_line(self, provider, size) -> str:
        space = size
        line = ""

        for key in provider:
            i = key+": "+str(provider[key])+' '
            if space > len(i):
                line += self.c('2t', key+": ")+self.c('2l', str(provider[key])+" ")
                space -= len(i)

        if space > len("ISP:"):
            if space > len("Provider: "):
                line = self.c('2c', "Provider: ")+line
                space -= len("Provider: ")
            else:
                line = self.c('2c', "ISP: ")+line
                space -= len("ISP: ")

        if space > 0:
            line += self.c('2t', ' ' * space)
        return line

    def tunnels_line(self, tunnels, size) -> str:
        space = size
        line = ""

        for tunnel in tunnels:
            i = " ["+tunnel['type'][0].upper()+"] "+tunnel['name']+' '
            m = '2g' if tunnel['online'] else '2r'
            m2 = '2gt' if tunnel['online'] else '2rt'
            if space > len(i):
                line += self.c(m, " ["+tunnel['type'][0].upper()+"] ")+self.c(m2, tunnel['name']+' ')
                space -= len(i)

                if space > 0:
                    line += self.c('2t', ' ')
                    space -= 1

        if space > len("TUN:"):
            if space > len("Tunnels: "):
                line = self.c('2c', "Tunnels: ")+line
                space -= len("Tunnels: ")
            else:
                line = self.c('2c', "TUN: ")+line
                space -= len("TUN: ")

        if space > 0:
            line += self.c('2t', ' ' * space)
        return line

    def features_line(self, features, size) -> str:
        space = size
        line = ""

        for feature in features:
            if space > len(feature) + 2:
                if features[feature] == 'on':
                    marker = '3on'
                elif features[feature] == 'off':
                    marker = '3of'
                else:
                    marker = '3er'
                line += self.c(marker, " "+feature+" ")
                space -= len(feature) + 2

                if space > 0:
                    line += self.c('3c', ' ')
                    space -= 1

        if space > len("FX:"):
            if space > len("Features: "):
                line = self.c('3c', "Features: ")+line
                space -= len("Features: ")
            else:
                line = self.c('3c', "FX: ")+line
                space -= len("FX: ")

        if space > 0:
            line += self.c('other', ' ' * space)
        return line

    def devices_line(self, devices, size) -> str:
        space = size

        max_ip = len(reduce(lambda a, b: a if len(a['ip']) > len(b['ip']) else b, devices)['ip'])
        ip_enabled = False
        if space > max_ip:
            ip_enabled = True
            space -= max_ip

        max_mac = len(reduce(lambda a, b: a if len(a['mac']) > len(b['mac']) else b, devices)['mac'])
        mac_enabled = False
        if space > max_mac + 3:
            mac_enabled = True
            space -= (max_mac + 3)

        max_host = len(reduce(lambda a, b: a if len(a['hostname']) > len(b['hostname']) else b, devices)['hostname'])
        host_enabled = False
        if space > max_host + 3:
            host_enabled = True
            space -= (max_host + 3)

        type_enabled = False
        if space > 10:
            type_enabled = True

        lines = []
        for device in devices:
            line = ""
            if type_enabled:
                if device['connection']['type'] == 'wired':
                    line += self.c('4l', str("eth"+str(device['connection']['speed'])).rjust(7))
                elif device['connection']['type'] == 'unknown':
                    line += self.c('4l', "other".rjust(7))
                elif device['connection']['mode'] == '11n':
                    line += self.c('4l', "wifi4".rjust(7))
                elif device['connection']['mode'] == '11ac':
                    line += self.c('4l', "wifi5".rjust(7))
                else:
                    line += self.c('4l', "other".rjust(7))
                line += self.c('4l', " | ")

            if host_enabled:
                line += self.c('4t', device['hostname'] + " "*(max_host - len(device['hostname'])))
                line += self.c('4l', " | ")
            if ip_enabled:
                line += self.c('4c', device['ip'] + " "*(max_ip - len(device['ip'])))
            if mac_enabled:
                line += self.c('4l', " | ")
                line += self.c('4t', device['mac'] + " "*(max_mac - len(device['mac'])))
            lines.append(line)
        return "\n".join(lines)
