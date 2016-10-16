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
    # No results for this search
    if not text_data:
        base_msg = ("Sorry, there weren't any results for your flight searches" +
            " today.\nIf you're in a hurry, you might try increasing the" +
            " maximum price or maximum flight length in your search.\n")
        subject = "No Japan flights found today."
    else:
        base_msg = ("Hey there! Here are your daily Japan flight search" +
            " results.\n\n")
        subject = 'Your daily Japan flight search results' 
    msg = MIMEText(base_msg + text_data)
    msg['Subject'] = subject
    msg['From'] = "japanflightcheck@gmail.com"
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
    email_user = "japanflightcheck@gmail.com"
    email_pwd = ""
    with open("/Users/Toz/code/gmail.txt", 'r') as filename:
        email_pwd = filename.read().strip()
    ssl_server.login(email_user, email_pwd)
    ssl_server.sendmail(email_user, recipient, message)
    ssl_server.close()

# TODO: Find cleaner way of passing recipient to both

