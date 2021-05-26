import imaplib
import email
from email.header import decode_header
import webbrowser
import os
import shutil
import re
import json
import sys
import csv
from geojson import Feature, FeatureCollection, Point

# account credentials
#username = ""
#password = ""
# THE ABOVE CODE WAS CHANGED TO PROTECT CONFIDENTIAL INFORMATION #


#Global Variables
download = False                        #Activates the downloading of the attached file, if the email contains it
username = sys.argv[1]                  #The username/email that gets scrubbed through. Passed as the first command line argument.
password = sys.argv[2]                  #The Password to the email address. Passed as the second command line argument.



def clean(text):
 # clean text for creating a folder
 return "".join(c if c.isalnum() else "_" for c in text)

#Checks to see if command line arguments were passed. 
if (len(sys.argv) < 3):
    sys.exit("You must pass command line arguments in the form: BouysProject <Email Address> <Password>")
    
try:
    storageDirectory = sys.argv[3]          #The location where the generated csv and json files will be stored.
except:
    print("No file directory specified, defaulting to the same location where the program is located.")
    storageDirectory = ''

try:
    numberOfBuoys = int(sys.argv[4])
except:
    print("Number of buoys not specified, defaulting to 1")
    numberOfBuoys = 1



def writeEmail(subject, body):
    f = open(subject, "w+")
    f.write(body)
    f.close()

def convertToGeojson(IMEI):
    
    features = []
    with open(storageDirectory + IMEI + '.csv', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        next(reader)
        for messageNo, time, latitude, longitude, pressure, temperature in reader:
            Latitude, Longitude = map(float, (latitude, longitude))
            features.append(
                Feature(
                    geometry = Point((float(longitude), float(latitude))),
                    properties = {
                        'Time': time,
                        'Pressure': float(pressure),
                        'Temperature': float(temperature)
                    }
                )
            )

    collection = FeatureCollection(features)
    with open(storageDirectory + IMEI + ".json", "w") as f:
        f.write('%s' % collection)

#reads the original text file, and changes some things to make it easier to parse as well as creates a csv
#of the input text file
def readTextfile(body, IMEI, messageNo):

    noWhitespaceBody = re.sub(r'\n\s*\n', '\n', body)
    
    print(noWhitespaceBody)

    bodyList = noWhitespaceBody.splitlines()

    data = re.sub(r'^.*?: ', '', bodyList[8])
    #print(data + " DATA")
    
    time = re.sub(r'^.*?=', '', bodyList[9])
    #print(time + " TIME")

    lat = float(re.sub(r'^.*?=', '', bodyList[11]))
    #print("{} {}".format(lat, " LAT"))

    lon = float(re.sub(r'^.*?=', '', bodyList[12]))
    #print("{} {}".format(lon, " LON"))

    bp = bodyList[13].split(' ', 1)[0]
    bp = float(re.sub(r'^.*?=', '', bp))
    #print("{} {}".format(bp, " BP"))

    temp = bodyList[14].split(' ', 1)[0]
    temp = float(re.sub(r'^.*?=', '', temp))
    #print("{} {}".format(temp, " TEMP"))

    csvData = [messageNo, time, lat, lon, bp, temp]

    with open(storageDirectory + IMEI + ".csv", 'a+', newline='') as csvFile:
        csvFile.seek(0)
        reader = csv.reader(csvFile)
        currentCsv = list(reader)
        csvLength = len(currentCsv)

        if csvLength == 0:
            writer = csv.writer(csvFile)
            writer.writerow(['Message Number', 'Time', 'Latitude', 'Longitude', 'Pressure', 'Temperature'])
            writer.writerow(csvData)
        else:
            if currentCsv[csvLength-1][0] < messageNo:
                writer = csv.writer(csvFile)
                writer.writerow(csvData)
                convertToGeojson(IMEI)
        csvFile.close()







# number of top emails to fetch
N = numberOfBuoys

# create an IMAP4 class with SSL
imap = imaplib.IMAP4_SSL("imap.gmail.com")
# authenticate
imap.login(username, password)

# select a mailbox (in this case, the inbox mailbox)
# use imap.list() to get the list of mailboxes
status, messages = imap.select("INBOX")

# total number of emails
messages = int(messages[0])

for i in range(messages - N, messages + 1, 1):
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
                        #####print(body)

                        #Saves the IMEI and Message Number as 2 variables
                        tempSubject = subject.split()
                        messageNo = tempSubject[1]
                        IMEI = tempSubject[4]
                        readTextfile(body, IMEI, messageNo)

                    elif "attachment" in content_disposition and download == True:
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

