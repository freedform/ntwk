import ipaddress
import re


class AddressMod:
    space_re_1 = r"^\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3} \d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}$"
    space_re_2 = r"^\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3} \d{1,2}$"
    dash_re_1 = r"^\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}\/\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}$"
    dash_re_2 = r"^\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}\/\d{1,2}$"

    def __init__(self, raw_data):
        self.ip_interface = ipaddress.ip_interface(raw_data)
        self.ip_network = ipaddress.ip_network(self.ip_interface.network)

    def host(self):
        return str(self.ip_interface.ip)

    def mask(self):
        return str(self.ip_network.netmask)

    def prefix(self):
        return self.ip_network.prefixlen

    def wildcard(self):
        return str(self.ip_network.hostmask)

    def network(self):
        return str(self.ip_network.network_address)

    def broadcast(self):
        return str(self.ip_network.broadcast_address)

    def net_prefix(self):
        return self.ip_network.with_prefixlen

    def net_mask(self):
        return self.ip_network.with_netmask

    def net_wildcard(self):
        return self.ip_network.with_hostmask

    def last_ip(self, count):
        if len(self.net_hosts()) > count:
            return self.net_hosts()[-count:]
        else:
            raise Exception(f"Given count {count} is greater than hosts in network {self.ip_network}")

    def net_hosts(self):
        ip_list = list(self.ip_network.hosts())
        return [str(x) for x in ip_list]

    @staticmethod
    def net_range(first, second):
        range_list = []
        start = ipaddress.ip_address(first)
        second = ipaddress.ip_address(second)
        while start <= second:
            range_list.append(start)
            start += 1
        return [str(x) for x in range_list]

    @staticmethod
    def ip_in_net(ip, net):
        ip_addr = ipaddress.ip_address(ip)
        ip_net = ipaddress.ip_network(net)
        if ip_addr in ip_net:
            return True
        return False

    @staticmethod
    def ip_in_range(ip, ip_range):
        start, end = ip_range
        ip_address = str(ipaddress.ip_address(ip))
        net_range = AddressMod.net_range(start, end)
        if ip_address in net_range:
            return True
        return False

    @staticmethod
    def ip_compare(first, second):
        start = ipaddress.ip_address(first)
        end = ipaddress.ip_address(second)
        if start < end:
            return True
        return False

    @staticmethod
    def mask_to_prefix(mask):
        mask_dict = {
            '255.255.255.255': '32',
            '255.255.255.254': '31',
            '255.255.255.252': '30',
            '255.255.255.248': '29',
            '255.255.255.240': '28',
            '255.255.255.224': '27',
            '255.255.255.192': '26',
            '255.255.255.128': '25',
            '255.255.255.0': '24',
            '255.255.254.0': '23',
            '255.255.252.0': '22',
            '255.255.248.0': '21',
            '255.255.240.0': '20',
            '255.255.224.0': '19',
            '255.255.192.0': '18',
            '255.255.128.0': '17',
            '255.255.0.0': '16',
            '255.254.0.0': '15',
            '255.252.0.0': '14',
            '255.248.0.0': '13',
            '255.240.0.0': '12',
            '255.224.0.0': '11',
            '255.192.0.0': '10',
            '255.128.0.0': '9',
            '255.0.0.0': '8',
            '254.0.0.0': '7',
            '252.0.0.0': '6',
            '248.0.0.0': '5',
            '240.0.0.0': '4',
            '224.0.0.0': '3',
            '192.0.0.0': '2',
            '128.0.0.0': '1',
            '0.0.0.0': '0'
        }
        return mask_dict.get(mask) if mask_dict.get(mask) else mask
    @staticmethod
    def wild_to_prefix(wild):
        wild_dict = {
            '0.0.0.0': '32',
            '0.0.0.1': '31',
            '0.0.0.3': '30',
            '0.0.0.7': '29',
            '0.0.0.15': '28',
            '0.0.0.31': '27',
            '0.0.0.63': '26',
            '0.0.0.127': '25',
            '0.0.0.255': '24',
            '0.0.1.255': '23',
            '0.0.3.255': '22',
            '0.0.7.255': '21',
            '0.0.15.255': '20',
            '0.0.31.255': '19',
            '0.0.63.255': '18',
            '0.0.127.255': '17',
            '0.0.255.255': '16',
            '0.1.255.255': '15',
            '0.3.255.255': '14',
            '0.7.255.255': '13',
            '0.15.255.255': '12',
            '0.31.255.255': '11',
            '0.63.255.255': '10',
            '0.127.255.255': '9',
            '0.255.255.255': '8',
            '1.255.255.255': '7',
            '3.255.255.255': '6',
            '7.255.255.255': '5',
            '15.255.255.255': '4',
            '31.255.255.255': '3',
            '63.255.255.255': '2',
            '127.255.255.255': '1',
            '255.255.255.255': '0',
        }
        return wild_dict.get(wild) if wild_dict.get(wild) else wild
