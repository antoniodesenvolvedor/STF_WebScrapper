import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import Flask, request
import json



class mailSender:

    def __init__(self):
        self._host = 'smtp.gmail.com'
        self._port = 587
        self._login = 'antoniodesenvolvedor2@gmail.com'
        self._password = 'Xsalada3'


    def send_mail(self, subject, message, recipient):
        server = smtplib.SMTP(host=self._host, port=self._port)
        server.starttls()
        server.login(self._login, self._password)

        msg = MIMEMultipart()

        msg['From'] = self._login
        msg['To'] = recipient
        msg['Subject'] = subject

        msg.attach(MIMEText(message, 'plain'))


        server.send_message(msg)
        server.quit()

        print('email enviado')






app = Flask(__name__)

@app.route('/send_mail', methods=['POST'])
def send_mail():
    content = request.json

    recipient = content['event']['fields']['recipient']
    message = json.loads(content['event']['fields']['message'])['_msg']
    subject = content['event']['fields']['subject']

    main_sender = mailSender()
    try:
        main_sender.send_mail(subject, message, recipient)
        return 'Success',200
    except Exception as e:
        return str(e), 500


@app.route('/')
def hello_world():
    return 'Hello World'



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
