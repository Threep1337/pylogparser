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
    parser.add_argument("-s","--search",help= "Search the log entries")
    parser.add_argument("-q","--query",help= "Query the log entries")
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

    if args.logfile:
        logging.info("Starting log ingestion")
        end = time.perf_counter()
        print(f"Time taken: {end - start:.6f} seconds")
        postfixLogParser = logParser(indexField,logFields,"postfixlogs")
        postfixLogParser.parseLog(args.logfile)

        end = time.perf_counter()
        print(f"Time AFTER PARSELOG taken: {end - start:.6f} seconds")

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
        end = time.perf_counter()
        print(f"Time taken: {end - start:.6f} seconds")

        for logFieldEntry in postfixLogParser.logFields:
            sqlQuery += f", {logFieldEntry.name}"
        sqlQuery += ") VALUES (%s"

        for logFieldEntry in postfixLogParser.logFields:
            sqlQuery += f", %s"
        sqlQuery += ")"
        logging.info(sqlQuery)


        #Since I know the number of log records and how many fields in each log, I could pre-allocate array sizes:
        #     n = 1000
        #       arr = [None] * n  # or [0] * n if numbers
        #
        #     rows = 1000
        # cols = 5
        # arr = [[None] * cols for _ in range(rows)]

        # for r in range(rows):
        # arr[r][0] = r            # int
        # arr[r][1] = str(r)       # str
        # arr[r][2] = r * 0.5      # float
        # arr[r][3] = {"id": r}    # dict
        # arr[r][4] = None         # placeholder

        end = time.perf_counter()
        print(f"Time taken: {end - start:.6f} seconds")

        if len(completeLogs) > 0:
            logRecords=[None] * len(completeLogs)

            x=0
            for log in completeLogs:
                #This doesnt need to be calculated every time
                val = [None] * (len(log.fields))
                val[0] = log.fields[postfixLogParser.identifierField.name]
                
                y=1
                for logFieldEntry in postfixLogParser.logFields:
                    val[y] = log.fields[logFieldEntry.name]
                    y+=1
                #print(f"val is {val}")
                logRecords[x]=val
                x+=1

            try:
                #print ("HERE")
                #print(len(logRecords))
                #print(logRecords[0])
                mycursor.executemany(sqlQuery, logRecords)
                mydb.commit()
            except Exception as e:
                logging.error(e)
        # if len(completeLogs) > 0:
    #     logRecords=[]
    #     for log in completeLogs:
    #         val = [log.fields[postfixLogParser.identifierField.name]]
    #         for logFieldEntry in postfixLogParser.logFields:
    #             val.append(log.fields[logFieldEntry.name])
    #         logRecords.append(val)

    #     try:
    #         mycursor.executemany(sqlQuery, logRecords)
    #         mydb.commit()
    #     except Exception as e:
    #         logging.error(e)
    
    if args.search:
        logging.info("Starting a search")
        # Build up a SQL query based on the search string passed in
        # Search strings should be of the format "field -operator value"
        # So for example "sender -eq 'someoneelse@mailrelay.onmicrosoft.com'"
        strippedSearchString = args.search.strip()

        #Validate its format
        #convert to SQL query

        #Get each token in the string, initially just have a single one that turn that into a query
        #Maybe I should make a new class to handle constructing the search query
        tokens = strippedSearchString.split(" ")
        
        field = tokens[0]
        operator = tokens[1]
        value = tokens[2]
        #-s "sender -eq someoneelse@mailrelay.onmicrosoft.com"
        logging.info(f"\nfield: {field}\noperator: {operator}\nvalue: {value}")

        #The table name shouldn't be hardcoded like this, need to think of how to re-factor previous code
        #Either the parser object needs to be present, or I need to think of a better way to have it defined if a non
        #parsing run is being performed
        searchQuery = f"SELECT * FROM postfixlogs WHERE {field}"

        #Add more operators here, and I should fail out if its not a valid one
        match operator:
            case "-eq":
                print ("equals")
                searchQuery += " = "
            case _:
                print ("default")

        searchQuery += f"{value}"
        # A valid query is 
        # SELECT * FROM postfixlogs WHERE sender = 'someoneelse@mailrelay.onmicrosoft.com';
        logging.info(f"Search query is {searchQuery}")

        mycursor.execute(searchQuery)
        # I should print the number of records found, and have a message if no results were found
        myresult = mycursor.fetchall()
        for x in myresult:
            print(x)

        
    if args.query:
        logging.info("Querying the logs")
        mycursor.execute(args.query)
        myresult = mycursor.fetchall()

        for x in myresult:
            print(x)


    
    end = time.perf_counter()
    print(f"Time taken: {end - start:.6f} seconds")

if __name__ == '__main__':
    main()