
class logField:

    def __init__(self,name,captureRegex,sqlType,regexMatchGroup=0):
        self.name = name
        self.captureRegex = captureRegex
        self.regexMatchGroup = regexMatchGroup
        self.sqlType = sqlType
    

def main():
    entry = logField()
    print(entry)

if __name__ == '__main__':
    main()
        
