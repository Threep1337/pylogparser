# https://www.geeksforgeeks.org/python/command-line-arguments-in-python/
import argparse
import re
import logging

from logField import logField
from logParser import logParser
from logEntry import logEntry

# Next steps:
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

    postfixLogParser = logParser(indexField,logFields)
    postfixLogParser.parseLog(args.logfile)


if __name__ == '__main__':
    main()