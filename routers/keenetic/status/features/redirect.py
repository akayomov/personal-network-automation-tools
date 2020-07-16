from ..logger import warn, log


class RedirectChecker:
    def __init__(self, config, rci):
        log("Checking redirect feature", config)
        super(RedirectChecker, self).__init__()
        self.rci = rci
        self.config = config

        status = True

        try:
            if self.config['routing']['type'] == 'static':
                status = self.check_routing(self.config['routing']['list']) if status else False
            if self.config['vpn']['type'] == 'wireguard':
                status = self.check_wireguard(self.config['vpn']) if status else False
        except KeyError:
            warn("RedirectChecker faced with wrong config")

        if status:
            self.data = 'on' if self.config['status'] else 'off'
        else:
            self.data = 'error'

    def check_routing(self, requirements) -> bool:
        table = self.rci('/show/ip/route')
        result = True

        for requirement in requirements:
            if result:
                filtered = table
                for field in requirement:
                    filtered = list(filter(lambda i: i[field] == requirement[field], filtered))
                if len(filtered) == 0:
                    result = not self.config['status']
        return result

    def check_wireguard(self, config) -> bool:
        peers = self.rci('/show/rc/interface/Wireguard0/wireguard/peer')
        peer = list(filter(lambda p: p['comment'] == config['peer'], peers))[0]
        result = True

        for requirement in config['subnets']:
            if result:
                occurred = False
                for subnet in peer['allow-ips']:
                    if subnet == requirement:
                        occurred = True
                result = False if occurred is not self.config['status'] else True
        return result
