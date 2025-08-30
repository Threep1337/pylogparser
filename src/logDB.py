from logDefinition import logDefinition
import mysql.connector
import logging
#Class to interact with log database
class logDatabase:

    def __init__(self,host,user,password,database,logToParseDefinition):
        self.host=host
        self.user = user
        self.password = password
        self.database = database
        self.logToParseDefinition = logToParseDefinition
        self.mycursor = None
        self.mydb = None
        self.connect()
        self.checkIfLogTableExists()

    def connect(self):

        self.mydb = mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database
            )
        self.mycursor = self.mydb.cursor()

    def executeLogQuery(self,query):
        self.mycursor.execute(query)
        return self.mycursor.fetchall()

    def checkIfLogTableExists(self):

        sqlTableCheckQuery = f"SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA='{self.database}' AND TABLE_NAME='{self.logToParseDefinition.logName}';"
        self.mycursor.execute(sqlTableCheckQuery)
        if self.mycursor.fetchone()[0] == 1:
            logging.info("Table already exists.")
        else:
            logging.info("Log DB table does not exist, creating it.")
            sqlTableCreationQuery = f"CREATE TABLE {self.logToParseDefinition.logName} ("
            sqlTableCreationQuery += f"{self.logToParseDefinition.identifierField.name} {self.logToParseDefinition.identifierField.sqlType} NOT NULL"
            for logFieldEntry in self.logToParseDefinition.otherFields:
                sqlTableCreationQuery +=f", {logFieldEntry.name} {logFieldEntry.sqlType}  NOT NULL"
            sqlTableCreationQuery += f", PRIMARY KEY ({self.logToParseDefinition.identifierField.name}));"
            self.mycursor.execute(sqlTableCreationQuery)
        pass
    def purgeLogs(self):
        sqlQuery = f"DELETE FROM {self.logToParseDefinition.logName}"
        try:
            self.mycursor.execute(sqlQuery)
            self.mydb.commit()
        except Exception as e:
            logging.error(e)

    def writeLogsToDB(self,logEntries):
        #Insert the complete log entries into the database
        #Build up the SQL insert query string that will be re-used on each insert
        sqlQuery = f"INSERT IGNORE INTO {self.logToParseDefinition.logName} ({self.logToParseDefinition.identifierField.name}"

        sqlQueryFieldstring=""
        sqlQueryValuestring=""
        for logFieldEntry in self.logToParseDefinition.otherFields:
            sqlQueryFieldstring += f", {logFieldEntry.name}"
            sqlQueryValuestring += f", %s"
        sqlQuery += f"{sqlQueryFieldstring}) VALUES (%s{sqlQueryValuestring})"
        logging.info(sqlQuery)

        if len(logEntries) > 0:
            logRecords=[]
            for log in logEntries:
                val = [log.fields[self.logToParseDefinition.identifierField.name]]
                for logFieldEntry in self.logToParseDefinition.otherFields:
                    val.append(log.fields[logFieldEntry.name])
                logRecords.append(val)

            try:
                self.mycursor.executemany(sqlQuery, logRecords)
                self.mydb.commit()
            except Exception as e:
                logging.error(e)


def main():
    pass

if __name__ == '__main__':
    main()