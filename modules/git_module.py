from classes.git_class import GitClass
from modules import mail_module


def git(repo_dir):
    action_dict = {'untracked_files': 'add_file',
                   'added_files': 'zero_action',
                   'modified_files': 'add_file',
                   'deleted_files': 'rm_file',
                   'unkhown_files': 'zero_action'}
    gc = GitClass(repo_dir)
    gc.status()
    git_status = gc.status_dict
    commit_count = 0
    commit_comment = None
    for st_type, st_files in git_status.items():
        if len(st_files) > 0:
            for st_file in st_files:
                getattr(gc, action_dict[st_type])(st_file)
            commit_count += 1
        else:
            pass
    if commit_count != 0:
        commit_comment = gc.commit()
    else:
        print("Nothing to commit")
    if commit_comment is not None:
        mail_subject = "Changes after ansible backup"
        mail_module.mail_fn(gc.git_log_comment(commit_comment), mail_subject)
    else:
        print("Nothing to show ")
