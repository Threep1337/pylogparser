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
# Search can be based on a text filter, "sender -eq 'example@test.com' or a raw SQL query", a different flag for each case
# Make the log field defintion be a config json file rather than hardcoded in main
# Add a unit test that takes a known input text source and makes sure the created logentries match it
# General polish and re-factoring is needed, the code and names are getting ugly
# Add better error checking and error handling



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
    sqlQuery = f"INSERT IGNORE INTO {postfixLogParser.logName} ({postfixLogParser.identifierField.name}"

    for logFieldEntry in postfixLogParser.logFields:
        sqlQuery += f", {logFieldEntry.name}"
    sqlQuery += ") VALUES (%s"

    for logFieldEntry in postfixLogParser.logFields:
        sqlQuery += f", %s"
    sqlQuery += ")"
    logging.info(sqlQuery)

    if len(completeLogs) > 0:
        logRecords=[]
        for log in completeLogs:
            val = [log.fields[postfixLogParser.identifierField.name]]
            for logFieldEntry in postfixLogParser.logFields:
                val.append(log.fields[logFieldEntry.name])
            logRecords.append(val)

        try:
            mycursor.executemany(sqlQuery, logRecords)
            mydb.commit()
        except Exception as e:
            logging.error(e)
    
    end = time.perf_counter()
    print(f"Time taken: {end - start:.6f} seconds")

if __name__ == '__main__':
    main()