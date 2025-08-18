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
        incompleteLogs =[]
        for value in self.logEntries.values():
            #Check if the log entry object has all of the fields set, by definition the identifier field has to be set
            #so that doesn't need to be checked

            for key in self.logFields:
                if not key in value.fields:
                    incompleteLogs.append(value)
                    break
        return incompleteLogs


    def getCompleteLogEntries(self):
        completeLogs =[]
        for value in self.logEntries.values():
            #Check if the log entry object has all of the fields set, by definition the identifier field has to be set
            #so that doesn't need to be checked

            for key in self.logFields:
                if not key in value.fields:
                    break
            completeLogs.append(value)
        return completeLogs
        

def main():
    entry = logParser()
    print(entry)

if __name__ == '__main__':
    main()
        
