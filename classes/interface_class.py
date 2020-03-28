import re
import copy
import json
from classes.ip_net_class import AddressMod


class MainClass:
    def __init__(self, file_name):
        with open(file_name) as file_n:
            self.file_data = file_n.readlines()

        self.summary = {}

        self.route_summary = []
        self.route_data = {
            'vrf': None,
            'network': None,
            'next_hop': None,
        }

        self.iface_dict = {}
        self.interface_summary = {}
        self.interface_data = {
            'description': None,
            'access_vlan': None,
            'voice_vlan': None,
            'allowed_vlans': [],
            'stp_edge': None,
            'stp_guard': None,
            'arp_trust': None,
            'arp_limit': None,
            'dhcp_trust': None,
            'dhcp_limit': None,
            'trunk_mode': None,
            'dot1q': None,
            'ip': None,
            'ip_second': None,
            'vrf': None,
            'helper': None,
            'fhrp': None,
            'vip_address': None,
            'fhrp_priority': None,
            'fhrp_preempt': None,
            'acl_in': None,
            'acl_out': None,
            'ospf_network': None,
            # 'ospf_auth': None,
            'channel_group': None,
            'channel_mode': None,
            'shutdown': None
        }

        self.ospf_dict = {}
        self.ospf_summary = {}
        self.ospf_data = {
            'vrf': None,
            'router_id': None,
            'auth_area': [],
            'stubs': [],
            'passive_interfaces': [],
            'networks': [],
            'redistribute': [],
            'summary': []
        }

    def return_fn(self):

        if self.interface_summary:
            self.summary['interface_summary'] = self.interface_summary
        if self.ospf_summary:
            self.summary['ospf_summary'] = self.ospf_summary
        if self.route_summary:
            self.summary['static_routes'] = self.route_summary

        if self.summary:
            return self.summary
        else:
            return None


class CISCO(MainClass):
    def __init__(self, file_name):
        super(CISCO, self).__init__(file_name)

    def __cisco_iface_parser(self, data):
        status = 'pass'
        cur_iface = None
        for line in data:
            if line.startswith("interface"):
                cur_iface, status = line.split()[-1], "iface"
                self.iface_dict[cur_iface] = []
                self.interface_summary[cur_iface] = copy.deepcopy(self.interface_data)
                continue
            elif "!" in line:
                cur_iface, status = None, "pass"
            else:
                pass

            if status == "iface" and cur_iface is not None:
                self.iface_dict[cur_iface].append(line.strip())
            else:
                pass

    def __cisco_ospf_parser(self, data):
        status = "pass"
        cur_ospf = None
        for line in data:
            if line.startswith("router ospf"):
                cur_ospf, status = line.strip(), "ospf"
                self.ospf_dict[cur_ospf] = []
                continue
            elif "!" in line:
                cur_ospf, status = None, "pass"
            else:
                pass
            if status == "ospf" and cur_ospf is not None:
                self.ospf_dict[cur_ospf].append(line.strip())
            else:
                pass

    def __cisco_range_vlans(self, vlans):
        result = []
        for vlan in vlans.split(","):
            if "-" in vlan:
                start, end = vlan.split("-")
                result += [x for x in range(int(start), int(end) + 1)]
            else:
                result.append(int(vlan))
        return result

    def interface_fn(self):

        self.__cisco_iface_parser(self.file_data)

        for port, configs in self.iface_dict.items():
            interface = self.interface_summary[port]
            for config in configs:
                description_re = re.match(r"description\s(.+)", config)
                access_vlan_re = re.match(r"switchport\saccess\svlan\s(\d{1,4})", config)
                voice_vlan_re = re.match(r"switchport\svoice\svlan\s(\d{1,4})", config)
                allowed_vlans_re = re.match(r"switchport\strunk\sallowed\svlan\s(add\s)*([0-9,-]+)", config)
                stp_edge_re = re.match(r"spanning-tree\sportfast\s(edge|network|)", config)
                stp_guard_re = re.match(r"spanning-tree\s(bpduguard|bpdufilter)\s(enable|disable)", config)
                arp_trust_re = re.match(r"ip\sarp\sinspection\s(trust|limit\srate\s(\d+))", config)
                dhcp_trust_re = re.match(r"ip\sdhcp\ssnooping\s(trust|limit\srate\s(\d+))", config)
                trunk_mode_re = re.match(r"switchport\strunk\sencapsulation\sdot1q", config)
                dot1q_re = re.match(r"encapsulation\sdot1Q\s(\d+)", config)
                ip_re = re.match(r"ip\saddress\s(\d{1,4}\s)*([0-9.]{7,15})(\/|\s)([0-9.]{1,15})", config)
                vrf_re = re.match(r"(ip\s|)vrf\s(forwarding\s|)([a-zA-Z0-9\-_]+)", config)
                fhrp_re = re.match(r"(ip\s)*(standby|glbp|vrrp)\s(\d+|address)\s(ip|\d{1,4})\s([0-9.]{7,15})", config)
                fhrp_priority_re = re.match(r"(standby|glbp)\s\d+\spriority\s(\d+)", config)
                fhtp_preempt_re = re.match(r"(standby|glbp)\s\d+\spreempt", config)
                helper_re = re.match(r"ip\shelper-address\s[0-9.]{7,15}", config)
                acl_re = re.match(r"ip\saccess-group\s([a-zA-Z0-9\-_]+)\s(in|out)", config)
                ospf_network_re = re.match(
                    r"ip\sospf\snetwork\s(broadcast|non-broadcast|point-to-multipoint|point-to-point)", config)
                channel_re = re.match(r"channel-group\s(\d+)(\smode)*\s*(active|auto|desirable|on|passive|)", config)
                shutdown_re = re.match(r"^shutdown$", config)

                if description_re:
                    description = description_re.group(1)
                    interface['description'] = description
                elif access_vlan_re:
                    access_vlan = int(access_vlan_re.group(1))
                    interface['access_vlan'] = access_vlan
                elif voice_vlan_re:
                    voice_vlan = int(voice_vlan_re.group(1))
                    interface['voice_vlan'] = voice_vlan
                elif allowed_vlans_re:
                    allowed_vlans = self.__cisco_range_vlans(allowed_vlans_re.group(2))
                    interface['allowed_vlans'] += allowed_vlans
                elif stp_edge_re:
                    interface['stp_edge'] = 1
                elif stp_guard_re:
                    interface['stp_guard'] = 1
                elif arp_trust_re:
                    arp_trust, arp_limit = arp_trust_re.group(1), arp_trust_re.group(2)
                    if arp_trust == 'trust':
                        interface['arp_trust'] = 1
                    elif arp_limit:
                        interface['arp_limit'] = int(arp_limit)
                elif dhcp_trust_re:
                    dhcp_trust, dhcp_limit = dhcp_trust_re.group(1), dhcp_trust_re.group(2)
                    if dhcp_trust == 'trust':
                        interface['dhcp_trust'] = 1
                    elif dhcp_limit:
                        interface['dhcp_limit'] = int(dhcp_limit)
                elif trunk_mode_re:
                    interface['trunk_mode'] = 1
                elif dot1q_re:
                    dot1q = int(dot1q_re.group(1))
                    interface['dot1q'] = dot1q
                elif ip_re:
                    ip, mask = ip_re.group(2), ip_re.group(4)
                    mask = AddressMod.mask_to_prefix(mask)
                    ip_address = '/'.join([ip, mask])
                    if not interface['ip']:
                        interface['ip'] = ip_address
                    else:
                        interface['ip_second'] = ip_address
                elif vrf_re:
                    vrf = vrf_re.group(3)
                    interface['vrf'] = vrf
                elif fhrp_re:
                    fhrp, vip_address = fhrp_re.group(2), fhrp_re.group(5)
                    interface['fhrp'] = fhrp
                    interface['vip_address'] = vip_address
                elif fhrp_priority_re:
                    fhrp_priority = int(fhrp_priority_re.group(2))
                    interface['fhrp_priority'] = fhrp_priority
                elif fhtp_preempt_re:
                    interface['fhrp_preempt'] = 1
                elif helper_re:
                    interface['helper'] = 1
                elif acl_re:
                    acl_name, acl_dir = acl_re.group(1), acl_re.group(2)
                    interface['acl_' + acl_dir] = acl_name
                elif ospf_network_re:
                    ospf_network = ospf_network_re.group(1)
                    interface['ospf_network'] = ospf_network
                elif channel_re:
                    channel_group, channel_mode = channel_re.group(1), channel_re.group(3)
                    if not channel_mode:
                        channel_mode = 'on'
                    interface['channel_group'] = int(channel_group)
                    interface['channel_mode'] = channel_mode
                elif shutdown_re:
                    interface['shutdown'] = 1
                else:
                    pass

    def ospf_fn(self):

        self.__cisco_ospf_parser(self.file_data)
        if self.ospf_dict:
            for ospf, configs in self.ospf_dict.items():
                route_ospf_re = re.match(r"router\sospf\s(\d+)(\svrf\s([\w\-]+))*", ospf)
                process, vrf = route_ospf_re.group(1), route_ospf_re.group(3)
                router_ospf = self.ospf_summary[process] = copy.deepcopy(self.ospf_data)

                if vrf:
                    router_ospf['vrf'] = vrf
                for config in configs:
                    router_id_re = re.match(r"router-id\s([\d.]{7,15})", config)
                    auth_area_re = re.match(r"area\s(\d+)\sauthentication\smessage-digest", config)
                    stub_re = re.match(r"area\s(\d+)\s(stub|nssa)\s*((no-summary|no-redistribution)\s(no-summary|))*",
                                       config)
                    passive_interface_re = re.match(r"passive-interface\s([\w\d\-]+)", config)
                    network_re = re.match(r"network\s([\d.]{7,15})\s([\d.]{7,15})\sarea\s(\d+)", config)
                    redistribute_re = re.match(r"redistribute\s(connected|static)\s*(subnets)*\s*(route-map\s([\w]+))*",
                                               config)
                    summary_re = re.match(r"area\s(\d+)\srange\s([\d.]{7,15})\s([\d.]{7,15})", config)

                    if router_id_re:
                        router_id = router_id_re.group(1)
                        router_ospf['router_id'] = router_id
                    elif auth_area_re:
                        auth_area = auth_area_re.group(1)
                        router_ospf['auth_area'].append(int(auth_area))
                    elif stub_re:
                        stub_dict = {'area': '', 'mode': '', 'params': []}
                        stub_dict['area'] = stub_re.group(1)
                        stub_dict['mode'] = stub_re.group(2)
                        if stub_re.group(4):
                            stub_dict['params'].append(stub_re.group(4))
                        if stub_re.group(5):
                            stub_dict['params'].append(stub_re.group(5))
                        router_ospf['stubs'].append(json.dumps(stub_dict))
                    elif passive_interface_re:
                        passive_interface = passive_interface_re.group(1)
                        router_ospf['passive_interfaces'].append(passive_interface)
                    elif network_re:
                        network_dict = {'network': '', 'mask': '', 'area': ''}
                        network_dict['network'] = network_re.group(1)
                        network_dict['mask'] = network_re.group(2)
                        network_dict['area'] = network_re.group(3)
                        router_ospf['networks'].append(json.dumps(network_dict))
                    elif redistribute_re:
                        redistribute_dict = {'source': '', 'subnets': '', 'route-map': ''}
                        source, subnets = redistribute_re.group(1), redistribute_re.group(2)
                        route_map = redistribute_re.group(4)
                        redistribute_dict['source'] = source
                        if subnets:
                            redistribute_dict['subnets'] = 1
                        if route_map:
                            redistribute_dict['route-map'] = route_map
                        router_ospf['redistribute'].append(json.dumps(redistribute_dict))
                    elif summary_re:
                        summary_dict = {'area': '', 'network': '', 'mask': ''}
                        summary_dict['area'] = summary_re.group(1)
                        summary_dict['network'] = summary_re.group(2)
                        summary_dict['mask'] = summary_re.group(3)
                        router_ospf['summary'].append(json.dumps(summary_dict))
                    else:
                        pass
        else:
            pass

    def static_route_fn(self):
        route_re = r"(ip\s|)route\s((vrf\s([\w\-_]+)\s)|[\w\d_\-]+\s|)([0-9.]{7,15})\s([0-9.]{7,15})\s([0-9.]{7,15})"
        route_list = list(filter(lambda x: re.match(route_re, x), self.file_data))
        if route_list:
            for raw_route in route_list:
                route = re.match(route_re, raw_route)
                _, _, _, vrf, network, mask, gw = route.groups()
                mask = AddressMod.mask_to_prefix(mask)
                self.route_data['vrf'] = vrf
                self.route_data['network'] = '/'.join([network, mask])
                self.route_data['next_hop'] = gw
                self.route_summary.append(self.route_data)
                self.route_data = dict.fromkeys(self.route_data, "")


class EXTREME(MainClass):
    def __init__(self, file_name):
        super(EXTREME, self).__init__(file_name)

    def __extreme_iface_parser(self, data):
        status = 'pass'
        cur_iface = None
        for line in data:
            if line.startswith("interface"):
                cur_iface, status = ''.join(line.split()[-2:]), "iface"
                if cur_iface not in self.iface_dict.keys():
                    self.iface_dict[cur_iface] = []
                    self.interface_summary[cur_iface] = copy.deepcopy(self.interface_data)
                continue
            elif re.match(r"vlan\smembers\s\d{1,4}", line):
                line = line.split(" ")
                vlan = ''.join(line[0:3:2]).title()
                ifaces = line[3]
                if vlan not in self.iface_dict.keys():
                    self.iface_dict[vlan] = [ifaces]
                else:
                    self.iface_dict[vlan].append(ifaces)
                self.interface_summary[vlan] = copy.deepcopy(self.interface_data)
            elif "exit" in line:
                cur_iface, status = None, "pass"
            else:
                pass

            if status == "iface" and cur_iface is not None and line.strip():
                self.iface_dict[cur_iface].append(line.strip())
            else:
                pass

    def __extreme_port_format(self, data):
        data = data.split(",")
        result = []
        for dt in data:
            scope_re = re.match(r"(\d{1,3}\/)(\d{1,3})-\d{1,3}\/(\d{1,3})", dt)
            if scope_re:
                prefix, start, end = scope_re.group(1), scope_re.group(2), scope_re.group(3)
                dt_repl = [prefix + str(x) for x in range(int(start), int(end) + 1)]
                result += dt_repl
            else:
                result.append(dt)
        return result

    def interface_fn(self):
        self.__extreme_iface_parser(self.file_data)
        trk_list = [x for x in self.iface_dict.keys() if "encapsulation dot1q" in self.iface_dict[x]]

        for port, configs in self.iface_dict.items():
            interface = self.interface_summary[port]
            for config in configs:
                description_re = re.match(r"name\s\"([\d\w\-]+)\"", config)
                vlan_ports_re = re.match(r"^(\d+\/\d+(,|-|))*$", config)
                vrf_re = re.match(r"vrf\s([\d\w\-]+)", config)
                ip_re = re.match(r"ip\saddress\s(\d+\s)*([\d.]{7,15})(\/|\s)([\d.]{7,15})", config)
                fhrp_re = re.match(r"ip\s(vrrp)\saddress\s\d+\s([\d.]{7,15})", config)
                rsmlt_re = re.match(r"ip\srsmlt", config)
                channel_re = re.match(r"lacp\skey\s(\d+)\saggregation", config)

                if description_re:
                    description = description_re.group(1)
                    interface['description'] = description
                elif channel_re:
                    channel_group = int(channel_re.group(1))
                    interface['channel_group'] = channel_group
                    interface['channel_mode'] = 'active'
                elif vlan_ports_re:
                    format_ports = self.__extreme_port_format(vlan_ports_re.group(0))
                    vlan_id = int(port.replace("Vlan", ""))
                    for item in format_ports:
                        item = "GigabitEthernet" + item
                        if item in trk_list:
                            self.interface_summary[item]['allowed_vlans'].append(vlan_id)
                        else:
                            self.interface_summary[item]['access_vlan'] = vlan_id
                elif vrf_re:
                    vrf = vrf_re.group(1)
                    interface['vrf'] = vrf
                elif ip_re:
                    ip, mask = ip_re.group(2), ip_re.group(4)
                    mask = AddressMod.mask_to_prefix(mask)
                    ip_address = '/'.join([ip, mask])
                    interface['ip'] = ip_address
                elif fhrp_re:
                    fhrp, vip_address = fhrp_re.group(1), fhrp_re.group(2)
                    interface['fhrp'] = fhrp
                    interface['vip_address'] = vip_address
                elif rsmlt_re:
                    interface['fhrp'] = "rsmtl"
                else:
                    pass

    def ospf_fn(self):
        pass

    def static_route_fn(self):
        vrf = None
        for line in self.file_data:
            if line.startswith("router vrf"):
                vrf = line.split()[-1]
            elif line.startswith("ip route"):
                route_data = re.match(r"(ip\s|)route\s([\d.]{7,15})\s([\d.]{7,15})\s([\d.]{7,15})", line)
                mask = AddressMod.mask_to_prefix(route_data.group(3))
                network = '/'.join([route_data.group(2), mask])
                self.route_data['vrf'] = vrf
                self.route_data['network'] = network
                self.route_data['next_hop'] = route_data.group(4)
                self.route_summary.append(self.route_data)
                self.route_data = dict.fromkeys(self.route_data, "")
            elif "exit" in line:
                vrf = None
            else:
                pass


class DELL(MainClass):
    def __init__(self, file_name):
        super(DELL, self).__init__(file_name)

    def __dell_iface_parser(self, data):
        status = 'pass'
        cur_iface = None
        for line in data:
            if line.startswith("interface"):
                cur_iface, status = ''.join(line.split()[-2:]), "iface"
                self.iface_dict[cur_iface] = []
                self.interface_summary[cur_iface] = copy.deepcopy(self.interface_data)
                continue
            elif "!" in line and line.count(" ") == 2:
                continue
            elif "!" in line and line.count(" ") == 0:
                cur_iface, status = None, "pass"
            else:
                pass
            if status == "iface" and cur_iface:
                self.iface_dict[cur_iface].append(line.strip())
            else:
                pass

    def __dell_port_format(self, data):
        index = ''
        result = []
        if "/" in data:
            index = data.split("/")[0] + "/"
        for dt in data.split(","):
            scope_re = re.search(r"(\d{1,3})-(\d{1,3})", dt)
            if scope_re:
                start, end = scope_re.group(1), scope_re.group(2)
                result += [index + str(x) for x in range(int(start), int(end) + 1)]
            else:
                result.append(index + dt)

        return result

    def interface_fn(self):
        self.__dell_iface_parser(self.file_data)

        for port, configs in self.iface_dict.items():
            interface = self.interface_summary[port]
            for config in configs:
                description_re = re.match(r"description\s(.+)", config)
                vlan_ports_re = re.match(r"(untagged|tagged)\s([\w\-]+)\s([\d\/\-,]+)", config)
                ip_re = re.match(r"ip\saddress\s([\d.]+\/\d{1,2})", config)
                channel_re = re.match(r"port-channel\s(\d+)\smode\s([\w]+)", config)
                shutdown_re = re.match(r"^shutdown$", config)

                if description_re:
                    description = description_re.group(1)
                    interface['description'] = description
                elif vlan_ports_re:
                    port_type, port_prefix, port_item = vlan_ports_re.groups()
                    format_ports = list(map(lambda x: port_prefix + x, self.__dell_port_format(port_item)))
                    vlan_id = int(port.replace("Vlan", ""))
                    if port_type == "tagged":
                        for item in format_ports:
                            self.interface_summary[item]['allowed_vlans'].append(vlan_id)
                    else:
                        for item in format_ports:
                            self.interface_summary[item]['access_vlan'] = vlan_id
                elif channel_re:
                    channel_group, channel_mode = channel_re.group(1), channel_re.group(2)
                    interface['channel_group'] = int(channel_group)
                    interface['channel_mode'] = channel_mode
                elif ip_re:
                    ip_address = ip_re.group(1)
                    interface['ip'] = ip_address
                elif shutdown_re:
                    interface['shutdown'] = 1

                else:
                    pass

        # for x, y in self.interface_summary.items():
        #     print(f"{x} access_port = {y['access_vlan']} trunk_ports {y['allowed_vlans']}")

    def ospf_fn(self):
        pass

    def static_route_fn(self):
        route_list = list(filter(lambda x: re.match(".*route.*", x), self.file_data))
        for route in route_list:
            route_data = re.match(r".*\sroute\s([\d.]{7,15})\/(\d{1,2})\s([\d.]{7,15})", route)
            self.route_data['vrf'] = None
            self.route_data['network'] = route_data.group(1)
            # self.route_data['mask'] = route_data.group(2)
            self.route_data['next_hop'] = route_data.group(3)
            self.route_summary.append(self.route_data)
            self.route_data = dict.fromkeys(self.route_data, "")
