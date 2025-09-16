

#I could modify this class so that there are multiple ways to capture a field, regex or split logic for example
class logField:

    def __init__(self,name,captureRegex,sqlType,regexMatchGroup=0,displayInShortOutput=False):
        self.name = name
        self.captureRegex = captureRegex
        self.regexMatchGroup = regexMatchGroup
        self.sqlType = sqlType
        self.displayInShortOutput = displayInShortOutput

def main():
    entry = logField()
    print(entry)

if __name__ == '__main__':
    main()
        
