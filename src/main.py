import argparse
import logging
from dotenv import load_dotenv
import os
import time
from logField import logField
from logParser import logParser
from logDefinition import logDefinition
from logSearcher import logSearcher
from logDB import logDatabase
import json
from tabulate import tabulate
# TODO
# Remove the hardcoded db table name from logSearcher
# Make the search results more compact my default
# Put examples in the commands and better help
# See if there is a better way to package this
# See if I can compile the regexes for better performance
# Compact output should include MessageID, Date, Sender, Recipient, Status, Subject


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
    LOGCONFIGJSON=os.getenv("LOGCONFIGJSON")

    #Create argument parser with a message
    msg = "Python log parser.  This program can parse a log file and ingest it into a database." \
    "The fields to ingest are configurable in the logConfig.json file.  The program can also be used to search through the log entries that are in the log database."

    parser = argparse.ArgumentParser(
        description=msg,
        epilog="""Examples:
  python main.py ingestLogs /tmp/SampleLogs.txt
  python main.py ingestLogs /tmp/SampleLogs.txt /tmp/SampleLogs2.txt
  python main.py search "sender -like '%someone%'"
  python main.py search "sender -eq 'someoneelse@mailrelay.onmicrosoft.com'"
  python main.py query "select * from postfixlogs"
  python main.py purge
""")

    #Global arguments
    parser.add_argument("-v","--verbose",help= "Set the verbosity level",action="count",default=0)
    parser.add_argument("-t","--time",help= "Flag to measure the runtime.",action="store_true")

    #Make the command use subcommandss
    #Add subcommands to the script
    subparsers = parser.add_subparsers(title="subcommands",dest="command",required=True,)

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
    
    args = parser.parse_args()

    if args.time:
        start = time.perf_counter()

    if args.verbose > 0:
        logging.basicConfig(level=logging.DEBUG)
    
    # Open the JSON file
    with open(LOGCONFIGJSON, "r") as configFile:
        # Load its contents into a Python object
        data = json.load(configFile)

    logName = data["logName"]
    indexField = logField(data["indexField"]["name"],data["indexField"]["captureRegex"],data["indexField"]["sqlType"],data["indexField"]["regexMatchGroup"],data["indexField"]["displayInShortOutput"])
    logFields =[]
    for configLogField in data["logFields"]:
        logFields.append(logField(configLogField["name"],configLogField["captureRegex"],configLogField["sqlType"],configLogField["regexMatchGroup"],configLogField["displayInShortOutput"]))

    #Create a log definition that will be used by the parser
    logToParseDefinition = logDefinition(logName,indexField,logFields)
    logDB = logDatabase(DBHOST,DBUSER,DBPASSWORD,DBDATABASE,logToParseDefinition)

    #I should use the logDefinition in any reference that creates fields etc, not the log parse references
    if args.command == "ingestLogs":
        logging.info("Starting log ingestion")

        if args.time:
            now = time.perf_counter()
            print(f"Start of log ingestion: {now - start:.6f} seconds")

        postfixLogParser = logParser(logToParseDefinition.identifierField,logToParseDefinition.otherFields,logToParseDefinition.logName)

        for file in args.files:
            print (f"Parsing log file: {file}")
            postfixLogParser.parseLog(file)
            print (f"Finished parsing log file: {file}")

        if args.time:
            now = time.perf_counter()
            print(f"end of log parsing: {now - start:.6f} seconds")

        logging.info("Complete logs:")
        completeLogs = postfixLogParser.getCompleteLogEntries()
        logging.info(completeLogs)

        logging.info("Incomplete logs:")
        logging.info(postfixLogParser.getIncompleteLogEntries())

        if args.time:
            now = time.perf_counter()
            print(f"Start of DB inserts: {now - start:.6f} seconds")

        logDB.writeLogsToDB(completeLogs)

    if args.command == "search":
        logging.info("Starting a search")
        myLogSearcher = logSearcher(logToParseDefinition)
        searchQuery = myLogSearcher.search(args.searchExpression, True)
        logging.info(f"Search query is {searchQuery}")
        myresult, mydescriptors = logDB.executeLogQuery(searchQuery)

        # Get column names for nice headers
        headers = [description[0] for description in mydescriptors]

        # Display results in a table
        print(tabulate(myresult, headers=headers, tablefmt="github"))
    
    if args.command == "query":
        logging.info("Querying the logs")
        myresult = logDB.executeLogQuery(args.queryString)
        for x in myresult:
            print(x)

    if args.command == "purge":
        logging.info("purging logs")
        logDB.purgeLogs()

    if args.time:
        now = time.perf_counter()
        print(f"End of program: {now - start:.6f} seconds")

if __name__ == '__main__':
    main()