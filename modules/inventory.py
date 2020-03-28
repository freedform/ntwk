from classes.pgsql_class import DatabaseClass


def inventory_gen(inventory_file):
    db = DatabaseClass()
    location_query = """
SELECT 
    location_id,
    location_name 
FROM 
    \"tbl_LOCATIONS\";
"""
    location_list = db.select(location_query)
    network_group = ['[zzz_network_devices:children]']
    with open(inventory_file, 'w') as inv_file:
        for location in location_list:
            location_id, location_name = location
            if location_name not in network_group:
                network_group.append(location_name)
            inventory_query = f"""
SELECT 
    dev_name,
    oper_system_id
FROM 
    \"tbl_INVENTORY\"
WHERE 
    location_id = '{location_id}'
"""
            inv_file.write(f"[{location_name}]\n")
            inventory_list = db.select(inventory_query)
            for item in inventory_list:
                dev_name, oper_sys_id = item
                if oper_sys_id == 1:
                    inv_file.write(f"{dev_name}\n")
                else:
                    oper_sys_query = f"""
SELECT 
    oper_system_name
FROM 
    \"tbl_OPER_SYSTEMS\" 
WHERE 
    oper_system_id = {oper_sys_id}
"""
                    oper_sys_name = db.select(oper_sys_query)[0][0]
                    inv_file.write(f"{dev_name} ansible_network_os={oper_sys_name}\n")
        inv_file.write('\n'.join(network_group))
    db.connect_close()
