
#This class defines the a log and how it can be parsed, and its SQL field types
#A way of loading log definitions should be by passing it a JSON file
class logDefinition:

    def __init__(self,logName,identifierField,otherFields):

        self.logName = logName
        self.identifierField = identifierField
        self.otherFields = otherFields





def main():
    #entry = logParser()
    #print(entry)
    pass

if __name__ == '__main__':
    main()
        
