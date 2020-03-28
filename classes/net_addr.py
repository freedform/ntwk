from netaddr import *
import re


class AddressMod:
    space_re_1 = r"^\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3} \d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}$"
    space_re_2 = r"^\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3} \d{1,2}$"
    dash_re_1 = r"^\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}\/\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}$"
    dash_re_2 = r"^\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}\/\d{1,2}$"

    def __init__(self, raw_data):
        if re.match(self.space_re_1, raw_data) or re.match(self.space_re_2, raw_data):
            raw_data = '/'.join(raw_data.split())
        elif re.match(self.dash_re_1, raw_data) or re.match(self.dash_re_2, raw_data):
            pass
        else:
            return
        self.net = IPNetwork(raw_data)

    def host(self):
        return f"{self.net.ip}"

    def mask(self):
        return self.net.netmask

    def prefix(self):
        return self.net.prefixlen

    def wildcard(self):
        return self.net.hostmask

    def network(self):
        return self.net.network

    def broadcast(self):
        return self.net.broadcast

    def net_prefix(self):
        return f'{self.network()}/{self.prefix()}'

    def net_mask(self):
        return f'{self.network()}/{self.mask()}'

    def net_wildcard(self):
        return f'{self.network()}/{self.wildcard()}'

    def last_ip(self, count):
        ip_list = list(self.net)[:-1:]
        if len(ip_list) > count:
            return [str(x) for x in ip_list[-count:]]
        else:
            print(f"Error: count value = {count} is >= than {len(ip_list)}")

    @staticmethod
    def ip_in_net(ip, net):
        ip_address = IPAddress(ip)
        ip_network = IPNetwork(net)
        if ip_address in ip_network:
            return True
        return False

    @staticmethod
    def ip_compare(first, second):
        start = IPAddress(first)
        end = IPAddress(second)
        if start < end:
            return True
        return False
