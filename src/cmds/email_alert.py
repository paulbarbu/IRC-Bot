import smtplib
import string
import config

def email_alert(components):
    first_word = components['arguments'].split()[0].strip(string.punctuation)

    if first_word in config.owner and first_word in config.owner_email.keys():
        send_alert(components, config.owner_email[first_word])


def send_alert(component, to_address):
    sender = component['sender']
    channel = component['action_args'][0]
    ircmsg = component['arguments']
    message = ircmsg[ircmsg.index(' ')+1:]

    msg = 'From: {0}\r\nTo: {1}\r\n\r\n{2}({3}) said:\r\n\r\n{4}'.format(
            config.from_email_address, to_address, sender, channel, message)

    try:
        server = smtplib.SMTP(config.smtp_server, config.smtp_port, timeout=2)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(config.from_email_address, config.from_email_password)
    except smtplib.SMTPException as e:
        print e
        server.quit()
        return False
    except IOError as e:
        print e
        return False

    try:
        server.sendmail(config.from_email_address, to_address, msg)
    except smtplib.SMTPException as e:
        print e
        server.quit()

        return False

    server.quit()
    return True
