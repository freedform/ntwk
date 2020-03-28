from classes.pgsql_class import DatabaseClass


def interact_menu():
    print('WELCOME TO NETWORK_MNG 1.0')
    print('please enter HOSTNAME:')
    # DEFINE HOSTNAME VIA CONSOLE data
    dev_hostname = data()
    if not dev_hostname:
        print('HOSTNAME is empty please, try again')
        return
    else:
        print(f'The HOSTNAME will be ---{dev_hostname}---\n')
    db = DatabaseClass()
    vt = ['vendor', 'type', 'location', 'oper_system']
    dev_vendor = dev_type = dev_location = dev_os =''
    for item in vt:
        print(f'Please select device {item}:')
        list_query = f"""
SELECT 
    * 
FROM 
    \"tbl_{item.upper()}S\";
"""
        list_result = (db.select(list_query))
        if not list_result:
            print('No data for itteration')
            return
        else:
            for d in list_result:
                print(f'[{d[0]}] for {d[1]}')
        user_data = int(data())
        if user_data > len(list_result):
            print(f'{item.upper()} index {user_data} is out of possible range')
            db.connect_close()
            return
        else:
            select_item_query = f"""
SELECT 
    {item}_name 
FROM 
    \"tbl_{item.upper()}S\" 
WHERE 
    {item}_id = {user_data};
"""
            print(f'{item.upper()} will be ---{db.select(select_item_query)[0][0]}---\n')
        if item == 'vendor':
            dev_vendor = user_data
        elif item == 'type':
            dev_type = user_data
        elif item == 'oper_system':
            dev_os = user_data
        else:
            dev_location = user_data
    if dev_vendor and dev_type and dev_location:
        insert_query = f"""
INSERT INTO 
    \"tbl_INVENTORY\" 
    (dev_name, vendor, type, location_id, oper_system_id)
VALUES 
    ('{dev_hostname}','{dev_vendor}','{dev_type}', '{dev_location}', '{dev_os}');
"""
        db.insert(insert_query)
        db.connect_close()
    else:
        db.connect_close()
        print('data DATA IS EMPTY')
        return
