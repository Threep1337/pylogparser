
class logEntry:

    def __init__(self,fields = {}):
        self.fields=fields

    def __repr__(self):
        return f"{self.fields}"

def main():
    entry = logEntry()
    print(entry)

if __name__ == '__main__':
    main()
        
