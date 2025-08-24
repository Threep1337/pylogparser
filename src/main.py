# https://www.geeksforgeeks.org/python/command-line-arguments-in-python/
import argparse
import re
import logging
import mysql.connector
from dotenv import load_dotenv
import os
import time


from logField import logField
from logParser import logParser
from logEntry import logEntry

# Next steps:

# Add a flag to allow for searching the log file being parsed
# Improve the code that does the DB inserts to possibly do them in bulk
# use cursor.executemany(sql, data), where data is a list lists of values to update
# change the insert to insert ignore, to handle records that already exist
# See if there is a better way to handle DB inserts for already existing records
# Make the log field defintion be a config json file rather than hardcoded in main
# Add a unit test that takes a known input text source and makes sure the created logentries match it
# General polish and re-factoring is needed, the code and names are getting ugly
# Add better error checking and error handling
# Finish project for now
# Eventually, add a timer to measure how long this takes so that I can optimise it, I will need a much larger data sample

# Measure time

# import time

# start = time.perf_counter()

# insert_records()

# end = time.perf_counter()
# print(f"Time taken: {end - start:.6f} seconds")

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

    start = time.perf_counter()

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

    if args.verbose > 0:
        logging.basicConfig(level=logging.DEBUG)

    #Create the log fields that I want to parse
    indexField = logField("MessageID", "[0-9,A-F]{11}","char(11)")
    logFields = [
        logField("Subject", "(?<=Subject: ).+(?= from.+\[.+\])","varchar(255)"),
        logField("Sender", "(?<=[0-9,A-F]{11}: from=<)[^>]+","varchar(255)"),
        logField("Recipient", "(?<=[0-9,A-F]{11}: to=<)[^>]+","varchar(255)"),
        logField("Status", "(?<=status=)[^ ]+","varchar(20)"),
        logField("Protocol", "(?<=proto=)[^ ]+","varchar(20)"),
        logField("DateTime", "^[^ ]+","date"),
        logField("MailServer", "(?<=^.{32}\s)[^ ]+","varchar(255)"),
        logField("ClientName", "(?<=client=)([^[]+)\[([^]]+)","varchar(255)",1),
        logField("ClientIP", "(?<=client=)([^[]+)\[([^]]+)","varchar(255)",2)
    ]

    # Connect to the SQL Instance holding the logs
    mydb = mysql.connector.connect(
        host=DBHOST,
        user=DBUSER,
        password=DBPASSWORD,
        database=DBDATABASE
        )

    mycursor = mydb.cursor()

    postfixLogParser = logParser(indexField,logFields,"postfixlogs")
    postfixLogParser.parseLog(args.logfile)

    logging.info("Complete logs:")
    completeLogs = postfixLogParser.getCompleteLogEntries()
    logging.info(completeLogs)

    logging.info("Incomplete logs:")
    logging.info(postfixLogParser.getIncompleteLogEntries())

    #Check if the table exists, if it doesn't create it
    #SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA='pythonlogger' AND TABLE_NAME='postfixlogs';

    sqlTableCheckQuery = f"SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA='{DBDATABASE}' AND TABLE_NAME='{postfixLogParser.logName}';"
    mycursor.execute(sqlTableCheckQuery)
    if mycursor.fetchone()[0] == 1:
        logging.info("Table already exists.")
    else:
        logging.info("Log DB table does not exist, creating it.")
        sqlTableCreationQuery = f"CREATE TABLE {postfixLogParser.logName} ("
        sqlTableCreationQuery += f"{postfixLogParser.identifierField.name} {postfixLogParser.identifierField.sqlType} NOT NULL"
        for logFieldEntry in postfixLogParser.logFields:
            sqlTableCreationQuery +=f", {logFieldEntry.name} {logFieldEntry.sqlType}  NOT NULL"
        sqlTableCreationQuery += f", PRIMARY KEY ({postfixLogParser.identifierField.name}));"
        mycursor.execute(sqlTableCreationQuery)


    #Insert the complete log entries into the database
    #Build up the SQL insert query string that will be re-used on each insert
    sqlQuery = f"INSERT INTO {postfixLogParser.logName} ({postfixLogParser.identifierField.name}"

    for logFieldEntry in postfixLogParser.logFields:
        sqlQuery += f", {logFieldEntry.name}"
    sqlQuery += ") VALUES (%s"

    for logFieldEntry in postfixLogParser.logFields:
        sqlQuery += f", %s"
    sqlQuery += ")"
    logging.info(sqlQuery)

    for log in completeLogs:
        val = [log.fields[postfixLogParser.identifierField.name]]
        for logFieldEntry in postfixLogParser.logFields:
            val.append(log.fields[logFieldEntry.name])
        #There is probably a better way to handle this then catching the error and doing nothing
        #Look into this when optimising the program
        try:
            mycursor.execute(sqlQuery, val)
            mydb.commit()
        except Exception as e:
            logging.error(e)
    
    end = time.perf_counter()
    print(f"Time taken: {end - start:.6f} seconds")

if __name__ == '__main__':
    main()