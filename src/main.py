
# Replace this with argparse later
# https://www.geeksforgeeks.org/python/command-line-arguments-in-python/
import sys
import argparse

# First goal is to just extract text from the log file and print out log lines
# Worry about making it more complex afterwards
# I think I will need to use regular expressions to extract the fields from the log lines.
# I will also need to take arguments into the script call that point to the file
# Later on I can deal with ingesting the logs into a database.


# First basic goal should be to parse a file containing only one message, and create a list of objects that represent entries

def main():

    msg = "Python Postfix log parser"

    parser = argparse.ArgumentParser(description=msg)

    parser.add_argument("-l", "--Logfile", help = "Path to the log file to parse")
    args = parser.parse_args()


    if args.Logfile:
        print(f"the passed in log file is {args.Logfile}")
    
    with open(args.Logfile) as f:
        file_contents = f.read()
        f.close()
    #print(f"{file_contents}")
    lines = file_contents.splitlines()

    x=0
    for line in lines:
        x+=1
        print(f"line {x}:{line}")



if __name__ == '__main__':
    main()