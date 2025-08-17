# https://www.geeksforgeeks.org/python/command-line-arguments-in-python/
import argparse
import re

from logField import logField
from logParser import logParser
from logEntry import logEntry

# Next steps:
# Add a unit test that takes a known input text source and makes sure the created logentries match it
# add a verbose flag or something so i can print the debug messages without commenting them out
# there is a built in logging module (import logging) that i could use for this, or just a simple function that prints
# if the verbose flag is set 
# log entry can have an isComplete method that checks if all of the fields have values

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


    #Create the log fields that I want to parse
    #Going to need to do something different for client and client ip, and mailserver
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

    postfixLogParser = logParser(indexField,logFields)
    postfixLogParser.parseLog(args.Logfile)


if __name__ == '__main__':
    main()