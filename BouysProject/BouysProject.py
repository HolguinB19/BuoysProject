import imaplib
import email
from email.header import decode_header
import webbrowser
import os
import shutil
from bs4 import BeautifulSoup
import re
import pandas as pd
import json
import sys

# account credentials
#username = ""
#password = ""
# THE ABOVE CODE WAS CHANGED TO PROTECT CONFIDENTIAL INFORMATION #

def clean(text):
 # clean text for creating a folder
 return "".join(c if c.isalnum() else "_" for c in text)

#Checks to see if command line arguments were passed. 
if (len(sys.argv) < 3):
    sys.exit("You must pass command line arguments in the form: BouysProject <Email Address> <Password>")
    
username = sys.argv[1]
password = sys.argv[2]



def writeEmail(subject, body):
    f = open(subject, "w+")
    f.write(body)
    f.close()

#reads the original text file, and changes some things to make it easier to parse as well as creates a csv
#of the input text file
def readTextfile(subject):
    with open(subject + '.txt', "r") as f:
        text = f.read()

        #replace all colons followed by a space with an equals sign
        interText = re.sub(': ', r'=', text, flags = re.M)

        #replace all equal signs with a newline
        newlineText = re.sub('=|\n', r'\n', interText, flags = re.M)
        
        #replace all equal signs with a space
        jsonText = re.sub('^.*(=)', r'', interText, flags = re.M)

        open('jsonText.txt', "w").write(jsonText)

        keyList = ['IMEI', 'MOMSN', 'Transmit Time', 'Iridium Latitude', 'Iridium Longitude', 'Iridium CEP', 'Iridium Session Status', 'Data', 'GMT', 'LBT', 'Lat', 'Lon', 'BP', 'Ts']

        
        dict1 = {}
  
        # creating dictionary
        with open('jsonText.txt') as fh:
            count = 0
  
            for line in fh:
  
                dict1[keyList[count]] = line.strip()
                count+=1
  
        # creating json file
        # the JSON file is named as test1
        out_file = open(subject + ".json", "w")
        json.dump(dict1, out_file, indent = 4, sort_keys = False)
        out_file.close()
        

        #write the new textfile to the original
        open('newline.txt', "w").write(newlineText)

        # DELETE THIS MULTILINE COMMENT AFTER WE START GETTING INPUT #
        # DELETE THIS MULTILINE COMMENT AFTER WE START GETTING INPUT #
        # DELETE THIS MULTILINE COMMENT AFTER WE START GETTING INPUT #
        # DELETE THIS MULTILINE COMMENT AFTER WE START GETTING INPUT #
        """
        with open('newline.txt', "r") as g:
            csvOutput = ''
            count = 0
            for line in g:
                count+=1
                line = line.strip()
                if count == 2:
                    csvOutput += line
                elif count % 2 == 0:
                    csvOutput += ',' + line
        open('csv.txt', "w").write(csvOutput)
                
        csvFile = pd.read_csv('csv.txt', header=None)
        csvFile.columns = ['IMEI', 'MOMSN', 'Transmit Time', 'Iridium Latitude', 'Iridium Longitude', 'Iridium CEP', 'Iridium Session Status', 'Data', 'GMT', 'LBT', 'Lat', 'Lon', 'BP', 'Ts']
        csvFile.to_csv(subject + '.csv', index=False)
        
        os.remove('newline.txt')
        os.remove('csv.txt')
        os.remove('jsonText.txt')
        """
        # DELETE THIS MULTILINE COMMENT AFTER WE START GETTING INPUT #
        # DELETE THIS MULTILINE COMMENT AFTER WE START GETTING INPUT #
        # DELETE THIS MULTILINE COMMENT AFTER WE START GETTING INPUT #
        # DELETE THIS MULTILINE COMMENT AFTER WE START GETTING INPUT #



# number of top emails to fetch
N = 1

# create an IMAP4 class with SSL
imap = imaplib.IMAP4_SSL("imap.gmail.com")
# authenticate
imap.login(username, password)

# select a mailbox (in this case, the inbox mailbox)
# use imap.list() to get the list of mailboxes
status, messages = imap.select("INBOX")

# total number of emails
messages = int(messages[0])

for i in range(messages, messages-N, -1):
    # fetch the email message by ID
    res, msg = imap.fetch(str(i), "(RFC822)")
    for response in msg:
        if isinstance(response, tuple):
            # parse a bytes email into a message object
            msg = email.message_from_bytes(response[1])
            # decode the email subject
            subject, encoding = decode_header(msg["Subject"])[0]
            if isinstance(subject, bytes):
                # if it's a bytes, decode to str
                subject = subject.decode(encoding)
            # decode email sender
            From, encoding = decode_header(msg.get("From"))[0]
            if isinstance(From, bytes):
                From = From.decode(encoding)
            print("Subject:", subject)
            print("From:", From)
            # if the email message is multipart
            if msg.is_multipart():
                # iterate over email parts
                for part in msg.walk():
                    # extract content type of email
                    content_type = part.get_content_type()
                    print(content_type)
                    content_disposition = str(part.get("Content-Disposition"))
                    try:
                        # get the email body
                        body = part.get_payload(decode=True).decode()
                    except:
                        pass
                    if content_type == "text/plain" and "attachment" not in content_disposition:
                        # print text/plain emails and skip attachments
                        print(body)

                    elif "attachment" in content_disposition:
                        # download attachment
                        filename = part.get_filename()
                        if filename:
                            folder_name = clean(subject)
                            if not os.path.isdir(folder_name):
                                # make a folder for this email (named after the subject)
                                os.mkdir(folder_name)
                            filepath = os.path.join(folder_name, filename)
                            # download attachment and save it
                            open(filepath, "wb").write(part.get_payload(decode=True))
            else:
                # extract content type of email
                content_type = msg.get_content_type()
                print(content_type)
                # get the email body
                body = msg.get_payload(decode=True).decode()
                if content_type == "text/plain":
                    # print only text email parts
                    print(body)
            if content_type == "text/html":
                # if it's HTML, create a new HTML file and open it in browser
                folder_name = clean(subject)
                if not os.path.isdir(folder_name):
                    # make a folder for this email (named after the subject)
                    os.mkdir(folder_name)
                filename = "index.html"
                filepath = os.path.join(folder_name, filename)
                # write the file
                open(filepath, "w").write(body)
                open("index.html", "w").write(body)
                
                with open('index.html', 'r') as f:
                    contents = f.read()

                    soup = BeautifulSoup(contents, "lxml")
                    open(subject + '.txt', "w").write(soup.getText("\n", strip=True))
                    print(soup.get_text())
                readTextfile(subject)
                os.remove('index.html')
                shutil.rmtree(folder_name)
            print("="*100)
# close the connection and logout
imap.close()
imap.logout()

