import email
import imaplib

EMAIL = 'bf.automate@gmail.com'

PASSWORD = 'jrrm xema evdw uvrr'

SERVER = 'imap.gmail.com'

def connect_to_imap():
    mail = imaplib.IMAP4_SSL(SERVER)
    mail.login(EMAIL, PASSWORD)
    mail.select('inbox')
    return mail

def retrieve_emails(mail):
    #status, data = mail.search(None, '(UNSEEN FROM "noreply@formspree.io")')
    status, data = mail.search(None, '(UNSEEN FROM "noreply@formspree.io")')
    mail_ids = []
    for block in data:
        mail_ids += block.split()
    return mail_ids

def parse_email(mail, mail_id):
    status, data = mail.fetch(mail_id, '(RFC822)')
    message = email.message_from_bytes(data[0][1])
    mail_from = message['from']
    mail_subject = message['subject']
    mail_content = ''
    if message.is_multipart():
        for part in message.get_payload():
            if part.get_content_type() == 'text/plain':
                mail_content += part.get_payload()
    else:
        mail_content = message.get_payload()
    return mail_from, mail_subject, mail_content

def scan_email():
    
    mail = connect_to_imap()
    mail_ids = retrieve_emails(mail)
    if mail_ids:
        for mail_id in mail_ids:
            mail_from, mail_subject, mail_content = parse_email(mail, mail_id)
            #print(f'From: {mail_from}')
            #print(f'Subject: {mail_subject}')
            mail_content_list = mail_content.split("\n")
            content_text = [line.strip() for line in mail_content_list if line.strip()]

            
            topic = content_text[content_text.index("message:")+1]

            #print(topic)
            return topic
    else:
        return None

if __name__ == '__main__':
    print(scan_email())
