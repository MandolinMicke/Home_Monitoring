import sys
import imaplib
import smtplib

import email
import email.header
import datetime

import mailcreds as mc

import std_cmd as sc

SMTP_SERVER = "imap.gmail.com"
SMTP_PORT   = 993






# -------------------------------------------------
#
# Utility to read email from Gmail Using Python
#
# ------------------------------------------------

def read_email_from_gmail(user):
    mail = imaplib.IMAP4_SSL(SMTP_SERVER)
    mail.login(mc.EMAIL[user],mc.PWD[user])
    mail.select('inbox')

    # Out: list of "folders" aka labels in gmail.
    mail.select("inbox") # connect to inbox.

    # Get all unread emails
    typ, msg_num = mail.search(None,'(UNSEEN)')#'ALL')#(UNSEEN)')
    
    # check if a new mail is here and get the text
    if msg_num[0].decode().split(' ')[0]:
        rettext = []
        for num in msg_num[0].decode().split(' '):
            result, data = mail.fetch(num.encode(), '(RFC822)')
            raw_email = data[0][1].decode()
            email_message = email.message_from_string(raw_email)
            maintype = email_message.get_content_maintype()
            mejltext = email_message.get_payload()[0].get_payload()
            rettext.append(mejltext)
    else:
        rettext = None
    mail.close()
    return rettext

def decodeMail(text):
    retcommands = {}
    for i in text:
        stringlist = i.split('\n')
        for s in stringlist:
            if any([x in s for x in sc.searchablecommands]):
                strs = s.strip().split(' ')
                retcommands[strs[0]] = strs[1]
                
          # print([x for x in stringlist if x in sc.searchablecommands])
    return retcommands


def sendEmail(body,fromaddr,toaddr):

    sent_from = mc.EMAIL[fromaddr]
    to = [mc.EMAIL[toaddr]]   

    # print(email_text)
    # try:  
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.ehlo()
    server.login(mc.EMAIL[fromaddr],mc.PWD[fromaddr])
    server.sendmail(sent_from, to, body)
    server.close()

        # print('Email sent!')
    # except:  
        # print('Something went wrong...')
if __name__ == '__main__':
    # text = read_email_from_gmail()
    # if text != None:
        # print(decodeMail(text))
    sendEmail('hej har kommer ett mejl med grejs','tarendo','system')



