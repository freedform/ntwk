from modules import mail_module
import subprocess


def ansible(task, device="zzz_network_devices"):
    ans_play_bin = "/usr/bin/ansible-playbook"
    playbook = "/etc/ansible/playbooks/ntwk"
    inventory_file = "/etc/ansible/inventory/tmp_main_inv"
    extra_vars = {
        "task": task,
        "device": device
    }
    failed_hosts = []
    ans_play_args = [ans_play_bin, "-i", inventory_file, playbook, "-e", f"{extra_vars}"]
    ans_play = subprocess.Popen(ans_play_args, stdout=subprocess.PIPE, universal_newlines=True)
    while True:
        line = ans_play.stdout.readline()
        if not line:
            break
        elif "failed=1" in line:
            fh = line.split(":", 1)[0].strip()
            failed_hosts.append(fh)
    if failed_hosts:
        for_mail = "\n".join(failed_hosts)
        mail_subject = 'Failed hosts after backup'
        mail_module.mail_fn(for_mail, mail_subject)
    else:
        mail_subject = 'Everybody are alive'
        mail_message = 'No failed hosts'
        mail_module.mail_fn(mail_message, mail_subject)
