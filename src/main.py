# https://www.geeksforgeeks.org/python/command-line-arguments-in-python/
import argparse
import re
import logging
import mysql.connector
from dotenv import load_dotenv
import os

from logField import logField
from logParser import logParser
from logEntry import logEntry

# Next steps:
# Make the SQL insert logic non-hardcoded, it should loop through the fields
# and build a SQL statement to do the insert
# Create the database if it doesn't already exist
# Create the table for the log type if it doesn't already exist in the database
# Improve the code that does the DB inserts to possibly do them in bulk
# See if there is a better way to handle DB inserts for already existing records
# Add a flag to allow for searching the log file being parsed
# Add a unit test that takes a known input text source and makes sure the created logentries match it

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

    load_dotenv()  # Loads variables from .env into os.environ
    DBHOST=os.getenv("DBHOST")
    DBUSER=os.getenv("DBUSER")
    DBPASSWORD=os.getenv("DBPASSWORD")
    DBDATABASE=os.getenv("DBDATABASE")

    msg = "Python Postfix log parser"
    parser = argparse.ArgumentParser(description=msg)

    parser.add_argument("-l", "--logfile", help = "Path to the log file to parse")
    parser.add_argument("-v","--verbose",help= "Set the verbosity level",action="count",default=0)
    args = parser.parse_args()

    print(f"verbose level set to {args.verbose}")
    if args.verbose > 0:
        logging.basicConfig(level=logging.DEBUG)

    #Create the log fields that I want to parse
    indexField = logField("MessageID", "[0-9,A-F]{11}")
    logFields = [
        logField("Subject", "(?<=Subject: ).+(?= from.+\[.+\])"),
        logField("Sender", "(?<=[0-9,A-F]{11}: from=<)[^>]+"),
        logField("Recipient", "(?<=[0-9,A-F]{11}: to=<)[^>]+"),
        logField("Status", "(?<=status=)[^ ]+"),
        logField("Protocol", "(?<=proto=)[^ ]+"),
        logField("DateTime", "^[^ ]+"),
        logField("MailServer", "(?<=^.{32}\s)[^ ]+"),
        logField("ClientName", "(?<=client=)([^[]+)\[([^]]+)",1),
        logField("ClientIP", "(?<=client=)([^[]+)\[([^]]+)",2)
    ]

    # Connect to the SQL Instance holding the logs
    mydb = mysql.connector.connect(
        host=DBHOST,
        user=DBUSER,
        password=DBPASSWORD,
        database=DBDATABASE
        )

    mycursor = mydb.cursor()

    postfixLogParser = logParser(indexField,logFields)
    postfixLogParser.parseLog(args.logfile)

    print("Complete logs:")
    completeLogs = postfixLogParser.getCompleteLogEntries()
    print(completeLogs)

    print("Incomplete logs:")
    print(postfixLogParser.getIncompleteLogEntries())

    #Insert the complete log entries into the database

    for log in completeLogs:
        sql = "INSERT INTO postfixlogs (MessageID, Sender,Recipient,Status,Protocol,DateTime,MailServer,ClientName,ClientIP) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        val = (log.fields["MessageID"], log.fields["Sender"],log.fields["Recipient"],log.fields["Status"],log.fields["Protocol"],log.fields["DateTime"],log.fields["MailServer"],log.fields["ClientName"],log.fields["ClientIP"])
        
        #There is probably a better way to handle this then catching the error and doing nothing
        #Look into this when optimising the program
        try:
            mycursor.execute(sql, val)
            mydb.commit()
        except Exception as e:
            print(e)


if __name__ == '__main__':
    main()