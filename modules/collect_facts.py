import os
from classes.pgsql_class import DatabaseClass
from classes.get_facts_class import GeatherFacts


def collect(summary_dir, col_list, spec_dev=None):
    summary_query = """
SELECT
    t1.dev_id,
    t1.dev_name,
    t2.location_name,
    t3.oper_system_name
FROM 
    \"tbl_INVENTORY\" t1,
    \"tbl_LOCATIONS\" t2,
    \"tbl_OPER_SYSTEMS\" t3
WHERE
    t1.location_id = t2.location_id 
    and 
    t1.oper_system_id = t3.oper_system_id
"""
    if spec_dev:
        spec_query = f"\nand t1.dev_name = ANY(ARRAY{spec_dev})"
        summary_query += spec_query
    db = DatabaseClass()
    device_list = db.select(summary_query)
    db.connect_close()
    if device_list:
        f_columns = [
            "dev_id",
            "dev_name",
            "location_name",
            "oper_system_name"
        ]
        for device in device_list:
            di = dict(zip(f_columns, device))
            print("{:-^100}".format(di['dev_name']))
            for col_type in col_list:
                file_path = os.path.join(summary_dir, di['location_name'], di['dev_name'] + f"_{col_type}")
                if not os.path.isfile(file_path):
                    print(f"No file for <{di['dev_name']}> or col_type <{col_type}> unknown")
                    continue
                gf = GeatherFacts(file_path)
                getattr(gf, di['oper_system_name'] + f"_{col_type}")()
                result = getattr(gf, "return" + f"_{col_type}")()
                if result:
                    print(f'BEGIN <{col_type}> function for {di["dev_id"]}')
                    try:
                        fn_dict[col_type](di["dev_id"], result)
                    except TypeError as error:
                        print(f"Errors for {col_type} with {di['dev_name']}: {error}")
                        continue
                    print(f'FINISH <{col_type}> function for {di["dev_id"]}')
                else:
                    print(f"No {col_type.upper()} data for {di['dev_name']}")
                    continue

    else:
        print(f"No data from Database at all")


def version_fn(dev_id, data):
    if type(data) is not dict:
        raise TypeError(f"Wrong data type, expect dict, but {type(data)} arrived")
    print(f"Processing version data for {dev_id}")
    sql_fields = ",".join(data.keys())
    sql_values = ",".join([f"'{x}'" for x in data.values()])
    sql_query = f"""
UPDATE
    \"tbl_software\"
SET
    ({sql_fields}) = ({sql_values})
WHERE
    dev_id = {dev_id};
"""
    db = DatabaseClass()
    db.update(sql_query)
    db.connect_close()


def inventory_fn(dev_id, data):
    sql_fields, sql_values = field_value(dev_id, data)
    print(f"Processing inventory data for {dev_id}")
    sql_query = f"""
INSERT INTO
    \"tbl_hardware\"
    ({sql_fields})
VALUES
    {sql_values};
"""
    db = DatabaseClass()
    db.raw_query(f"DELETE FROM \"tbl_hardware\" WHERE dev_id = '{dev_id}'")
    db.insert(sql_query)
    db.connect_close()


def neighbor_fn(dev_id, data):
    sql_fields, sql_values = field_value(dev_id, data)
    print(f"Processing neighbor data for {dev_id}")
    sql_query = f"""
INSERT INTO
    \"tbl_neighbors\"
    ({sql_fields})
VALUES
    {sql_values};
"""
    db = DatabaseClass()
    db.raw_query(f"DELETE FROM \"tbl_neighbors\" WHERE dev_id = '{dev_id}'")
    db.insert(sql_query)
    db.connect_close()


def field_value(dev_id, data):
    if type(data) is not list:
        raise TypeError(f"Wrong data type, expect list, but {type(data)} arrived")
    elif not all(isinstance(x, dict) for x in data):
        raise TypeError(f"Not all eliment in inventory list for {dev_id} decvive are dict")
    sql_fields = None
    sql_values = []
    for item in data:
        item["dev_id"] = dev_id
        if not sql_fields:
            sql_fields = ",".join(item.keys())
        raw_sql_values = ",".join([f"'{x}'" if x != "null" else x for x in item.values()])
        sql_values.append(f"({raw_sql_values})")
    if sql_values:
        sql_values = ",".join(sql_values)
    else:
        raise TypeError(f"SQL values are unexpectly empty")
    return sql_fields, sql_values


fn_dict = {
    "version": version_fn,
    "inventory": inventory_fn,
    "neighbor": neighbor_fn
}
