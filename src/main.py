# https://www.geeksforgeeks.org/python/command-line-arguments-in-python/
import argparse
import re

# Next steps:
# refactor current code
# create legEntry instances for each log line found and put them into a list
# take the hardcoded regex logic out of the code somehow, so the regex and the group field to capture
# Add a unit test that takes a known input text source and makes sure the created logentries match it
# add a verbose flag or something so i can print the debug messages without commenting them out
# there is a built in logging module (import logging) that i could use for this, or just a simple function that prints
# if the verbose flag is set 


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

    # if args.Logfile:
    #     print(f"the passed in log file is {args.Logfile}")
    
    # Here i can either read the whole log or iterate through it line by line
    with open(args.Logfile) as f:
        lines = f.readlines()
    
    # If a message ID is found, all subsequent lines will contain the message ID
    # the next line that doesn't is a different entry
    currentMessageId = None
    currentMessage={}
    for line in lines:
        messageID = None
        messageIDSearch = re.search("[0-9,A-F]{11}",line)

        if messageIDSearch:
            messageID=messageIDSearch.group(0)

        if messageID and messageID == currentMessageId:
            #print(f"Found current message id {messageID}")
            
            subject = re.search("(?<=Subject: ).+(?= from.+\[.+\])",line)
            if (subject):
                #print (f"Found subject: {subject.group(0)}")
                currentMessage["subject"] = subject.group(0)
                

            sender = re.search("(?<=[0-9,A-F]{11}: from=<)[^>]+",line)
            if (sender):
                #print (f"Found sender: {sender.group(0)}")
                currentMessage["sender"] = sender.group(0)
            
            
            recipient = re.search("(?<=[0-9,A-F]{11}: to=<)[^>]+",line)
            if (recipient):
                #print (f"Found recipient: {recipient.group(0)}")
                currentMessage["recipient"] = recipient.group(0)

            status = re.search("(?<=status=)[^ ]+",line)
            if (status):
                #print (f"Found status: {status.group(0)}")
                currentMessage["status"] = status.group(0)

            protocol = re.search("(?<=proto=)[^ ]+",line)
            if (protocol):
                #print (f"Found protocol: {protocol.group(0)}")
                currentMessage["protocol"] = protocol.group(0)

        elif messageID:
            #print(f"Found new message id {messageID}")
            if currentMessageId:
                print("Message found is:")
                print(currentMessage)

            currentMessageId = messageID
            currentMessage["messageID"] = messageID

            timeInfo = re.search("^[^ ]+",line)
            if (timeInfo):
                time = timeInfo.group(0)
                currentMessage["time"] = time

            clientInfo = re.search("(?<=client=)([^[]+)\[([^]]+)",line)
            if (clientInfo):
                clientName = clientInfo.group(1)
                clientIP = clientInfo.group(2)
                #print (f"Found client named {clientName} with IP {clientIP}")
                currentMessage["clientName"] = clientName
                currentMessage["clientIP"] = clientIP
            mailServer = re.search("^[^ ]+\s([^ ]+)",line)
            if (mailServer):
                #print (f"Found mailServer: {mailServer.group(1)}")
                currentMessage["mailServer"] = mailServer.group(1)
        else:
            #print("Found a line with no message ID on it, skipping it...")
            pass
            
    print("Message found is:")
    print(currentMessage)

if __name__ == '__main__':
    main()