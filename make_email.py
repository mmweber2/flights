from email.mime.text import MIMEText
import smtplib

def create_email(text_data, recipient, sender):
    """Generate an email containing the given text.

    Args:
        text_data: string, the message to write in the email.

        recipient: string, the email address to which the message will be sent.
            Must be a valid email address.

        sender: string, the email address from which to send the email.

    Returns:
        A MIMEText email object with the given data.
    """
    if not text_data:
        # No results for this search
        base_msg = ("Sorry, there weren't any results for your flight" +
            " searches today.\nIf you're in a hurry, you might try increasing" +
            " or removing the maximum price or maximum flight length in your" +
            " search.\n")
        subject = "No flights found today."
    else:
        base_msg = ("Hey there! Here are your daily flight search results.\n\n")
        subject = 'Your daily flight search results' 
    msg = MIMEText(base_msg + text_data)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = recipient
    return msg

def send_email(email, filepath, smtp):
    """Sends an email message.
    
    Args:
        email: MIMEText object, the email to send.
        
        filepath: string, the system path to a file containing the password
            for the message sender's email account.

        smtp: string, the smtp server for the sender's email account.
                For example, the Gmail server is smtp.gmail.com.

    Raises:
        smtplib.SMTPAuthenticationError: The username and password were not
            accepted by the email server, or the email account does not allow
            access from this program.
    """
    # Get sender/receiver data from message
    recipient = email['To']
    email_user = email['From']
    email_pwd = ""
    ssl_server = smtplib.SMTP_SSL(smtp, 465)
    ssl_server.ehlo()
    with open(filepath, 'r') as filename:
        email_pwd = filename.read().strip()
    ssl_server.login(email_user, email_pwd)
    ssl_server.sendmail(email_user, recipient, email.as_string())
    ssl_server.close()
