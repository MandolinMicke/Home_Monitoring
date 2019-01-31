# -*- coding: utf-8 -*-

#import sys
import imaplib
import smtplib

import email
import email.header
#import datetime

import time
import mailcreds as mc

import std_cmd as sc

from ssl import SSLEOFError as ssler
SMTP_SERVER = "imap.gmail.com"
SMTP_PORT   = 993




# -------------------------------------------------
#
# Utility to read email from Gmail Using Python
#
# ------------------------------------------------

def read_email_from_gmail(subject = None, user = 'tarendo'):
    tries = 0
    rettext = None
    while tries <10:
        try:    
            mail = imaplib.IMAP4_SSL(SMTP_SERVER)
            mail.login(mc.EMAIL[user],mc.PWD[user])

        
            # Out: list of "folders" aka labels in gmail.
            mail.select("inbox") # connect to inbox.
        
            # Get all unread emails
            if subject == None:
                typ, msg_num = mail.search(None,'(UNSEEN)')
            else:
                typ, msg_num = mail.search(None,'(UNSEEN SUBJECT "' + subject + ' ")')
                
            # check if a new mail is here and get the text
            if msg_num[0].decode().split(' ')[0]:
                rettext = []
                for num in msg_num[0].decode().split(' '):
                    result, data = mail.fetch(num.encode(), '(RFC822)')
                    raw_email = data[0][1].decode()
                    email_message = email.message_from_string(raw_email)
                    mejltext = email_message.get_payload()
                    rettext.append(mejltext)
            else:
                rettext = None
            
        except (imaplib.IMAP4.abort, imaplib.IMAP4.error,ssler):
            time.sleep(1)
            tries += 10
            rettext = 'FAIL'
            continue
        mail.logout()
#        mail.close()
        break
    return rettext

def decodeMail(text):
    retcommands = {}
    for i in text:
        stringlist = i.split('\n')
        if stringlist[0].strip() == 'History':
            retcommands = []
            del(stringlist[0])
            for s in stringlist:
                retcommands.append(s.strip())
        else:
            for s in stringlist:
                if any([x in s for x in sc.systemcommands]):
                    strs = s.strip().split(' ')
                    retcommands[strs[0]] = strs[1]
    return retcommands


def sendEmail(body,fromaddr,toaddr,subject):

    sent_from = mc.EMAIL[fromaddr]
    to = [mc.EMAIL[toaddr]]

    try:  
        message = 'Subject: {}\n\n{}'.format(subject, body)   
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(mc.EMAIL[fromaddr],mc.PWD[fromaddr])
        server.sendmail(sent_from, to, message)
        server.close()
        print('Email sent!')
    except:  
        print('Something went wrong...')
if __name__ == '__main__':
     text = read_email_from_gmail('GUI', 'tarendo')
#     print(text)
     if text != None:
         print(decodeMail(text))
#    sendEmail('hej hopp','tarendo','system')



