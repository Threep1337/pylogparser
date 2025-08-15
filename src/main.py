
# Replace this with argparse later
# https://www.geeksforgeeks.org/python/command-line-arguments-in-python/
import sys

# First goal is to just extract text from the log file and print out log lines
# Worry about making it more complex afterwards
# I think I will need to use regular expressions to extract the fields from the log lines.
# I will also need to take arguments into the script call that point to the file
# Later on I can deal with ingesting the logs into a database.


def main():
    if len(sys.argv) < 2:
        print ("Usage: python main.py logfile")
        sys.exit
    
    print(f"Going to open {sys.argv[1]}")
    with open(sys.argv[1]) as f:
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