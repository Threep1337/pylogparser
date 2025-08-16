
# Replace this with argparse later
# https://www.geeksforgeeks.org/python/command-line-arguments-in-python/
import sys
import argparse
import re

# First goal is to just extract text from the log file and print out log lines
# Worry about making it more complex afterwards
# I think I will need to use regular expressions to extract the fields from the log lines.
# I will also need to take arguments into the script call that point to the file
# Later on I can deal with ingesting the logs into a database.


# First basic goal should be to parse a file containing only one message, 
# and create a list of objects that represent entries


# Here is some AI generated program outline:

# High-level structure for postfix log analyzer
# 1. LogReader – reads raw log lines from file(s)
# 2. LogParser – parses lines into structured data
# 3. LogEntry – class to represent a single parsed message
# 4. LogStorage – stores parsed entries (list or later a DB)
# 5. SearchEngine – filters/searches entries by criteria
# 6. CLI/Interface – user interaction (command line first)

# Classes:
# LogEntry: holds timestamp, queue_id, from_address, to_address, status, raw_line
# LogReader: opens log file, yields lines
# LogParser: converts raw line -> LogEntry (regex helpers etc.)
# LogStorage: keeps all LogEntry objects (list or indexed)
# SearchEngine: query/filter functions on LogStorage
# PostfixAnalyzer (optional): ties everything together

# Flow:
# - Reader gets lines
# - Parser builds LogEntry
# - Storage keeps entries
# - SearchEngine finds matches
# - Results printed/output



def main():

    msg = "Python Postfix log parser"

    parser = argparse.ArgumentParser(description=msg)

    parser.add_argument("-l", "--Logfile", help = "Path to the log file to parse")
    args = parser.parse_args()


    if args.Logfile:
        print(f"the passed in log file is {args.Logfile}")
    
    #here i can either read the whole log or iterate through it line by line
    with open(args.Logfile) as f:
        lines = f.readlines()
    #print(f"{file_contents}")

    #Extract the message ID in the line
    #Message IDs are 11 characters and look to contain 0-9 and A-F
    #[0-9,A-F]{11}

    #Client name
    #Client IP
    #Extract from the capture groups
    #(?<=client=)([^[]+)\[([^]]+)

    #subject
    #(?<=Subject: ).+(?= from.+\[.+\])

    #from
    # (?<=[0-9,A-F]{11}: from=<)[^>]+
    #to
    #(?<=[0-9,A-F]{11}: to=<)[^>]+

    #status
    # (?<=status=)[^ ]+

    #Mail server name

    #^[^ ]+\s([^ ]+)
    
    # If a message ID is found, all subsequent lines will contain the message ID
    # the next line that doesn't is a different entry
    currentMessageId = None
    for line in lines:
        #This is bad, I can't assume group 0 will exist, i first need to do the regex, then test if it found anything
        messageID = re.search("[0-9,A-F]{11}",line).group(0)
        if messageID == currentMessageId:
            print(f"Found current message id {messageID}")
            
            subject = re.search("(?<=Subject: ).+(?= from.+\[.+\])",line)
            if (subject):
                print (f"Found subject: {subject.group(0)}")

            sender = re.search("(?<=[0-9,A-F]{11}: from=<)[^>]+",line)
            if (sender):
                print (f"Found sender: {sender.group(0)}")
            
            
            recipient = re.search("(?<=[0-9,A-F]{11}: to=<)[^>]+",line)
            if (recipient):
                print (f"Found recipient: {recipient.group(0)}")

            status = re.search("(?<=status=)[^ ]+",line)
            if (status):
                print (f"Found status: {status.group(0)}")

            protocol = re.search("(?<=proto=)[^ ]+",line)
            if (protocol):
                print (f"Found protocol: {protocol.group(0)}")

        elif messageID:
            print(f"Found new message id {messageID}")
            currentMessageId = messageID
            clientInfo = re.search("(?<=client=)([^[]+)\[([^]]+)",line)
            if (clientInfo):
                clientName = clientInfo.group(1)
                clientIP = clientInfo.group(2)
                print (f"Found client named {clientName} with IP {clientIP}")
            mailServer = re.search("^[^ ]+\s([^ ]+)",line)
            if (mailServer):
                print (f"Found mailServer: {mailServer.group(1)}")
        else:
            pass
            



if __name__ == '__main__':
    main()