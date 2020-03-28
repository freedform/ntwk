class GeatherFacts:
    def __init__(self, file_name):
        self.__version_dict = {
            'model': "",
            'soft_image': "",
            'soft_version': "",
        }

        self.__inventory_dict = {
            'name': "",
            'description': "",
            'pid': "",
            'vid': "",
            'sn': ""
        }
        self.__inventory_list = []

        self.__neighbor_dict = {
            "neighbor_name": "",
            "local_interface": "",
            "remote_interface": ""
        }
        self.__neighbor_list = []

        with open(file_name) as fn:
            self.parse_data = fn.readlines()

    # -------------------NEIGHBOR-----------------
    def asa_neighbor(self):
        print("ASA don't have and cdp or lldp neighbors")
        pass

    def ios_neighbor(self):
        dev_name = None
        for line in self.parse_data:
            # "Device ID: kar-of-sw1.net.ums.uz"
            if line.startswith("Device ID:") and "SEP" not in line:
                dev_name = line.split(":")[-1].strip()
                self.__neighbor_dict["neighbor_name"] = dev_name
                # print(dev_name)
            # "Interface: GigabitEthernet2/0/19,  Port ID (outgoing port): FastEthernet0/24"
            elif line.startswith("Interface:") and dev_name:
                raw_local, raw_remote = line.split(",", 1)
                local_iface = raw_local.split(":", 1)[-1].strip()
                remote_iface = raw_remote.split(":", 1)[-1].strip()
                self.__neighbor_dict["neighbor_name"] = dev_name
                self.__neighbor_dict["local_interface"] = local_iface
                self.__neighbor_dict["remote_interface"] = remote_iface
                self.__neighbor_list.append(self.__neighbor_dict)
                self.__neighbor_dict = self.__neighbor_dict.fromkeys(self.__neighbor_dict, "")
                dev_name = None
            elif not line.strip() or "----------" in line:
                dev_name = None

    def voss_neighbor(self):
        local_port = None
        for line in self.parse_data:
            # "Port: 1/1       Index    : 35   "
            if line.startswith("Port:"):
                local_port = line.split()[1]
            # "SysName  : "
            elif "SysName  :" in line and local_port:
                dev_name = line.split(":")[-1].strip()
                self.__neighbor_dict["neighbor_name"] = dev_name if dev_name else "null"
                self.__neighbor_dict["local_interface"] = local_port
                self.__neighbor_dict["remote_interface"] = "null"
                self.__neighbor_list.append(self.__neighbor_dict)
                self.__neighbor_dict = self.__neighbor_dict.fromkeys(self.__neighbor_dict, "")
                local_port = None
            elif not line.strip():
                local_port = None

        pass

    def dellos9_neighbor(self):
        local_port = None
        remote_port = None
        for line in self.parse_data:
            # "Remote Port ID:  1/18"
            if "Remote Port ID:" in line:
                remote_port = line.split(":", 1)[-1].strip()
            # "Local Port ID: TenGigabitEthernet 1/44"
            elif "Local Port ID:" in line:
                local_port = line.split(":", 1)[-1].strip()
                # print(local_port)
            # "Remote System Name:  s4-bill-core-sw2"
            elif "Remote System Name:" in line and local_port and remote_port:
                dev_name = line.split(":", 1)[-1].strip()
                self.__neighbor_dict["neighbor_name"] = dev_name
                self.__neighbor_dict["local_interface"] = local_port
                self.__neighbor_dict["remote_interface"] = remote_port
                self.__neighbor_list.append(self.__neighbor_dict)
                self.__neighbor_dict = self.__neighbor_dict.fromkeys(self.__neighbor_dict, "")
                local_port = None
                remote_port = None
            elif "====================" in line:
                local_port = None
                remote_port = None

    def return_neighbor(self):
        if self.__neighbor_list:
            return self.__neighbor_list
        return None

    # ---------------------------------------------

    # -------------------INVENTORY-----------------
    def asa_inventory(self):
        for line in self.parse_data:
            # "Name: "Chassis", DESCR: "ASA 5540 Adaptive Security Appliance""
            if "Name:" in line and "DESCR:" in line:
                raw_name, raw_descr = line.split(",", 1)
                name = raw_name.split(":")[-1].strip(' "\n')
                descr = raw_descr.split(":")[-1].strip(' "\n')
                self.__inventory_dict['name'] = name
                self.__inventory_dict['description'] = descr
            # "PID: SSM-4GE           , VID: V02     , SN: JAF1448CCSF"
            elif "PID:" in line and "VID:" in line and "SN:" in line:
                raw_pid, raw_vid, raw_sn = line.split(",", 2)
                pid = raw_pid.split(":")[-1].strip()
                vid = raw_vid.split(":")[-1].strip()
                sn = raw_sn.split(":")[-1].strip()
                if self.__inventory_dict['name'] and self.__inventory_dict['description']:
                    self.__inventory_dict['pid'] = pid if pid else "null"
                    self.__inventory_dict['vid'] = vid if vid else "null"
                    self.__inventory_dict['sn'] = sn if sn else "null"
                    self.__inventory_list.append(self.__inventory_dict)
                    self.__inventory_dict = self.__inventory_dict.fromkeys(self.__inventory_dict, "")
                else:
                    print(f"Detect orphant pid: {pid}, vid: {vid}, sn: {sn}")

    def ios_inventory(self):
        for line in self.parse_data:
            # "NAME: "foris-ivr-2950-1", DESCR: "Cisco Catalyst c2950 switch""
            if "NAME:" in line and "DESCR:" in line:
                raw_name, raw_descr = line.split(",", 1)
                name = raw_name.split(":")[-1].strip(' "\n')
                descr = raw_descr.split(":")[-1].strip(' "\n')
                self.__inventory_dict['name'] = name
                self.__inventory_dict['description'] = descr
            elif "PID:" in line and "VID:" in line and "SN:" in line:
                raw_pid, raw_vid, raw_sn = line.split(",", 2)
                pid = raw_pid.split(":")[-1].strip()
                vid = raw_vid.split(":")[-1].strip()
                sn = raw_sn.split(":")[-1].strip()
                if self.__inventory_dict['name'] and self.__inventory_dict['description']:
                    self.__inventory_dict['pid'] = pid if pid else "null"
                    self.__inventory_dict['vid'] = vid if vid else "null"
                    self.__inventory_dict['sn'] = sn if sn else "null"
                    self.__inventory_list.append(self.__inventory_dict)
                    self.__inventory_dict = self.__inventory_dict.fromkeys(self.__inventory_dict, "")
                else:
                    print(f"Detect orphant pid: {pid}, vid: {vid}, sn: {sn}")

    def voss_inventory(self):
        # print("VOSS")
        pass

    def dellos9_inventory(self):
        label = None
        for line in self.parse_data:
            line = line.strip()
            if not line:
                continue
            # "Unit Type Serial Number Part Number  Rev  Piece Part ID Rev  Svc Tag  Exprs Svc Code"
            if "Serial Number" in line and "Part Number" in line:
                label = 1
            elif "-------" in line:
                continue
            elif "Management Unit" in line:
                label = None
            elif label:
                line = line.lstrip("*").split()
                self.__inventory_dict['name'] = line[1]
                self.__inventory_dict['sn'] = line[2]
                self.__inventory_dict['description'] = line[3]
                self.__inventory_dict['vid'] = line[4]
                self.__inventory_dict['pid'] = "null"
                self.__inventory_list.append(self.__inventory_dict)
                self.__inventory_dict = self.__inventory_dict.fromkeys(self.__inventory_dict, "")

    def return_inventory(self):
        if self.__inventory_list:
            return self.__inventory_list
        return None

    # ---------------------------------------------

    # -------------------VERSION-------------------
    def asa_version(self):
        for line in self.parse_data:
            # "Cisco Adaptive Security Appliance Software Version 9.1(7)16 "
            if line.startswith("Cisco Adaptive Security Appliance Software Version"):
                soft_version = line.split()[-1]
                self.__version_dict['soft_version'] = soft_version
            # "System image file is "disk0:/asa917-16-k8.bin""
            elif line.startswith("System image file is"):
                soft_image = line.split()[-1].strip('"')
                self.__version_dict['soft_image'] = soft_image
            # "Hardware:   ASA5540, 2048 MB RAM, CPU Pentium 4 2000 MHz,"
            elif line.startswith("Hardware:"):
                model = line.split(":")[-1].split(",")[0].strip()
                self.__version_dict['model'] = model
            else:
                pass

    def ios_version(self):
        for line in self.parse_data:
            # "Cisco IOS Software, C2900 Software (C2900-UNIVERSALK9-M), Version 15.4(3)M9, RELEASE SOFTWARE (fc1)"
            if line.startswith("Cisco IOS Software") or line.startswith("IOS"):
                raw_soft_version = [x.split()[1] for x in line.split(",") if "Version" in x]
                soft_version = raw_soft_version[0] if raw_soft_version else None
                self.__version_dict['soft_version'] = soft_version
            # "System image file is "flash:c2900-universalk9-mz.SPA.154-3.M9.bin""
            elif line.startswith("System image file is"):
                soft_image = line.split()[-1].strip('"')
                self.__version_dict['soft_image'] = soft_image
            # "cisco WS-C2950T-24 (RC32300) processor (revision R0) with 19912K bytes of memory."
            elif line.startswith("cisco"):
                model = line.split()[1]
                self.__version_dict['model'] = model
            # "7600 Cisco CISCO7606-S (M8500) processor (revision 1.1) with 917504K/65536K bytes of memory."
            elif line.startswith("Cisco") and "processor" in line:
                model = line.split()[1]
                self.__version_dict['model'] = model
            # "Cisco CISCO2921/K9 (revision 1.0) with 479232K/45056K bytes of memory."
            elif line.startswith("Cisco") and "memory" in line:
                model = line.split()[1]
                self.__version_dict['model'] = model
            else:
                pass

    def voss_version(self):
        for line in self.parse_data:
            # "SysDescr     : VSP-7254XSQ (7.1.0.1)"
            if "SysDescr" in line:
                soft_version = line.split()[-1].strip("()")
                self.__version_dict['soft_version'] = soft_version
                self.__version_dict['soft_image'] = soft_version
            # "ModelName          : 7254XSQ"
            elif "ModelName" in line:
                model = line.split(":")[-1].strip()
                self.__version_dict['model'] = model
            else:
                pass

    def dellos9_version(self):
        for line in self.parse_data:
            # "Dell Application Software Version:  9.13(0.1)"
            if line.startswith("Dell Application Software Version:"):
                soft_version = line.split(":")[-1].strip()
                self.__version_dict['soft_version'] = soft_version
            # "System image file is "system://A""
            elif line.startswith("System image file is"):
                soft_image = line.split()[-1].strip('"')
                self.__version_dict['soft_image'] = soft_image
            # "System Type: MXL-10/40GbE "
            elif line.startswith("System Type:"):
                model = line.split(":")[-1].strip()
                self.__version_dict['model'] = model
            else:
                pass

    def return_version(self):
        if all(value for value in self.__version_dict.values()):
            return self.__version_dict
        else:
            return None
    # ---------------------------------------------
