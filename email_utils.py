import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def send_email(to, subject, content):
    message = Mail(
        from_email=os.getenv("DEFAULT_FROM_EMAIL"),
        to_emails=to,
        subject=subject,
        html_content=content
    )
    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        print(response.status_code)
    except Exception as e:
        print(str(e))
