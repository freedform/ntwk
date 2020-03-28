import os.path
from classes.pgsql_class import DatabaseClass


def ports(config_dir, method_list, host=None):
    dev_query = """
SELECT
    t1.dev_id,
    t1.dev_name,
    t2.vendor_name,
    t3.port_types,
    t4.location_name

FROM
    "tbl_INVENTORY" t1, 
    "tbl_VENDORS" t2,
    "tbl_TYPES" t3,
    "tbl_LOCATIONS" t4
WHERE
    t1.vendor_id = t2.vendor_id
    and
    t1.type_id = t3.type_id
    and
    t1.location_id = t4.location_id
    """
    if host:
        where_add = f"\nand t1.dev_name = ANY(ARRAY{host})"
        dev_query += where_add
    db = DatabaseClass()
    port_re_data = db.select(dev_query)
    db.connect_close()
    if port_re_data:
        dev_columns = ['dev_id',
                       'dev_name',
                       'vendor_name',
                       'port_types',
                       'location_name']
        for item in port_re_data:
            dd = dict(zip(dev_columns, item))
            file_path = os.path.join(config_dir, dd.get('location_name'), dd.get('dev_name'))
            print("{:=^100}".format(dd.get('dev_name')))
            if not os.path.isfile(file_path):
                print(f"No file for {dd.get('dev_name')}")
                continue
            try:
                import_class = __import__('classes.interface_class', fromlist=[dd.get('vendor_name')])
                class_ins = getattr(import_class, dd.get('vendor_name'))
                ins = class_ins(file_path)
            except Exception as error:
                print(f"Error in CLASS: {error}")
                continue
            for method in method_list:
                getattr(ins, method + "_fn")()
            result = ins.return_fn()
            if result:
                for res_key, res_val in result.items():
                    func_dict[res_key](res_val, dd.get('dev_id'))
            else:
                print(f"No any data from {host} config")
    else:
        print(f"No data for {host} from Database")


def interface_insert(data, dev_id):
    insert_all = []
    sql_fields = None
    for iface, if_data in data.items():
        if_data['dev_id'], if_data['interface_name'] = dev_id, iface
        add_fields, add_values = list(if_data.keys()), list(if_data.values())
        if not sql_fields:
            sql_fields = ','.join(add_fields)
        raw_values = ','.join(list(map(f_type, add_values)))
        insert_all.append(f"({raw_values})")
    sql_values = ','.join(insert_all)
    insert_query = f"""
INSERT INTO
        \"tbl_interface_summary\"
        ({sql_fields})
VALUES
        {sql_values};"""
    clear_data("tbl_interface_summary", dev_id)
    insert_data(insert_query)


def ospf_insert(data, dev_id):
    insert_all = []
    sql_fields = None
    for proc, ospf_data in data.items():
        ospf_data['dev_id'], ospf_data['process'] = f"{dev_id}", proc
        ospf_data = dict(map(js_type, ospf_data.items()))
        add_fields, add_values = list(ospf_data.keys()), list(ospf_data.values())
        if not sql_fields:
            sql_fields = ','.join(add_fields)
        raw_values = ','.join(add_values)
        insert_all.append(f"({raw_values})")
    sql_values = ','.join(insert_all)
    insert_query = f"""
    INSERT INTO
            \"tbl_ospf_summary\"
            ({sql_fields})
    VALUES
            {sql_values};"""
    clear_data("tbl_ospf_summary", dev_id)
    insert_data(insert_query)


def route_insert(data, dev_id):
    insert_all = []
    sql_fields = None
    for route in data:
        route['dev_id'] = dev_id
        route = dict(map(js_type, route.items()))
        add_fields, add_values = list(route.keys()), list(route.values())
        if not sql_fields:
            sql_fields = ','.join(add_fields)
        raw_values = ','.join(add_values)
        insert_all.append(f"({raw_values})")
    sql_values = ','.join(insert_all)
    insert_query = f"""
        INSERT INTO
                \"tbl_route_summary\"
                ({sql_fields})
        VALUES
                {sql_values};"""
    clear_data("tbl_route_summary", dev_id)
    insert_data(insert_query)


def f_type(data):
    if type(data) == str:
        return f"'{data}'"
    elif type(data) == int:
        return f"'{data}'"
    elif type(data) == list:
        if len(data) == 0:
            return 'null'
        return f"ARRAY{data}"
    elif data is None:
        return 'null'
    else:
        pass


def js_type(data):
    k, v = data
    if k in js_lsit and type(v) == list:
        if len(v) == 0:
            return k, 'null'
        return k, f"ARRAY{v}::jsonb[]"
    elif type(v) == list:
        if len(v) == 0:
            return k, 'null'
        return k, f"ARRAY{v}"
    elif type(v) == int:
        return k, f"{v}"
    elif v is None:
        return k, 'null'
    elif type(v) == str:
        return k, f"'{v}'"
    else:
        pass


def clear_data(table_name, dev_id):
    delete_query = f"""
DELETE FROM
    "{table_name}"
WHERE
    dev_id = '{dev_id}'"""
    db = DatabaseClass()
    db.raw_query(delete_query)
    db.connect_close()


def insert_data(insert_q):
    db = DatabaseClass()
    db.insert(insert_q)
    db.connect_close()


func_dict = {
    'interface_summary': interface_insert,
    'ospf_summary': ospf_insert,
    'static_routes': route_insert
}

fff = {
    "interface": "tbl_interface_summary",
    "ospf": "tbl_ospf_summary",
    "static_route": "tbl_route_summary"
}

js_lsit = ['stubs', 'networks', 'redistribute', 'summary']
