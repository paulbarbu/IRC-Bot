import smtplib
import config

def email_alert(s, components):
    first_word = components['arguments'].split()[0]

    import pdb
    #pdb.set_trace()
    if ':' in first_word:
        if first_word[:first_word.index(':')] in config.owner and first_word[:first_word.index(':')] in config.owner_email.keys():
            send_alert(components, config.owner_email[first_word[:first_word.index(':')]])
    else:
        if first_word in config.owner and first_word in config.owner_email.keys():
            send_alert(components, config.owner_email[first_word])

def send_alert(component, to_address):
    status = False
    sender = component['sender']
    channel = component['action_args'][0]
    ircmsg = component['arguments']
    message = ircmsg[ircmsg.index(' ')+1:]

    try:
        server = smtplib.SMTP(config.smtp_server, config.smtp_port, timeout=2)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(config.from_email_address, config.from_email_password)
    except smtplib.SMTPException as e:
        print e
        server.quit()
        return status
    except IOError as e:
        print e
        return status

    msg = ("From: %s\r\nTo: %s\r\n\r\n%s (%s) said:\r\n\r\n%s") % (config.from_email_address, to_address, sender, channel, message)
    print msg

    try:
        server.sendmail(config.from_email_address, to_address, msg)
    except smtplib.SMTPException as e:
        print e
        server.quit()

        return status

    server.quit()
    return status
