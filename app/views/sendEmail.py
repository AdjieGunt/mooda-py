import smtplib
from smtplib import SMTP, SMTPAuthenticationError, SMTPException
import string
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class senEmail():                                    #create class
    def __init__(self, send_to):                    #create contruct
        self.send_to = send_to


    def oto(self):
        # print self.send_to
        
        host_email = "smtp.gmail.com"
        port_email = 587
        username = "calakmania@gmail.com"
        password = "jemmycalak14"
        # send_to = "jemmy.sapta14@gmail.com"

        msg = MIMEMultipart('alternativ')
        msg ['To'] = self.send_to
        # msg ['CC'] = CC
        msg['Subject'] = "MOODA MAIL ELEKTROMAIL"
        #create text HTML
        Text ="""\
        <html>
        <head></head>
        <body>
            <H1>Hi!</H1>
            <H1> INI ADALAH EMAIL DARI CAMART, I HOPE YOU ENJOY THE SHOP.</H1>
            
        </body>
        </html>
        """
        #convert text HTML
        hateemel = MIMEText(Text, 'html')
        msg.attach(hateemel)

        # email_to = params['email_to']
        # email_cc = params.get('email_cc')
        # email_bcc = params.get('email_bcc')
        # manyEmail = [email_to] + [email_cc] + [email_bcc]

        # Body = string.join((
        # "From: %s" % username,
        # "To: %s" % self.send_to,
        # "Subject: %s" % Subj,
        # "",
        # hateemel,
        # ), "\r\n")

        email_con = smtplib.SMTP(host_email, port_email)
        email_con.ehlo()
        email_con.starttls()
        try:
            email_con.login(username, password)
            email_con.sendmail(username, self.send_to, msg.as_string())                 #call data from contruct

            print "succes send email"

        except smtplib.SMTPAuthenticationError:
            print("Error Login.")
        except:
            print("An error occured.")

        email_con.quit()