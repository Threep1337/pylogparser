import re
import logging
from logEntry import logEntry
class logParser:

    def __init__(self,identifierField,logFields):
        self.identifierField = identifierField
        self.logFields = logFields

        #Dictionary of log entries, the identifierField is the key, the value will be a logEntry class instance
        self.logEntries = {}

    def __repr__(self):
        return "to fill"
    
    def parseLog(self,logFile):
        #change this to go line by line later
        with open(logFile) as f:
           for line in f:

                logIdentifier = None
                logIdentifierSearch = re.search(self.identifierField.captureRegex,line)

                if logIdentifierSearch:
                    logIdentifier=logIdentifierSearch.group(0)
                    
                    #Create a log entry for the identifier if it doesn't exist
                    if not logIdentifier in self.logEntries:
                        self.logEntries[logIdentifier] = logEntry({self.identifierField.name:logIdentifier})

                    for logField in self.logFields:
                        logging.info(f"Searching for field {logField.name}")

                        #Skip searching for the field if the entry already has a value, more efficient
                        if not logField.name in self.logEntries[logIdentifier].fields:
                            logFieldSearch = re.search(logField.captureRegex,line)

                            if logFieldSearch:
                                logFieldValue=logFieldSearch.group(logField.regexMatchGroup)
                                logging.info(f"found log field value {logField}")
                                self.logEntries[logIdentifier].fields[logField.name] = logFieldValue
                        else:
                            logging.info(f"Skipping searching for field {logField.name}, a value already exists.")
        #print(self.logEntries)

    def getIncompleteLogEntries(self):

        #Build up a list of incomplete log entries
        incompleteLogs =[]

        #Get all of the valid field names

        field_names = [field.name for field in self.logFields]

        for parsedLogEntry in self.logEntries.values():
            logging.info(f"working on parded log entry {parsedLogEntry}")

            #Check if the log entry object has all of the fields set, by definition the identifier field has to be set
            #so that doesn't need to be checked
            for logFieldName in field_names:
                logging.info(f"checking if {logFieldName} is in {parsedLogEntry.fields}")
                if not logFieldName in parsedLogEntry.fields:
                    logging.info(f"could not find {logFieldName} in {parsedLogEntry.fields}, marking as an incomplete log entry.")
                    incompleteLogs.append(parsedLogEntry)
                    break
        return incompleteLogs


    def getCompleteLogEntries(self):
        completeLogs =[]

        field_names = [field.name for field in self.logFields]

        for parsedLogEntry in self.logEntries.values():
            #Check if the log entry object has all of the fields set, by definition the identifier field has to be set
            #so that doesn't need to be checked
            logIsComplete = True
            for logFieldName in field_names:
                if not logFieldName in parsedLogEntry.fields:
                    logIsComplete = False
                    break
            if logIsComplete:
                completeLogs.append(parsedLogEntry)

        return completeLogs
        

def main():
    entry = logParser()
    print(entry)

if __name__ == '__main__':
    main()
        
