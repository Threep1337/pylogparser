# Python log parser

This program is a log parser for processing Postfix logs (and maybe be generic enough to process other logs).  The goal will be to be able to take raw logs that are created by Postfix and process them in a way to extract information about sent messages.  Each message should have the following information included with it:

- Message ID
- Time
- Sender
- Recipient
- Subject
- Status
- Mail server hostname

Since processing the logs every time from the raw text will be inefficient, I would like to add functionality to ingest the logs into a database so that they can be searched very quickly, without having to parse the log files every time a search is performed.

I have included some sample date in the "sampleLogs" directory, I should add more sample logs as the project evolves to make sure I can get all of the required information.

My first goal for the project should be simple, all I should try and do at first is extract the message information from the raw log file and display it.  I should create a logLine class I think to represent the log lines parsed from the file.  At first the extraction logic should be static and hardcoded, maybe as another goal I could make it more generic and have the parsing logic in a config file or something.