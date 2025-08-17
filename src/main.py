# https://www.geeksforgeeks.org/python/command-line-arguments-in-python/
import argparse
import re

from logField import logField
from logParser import logParser
from logEntry import logEntry

# Next steps:
# refactor current code
# create logEntry instances for each log line found and put them into a list
# take the hardcoded regex logic out of the code somehow, so the regex and the field to capture
# Add a unit test that takes a known input text source and makes sure the created logentries match it
# add a verbose flag or something so i can print the debug messages without commenting them out
# there is a built in logging module (import logging) that i could use for this, or just a simple function that prints
# if the verbose flag is set 

# Cant assume that log entries for a particular messageId are all on adjacent lines
# so message ID is the only way to tie them together
# Maybe make the fields and the regexes to find them be part of an object?  so like subject,TheRegex
# Maybe a log entry is a collection of log fields, and each log field has a name and a regex to capture it?
# one of the fields is the identifier field, the rest is other fields, so a single item and a list of items
# log entry can have an isComplete method that checks if all of the fields have values

## No, log entry should not have any parse logic in it.
# make a log parser class that has an identifier logfield, and a list of other fields
# on every line, run the regex check for the identifier field, then check if a log entry already exists for the identifier
# if it does, skip checking the other fields if they already have a value, so it minimizes the regex calls
# the log parser can create log entries and maintains a list of them while it parses a log

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
        logField("DateTime", "^[^ ]+")
        
    ]

    postfixLogParser = logParser(indexField,logFields)
    postfixLogParser.parseLog(args.Logfile)


if __name__ == '__main__':
    main()