import sys
import smtplib

print "External call to sip_email.py"
for arg in sys.argv:
    subject = arg

def send_email(recipient, subject):
    print "sending email..."
#    if not elapsedMoreThan( 10 ):
#       return
#    gmail_user = 'pepe.femenias@gmail.com'
    gmail_user = 'newhousegate@gmail.com'
    gmail_pwd = 'newhousegate.google'
#    gmail_pwd = 'crbgkzyeivwkuuqg'
    FROM = "NewHouseGate"
    TO = recipient if type(recipient) is list else [recipient]
    SUBJECT = subject
    TEXT = subject +" has just opened/closed the gate"

    # Prepare actual message
    message = """From: %s\nTo: %s\nSubject: %s\n\n%s
    """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(gmail_user, gmail_pwd)
        server.sendmail(FROM, TO, message)
        server.close()
        print 'successfully sent the mail: ' + subject
    except Exception as e:
        print "failed to send mail.Reason: " + str(e)
    #last_email_datetime = datetime.datetime.now()

send_email( "jose.femenias@gmail.com", subject )
