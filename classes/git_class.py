import subprocess, datetime, os, re


class GitClass:
    def __init__(self, repo):
        self.git_exec = r'/usr/bin/git'
        self.git_comment = "UPDATE_CONFIGS:" + datetime.datetime.today().strftime("%Y-%m-%d-%H.%M.%S")
        self.repo = repo
        os.chdir(self.repo)
        self.status_dict = {'untracked_files': [],
                            'added_files': [],
                            'modified_files': [],
                            'deleted_files': [],
                            'unkhown_files': []}

    def status(self):
        status_args = [self.git_exec, "status", "-s"]
        status_exec = subprocess.Popen(status_args, stdout=subprocess.PIPE, universal_newlines=True)
        status_data = status_exec.communicate()
        status_result = status_data[0]
        status_error = status_data[1]
        if status_error:
            print(f"There are some errors after git_status executed: {status_error}")
        status_return = status_result.strip().split('\n')
        for item in status_return:
            try:
                status_type, status_file = item.split()
            except ValueError:
                status_type = status_file = None
            if status_type == '??':
                self.status_dict['untracked_files'].append(status_file)
            elif status_type == 'A':
                self.status_dict['added_files'].append(status_file)
            elif status_type == 'M':
                self.status_dict['modified_files'].append(status_file)
            elif status_type == 'D':
                self.status_dict['deleted_files'].append(status_file)
            else:
                self.status_dict['unkhown_files'].append(status_file)

    def add_file(self, add_file):
        add_args = [self.git_exec, "add", add_file]
        add_exec = subprocess.call(add_args)
        if add_exec != 0:
            print(f"There are some errors after git_add executed")
        else:
            pass

    def rm_file(self, rm_file):
        rm_args = [self.git_exec, "rm", "--cached", rm_file]
        rm_exec = subprocess.call(rm_args)
        if rm_exec != 0:
            print(f"There are some errors after git_rm executed")
        else:
            pass

    def git_log_comment(self, comment):
        git_log_args = [self.git_exec, "log", "--oneline"]
        git_log_exec = subprocess.Popen(git_log_args, stdout=subprocess.PIPE, universal_newlines=True)
        git_log_result, git_log_error = git_log_exec.communicate()
        rev_id = None
        for item in git_log_result.split('\n'):
            try:
                commit_id, commit_comment = item.split()
            except:
                rev_id = None
            if comment == commit_comment:
                rev_id = commit_id
                break
        if rev_id is not None:
            git_show_args = [self.git_exec, "show", "--oneline", rev_id]
            git_show_exec = subprocess.Popen(git_show_args, stdout=subprocess.PIPE, universal_newlines=True)
            git_show_result, git_show_error = git_show_exec.communicate()
            return self.__re_parse_fn(git_show_result)
        else:
            print("Unable to get rev_id")

    def commit(self):
        commit_args = [self.git_exec, "commit", "-m", self.git_comment]
        commit_exec = subprocess.call(commit_args)
        if commit_exec != 0:
            print(f"There are some errors after git_commit executed")
        else:
            return self.git_comment

    def zero_action(self, zero_file):
        pass

    def __re_parse_fn(self, data):
        parse_temp = re.compile("(diff\s--git\s.*\/(.*?)\n)([\s\S]*?)(?=diff.*)")
        git_temp = re.compile("(@@.*@@)([\s\S]*?)(?=@@|$)")
        host_dict = {}
        for x in parse_temp.findall(data):
            data = git_temp.findall(x[2])
            host = x[1]
            host_dict[host] = []
            for lines in data:
                if "clock-period" in lines[1]:
                    pass
                else:
                    host_dict[host].append(lines[1])
        result_data = "Start\n"
        for key, value in host_dict.items():
            if not len(value) == 0:
                format_host = "\n\n{:=^40}\n\n".format(key)
                result_data += format_host
                for change in value:
                    result_data += change
        return result_data
