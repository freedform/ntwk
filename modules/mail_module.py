import smtplib

def mail_fn(msg, subject):
    mail_server = smtplib.SMTP('dag01.ad.ums.uz', 25)
    mail_list = "netman@ums.uz"
    mail_from = "ansible@ums.uz"
    mail_subject = subject
    mail_text = msg
    mail_body = f"From: {mail_from}\nTo: {mail_list}\nSubject: {mail_subject}\n\n{mail_text}"
    mail_send = mail_server.sendmail("ansible@ums.uz", mail_list, mail_body)
