from logDefinition import logDefinition
import logging
#Class to search through logs
#It should take either a direct SQL query and validate that the query is OK to run and then do it
#Or take a search string and turn it into a query and execute it
class logSearcher:

    #the log defintion is needed by this class so that it can validate search fields
    def __init__(self,logDefinition,dbTableName):
        self.logDefinition = logDefinition
        self.dbTableName = dbTableName
        pass

    #The search string should be checked and string values should be padded with quotes
    def search(self,searchString):

        # Clean white space off the string
        searchString = searchString.strip()
        tokens = searchString.split(" ")

        field = tokens[0]
        operator = tokens[1]
        value = tokens[2]
        logging.info(f"\nfield: {field}\noperator: {operator}\nvalue: {value}")

        #The table name shouldn't be hardcoded like this, need to think of how to re-factor previous code
        #Either the parser object needs to be present, or I need to think of a better way to have it defined if a non
        #parsing run is being performed
        searchQuery = f"SELECT * FROM {self.dbTableName} WHERE {field}"


        # Build up a SQL query based on the search string passed in
        # Search strings should be of the format "field -operator value"
        # So for example "sender -eq 'someoneelse@mailrelay.onmicrosoft.com'"
        match operator:
            case "-eq":
                print ("equals")
                searchQuery += " = "
            case "-gt":
                print ("greater than")
                searchQuery += " > "
            case "-lt":
                print ("less than")
                searchQuery += " < "
            case "-ge":
                print ("greater than or equal to")
                searchQuery += " >= "
            case "-le":
                print ("less than or equal to")
                searchQuery += " <= "
            case "-ne":
                print ("not equal")
                searchQuery += " <> "
            case "-like":
                print ("like")
                searchQuery += " LIKE "
            case _:
                print ("default")

        searchQuery += f"{value}"

        logging.info(f"Search query is {searchQuery}")
        return searchQuery

def main():
    pass

if __name__ == '__main__':
    main()