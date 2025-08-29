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
from logDefinition import logDefinition
from logSearcher import logSearcher

# Next steps:
# Put all of the DB code in its own class and get it out of main
# Make the log field defintion be a config json file rather than hardcoded in main
# Add a unit test that takes a known input text source and makes sure the created logentries match it
# General polish and re-factoring is needed
# Add better error checking and error handling


# Classes in project and uses
# logParser: Performs parsing against a log file and returns a list of logEntry objects
# logEntry: Represents an individial log entry, does not contain any info on how to parse a log
# logField: Represents the definition of a log field that exists in a log, how it can be parsed, and what SQL type it should be. I might rename the class logFieldDefinition or something
# logDefinition: Represents the definition of a log file, specifying what the name of the log type is, what its identifier field is, and what other fields exist in it.
# logSearcher: Validates that the query or search string is valid and then executes a seearch against a logDB
# logDB: Represents a log database, connects to the DB and validates that the DB exists and is valid, and has logic to create the DB if not.  Requires a logDefintion.


def main():

    
    # Loads variables from .env into os.environ
    load_dotenv()
    DBHOST=os.getenv("DBHOST")
    DBUSER=os.getenv("DBUSER")
    DBPASSWORD=os.getenv("DBPASSWORD")
    DBDATABASE=os.getenv("DBDATABASE")

    #Create argument parser with a message
    msg = "Python log parser.  This program can ingest logs into a database for searching."
    parser = argparse.ArgumentParser(description=msg)

    #Global arguments
    parser.add_argument("-v","--verbose",help= "Set the verbosity level",action="count",default=0)
    parser.add_argument("-t","--time",help= "Flag to measure the runtime.",action="store_true")

    #Make the command use subcommandss
    #Add subcommands to the script
    subparsers = parser.add_subparsers(title="subcommands",dest="command",required=True)

    #Subcommand ingestLogs
    ingestLogsParser = subparsers.add_parser("ingestLogs", help="Ingest logs into the database")
    ingestLogsParser.add_argument("files",nargs="+", help="Log files to parse and ingest to the database")

    #Subcommand search
    searchParser = subparsers.add_parser("search", help="Search the logs using a search expression")
    searchParser.add_argument("searchExpression",help="Search expression to run")

    #Subcommand query
    queryParser = subparsers.add_parser("query", help="Run a direct query against the log DB")
    queryParser.add_argument("queryString",help="The Query string to run")

    #Subcommand purge
    purgeParser = subparsers.add_parser("purge", help="purge logs into the database")
    # purgeParser.add_argument("files",nargs="+", help="Log files to parse and ingest to the database")
    
    args = parser.parse_args()

    if args.time:
        start = time.perf_counter()

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

    #Create a log definition that will be used by the parser
    logToParseDefinition = logDefinition("postfixlogs",indexField,logFields)

    # Connect to the SQL Instance holding the logs
    mydb = mysql.connector.connect(
        host=DBHOST,
        user=DBUSER,
        password=DBPASSWORD,
        database=DBDATABASE
        )

    mycursor = mydb.cursor()

    #I should use the logDefinition in any reference that creates fields etc, not the log parse references
    if args.command == "ingestLogs":
        logging.info("Starting log ingestion")

        if args.time:
            now = time.perf_counter()
            print(f"Start of log ingestion: {now - start:.6f} seconds")

        postfixLogParser = logParser(logToParseDefinition.identifierField,logToParseDefinition.otherFields,logToParseDefinition.logName)

        for file in args.files:
            print (f"working on {file}")
            postfixLogParser.parseLog(file)

        if args.time:
            now = time.perf_counter()
            print(f"end of log parsing: {now - start:.6f} seconds")

        logging.info("Complete logs:")
        completeLogs = postfixLogParser.getCompleteLogEntries()
        logging.info(completeLogs)

        logging.info("Incomplete logs:")
        logging.info(postfixLogParser.getIncompleteLogEntries())

        #This should be put into another class (logDB) it should have a function like CreateInsertQuery or something that takes a logDefinition.
        #Check if the table exists, if it doesn't create it
        sqlTableCheckQuery = f"SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA='{DBDATABASE}' AND TABLE_NAME='{logToParseDefinition.logName}';"
        mycursor.execute(sqlTableCheckQuery)
        if mycursor.fetchone()[0] == 1:
            logging.info("Table already exists.")
        else:
            logging.info("Log DB table does not exist, creating it.")
            sqlTableCreationQuery = f"CREATE TABLE {logToParseDefinition.logName} ("
            sqlTableCreationQuery += f"{logToParseDefinition.identifierField.name} {logToParseDefinition.identifierField.sqlType} NOT NULL"
            for logFieldEntry in logToParseDefinition.otherFields:
                sqlTableCreationQuery +=f", {logFieldEntry.name} {logFieldEntry.sqlType}  NOT NULL"
            sqlTableCreationQuery += f", PRIMARY KEY ({logToParseDefinition.identifierField.name}));"
            mycursor.execute(sqlTableCreationQuery)

        #Insert the complete log entries into the database
        #Build up the SQL insert query string that will be re-used on each insert
        sqlQuery = f"INSERT IGNORE INTO {logToParseDefinition.logName} ({logToParseDefinition.identifierField.name}"

        if args.time:
            now = time.perf_counter()
            print(f"Start of DB inserts: {now - start:.6f} seconds")

        for logFieldEntry in logToParseDefinition.otherFields:
            sqlQuery += f", {logFieldEntry.name}"
        sqlQuery += ") VALUES (%s"

        for logFieldEntry in logToParseDefinition.otherFields:
            sqlQuery += f", %s"
        sqlQuery += ")"
        logging.info(sqlQuery)

        
        if len(completeLogs) > 0:
            logRecords=[]
            for log in completeLogs:
                val = [log.fields[logToParseDefinition.identifierField.name]]
                for logFieldEntry in logToParseDefinition.otherFields:
                    val.append(log.fields[logFieldEntry.name])
                logRecords.append(val)

            try:
                mycursor.executemany(sqlQuery, logRecords)
                mydb.commit()
            except Exception as e:
                logging.error(e)
    
    if args.command == "search":
        logging.info("Starting a search")
        # Build up a SQL query based on the search string passed in
        # Search strings should be of the format "field -operator value"
        # So for example "sender -eq 'someoneelse@mailrelay.onmicrosoft.com'"

        myLogSearcher = logSearcher(logToParseDefinition)
        searchQuery = myLogSearcher.search(args.searchExpression)

        logging.info(f"Search query is {searchQuery}")

        mycursor.execute(searchQuery)

        # I should print the number of records found, and have a message if no results were found
        myresult = mycursor.fetchall()
        for x in myresult:
            print(x)
    
    if args.command == "query":
        logging.info("Querying the logs")
        mycursor.execute(args.query)
        myresult = mycursor.fetchall()

        for x in myresult:
            print(x)
    
    if args.command == "purge":
        logging.info("purging logs")


    if args.time:
        now = time.perf_counter()
        print(f"End of program: {now - start:.6f} seconds")

if __name__ == '__main__':
    main()