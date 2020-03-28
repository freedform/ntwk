import argparse
from modules import menu, inventory, collect_facts, git_module, ports_parser, ansible_m

repo_dir = r'C:\Users\isimashev\PycharmProjects\network_config\backups'
summary_dir = r'C:\Users\isimashev\PycharmProjects\network_config\summary'
backup_dir = r'C:\Users\isimashev\PycharmProjects\network_config\configs'
inventory_file = r'C:\Users\isimashev\PycharmProjects\network_config\inventory_main'

if __name__ == '__main__':
    input_parser = argparse.ArgumentParser()
    input_parser.add_argument('-a', '--add',
                              action='store_const',
                              const=True)
    input_parser.add_argument('-i', '--inventory',
                              action='store_const',
                              const=True)
    input_parser.add_argument('-c', '--collect',
                              action='store',
                              nargs='+',
                              choices=["inventory", "version", "neighbor"])
    input_parser.add_argument('-d', '--device',
                              action='store',
                              nargs='+')
    input_parser.add_argument('-g', '--git',
                              action='store_const',
                              const=True)
    input_parser.add_argument('-p', '--pull',
                              nargs='+',
                              choices=["interface", "ospf", "static_route"])
    input_parser.add_argument('-b', '--backup',
                              action='store',
                              choices=["inventory", "version", "neighbor", "config"])
    output_parser = input_parser.parse_args()
    out = vars(output_parser)

    if output_parser.add:
        menu.interact_menu()
    elif output_parser.inventory:
        inventory.inventory_gen(inventory_file)
    # +++++COLLECT DATA FOR ALL DEVICES+++++
    elif out.get("collect") and not out.get("device"):
        collect_facts.collect(
            summary_dir,
            out.get("collect")
        )
    # +++++COLLECT DATA FOR SPECIFIC DEVICES+++++
    elif out.get("collect") and out.get("device"):
        collect_facts.collect(
            summary_dir,
            out.get("collect"),
            out.get("device")
        )
    # +++++COLLECT DATA FROM ALL DEVICES+++++
    elif out.get("backup") and not out.get("device"):
        ansible_m.ansible(out.get("backup"))
    # +++++COLLECT DATA FROM SPECIFIC DEVICES+++++
    elif out.get("backup") and out.get("device"):
        ansible_m.ansible(out.get("backup"), out.get("device"))

    elif output_parser.git:
        git_module.git(repo_dir)

    elif out["pull"] and not out.get("device"):
        ports_parser.ports(backup_dir, out["pull"])

    elif out["pull"] and out.get("device"):
        ports_parser.ports(backup_dir, out["pull"], out.get("device"))

    else:
        print('not')
