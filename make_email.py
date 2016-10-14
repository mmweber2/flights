from email.mime.text import MIMEText
import smtplib

def create_email(text_data, recipient):
    """Generate an email containing the given text.

    Args:
        text_data: string, the message to send in the email.

        recipient: string, the email address to which the message
            will be sent. Must be a valid email address.

    Returns:
        A String conversion of a MIMEText object with the given data.
    """
    # TODO: Error checking
    base_msg = "Hey there! Here are your daily Japan flight search results.\n\n"
    msg = None
    # TODO: Replace with actual search results
    with open('search_output.txt', 'r') as filename:
        msg = MIMEText(base_msg + filename.read())
    msg['Subject'] = 'Your daily Japan flight search results' 
    msg['From'] = "" # TODO: New gmail account
    msg['To'] = recipient
    return msg.as_string()

def send_email(message, recipient):
    """Sends an email message.
    
    Args:
        message: string, the email message to send.
        
        recipient: string, the email address to which the message
            will be sent. Must be a valid email address.

    Raises:
        smtplib.SMTPAuthenticationError: The username and password were not
            accepted by the email server, or the email account does not allow
            access from this program.
    """
    # TODO: Error checking
    ssl_server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    ssl_server.ehlo()
    # TODO: Make a new Gmail account to send these
    email_user = ""
    email_pwd = ""
    ssl_server.login(email_user, email_pwd)
    ssl_server.sendmail(email_user, recipient, message)
    ssl_server.close()

print create_email(None)
send_email(create_email(None))

