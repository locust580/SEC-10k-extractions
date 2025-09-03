Extracts past data from SEC 10-k filings to create CSVs for:
- Income Statements
- Balance Sheets
- Cash Flows

These CSV files can be easily copied into an excel spreadsheet for analysis: 
- Use "Split Text to Columns" under "Data"
- Split by commas
- You're golden

In the folder is 5 example SEC reports that I've been testing on.
If a value comes up Null or NaN or something wack, it probably wasn't found in the xbrl tags:
- Go to the SEC filing where the value was missing
- Go to Part II, Item 8
- Look through financials to find value
- Copy value and Ctrl + F through the xml file (usually ticker-YYYYMMDD-htm.xml) for value
- Copy XBRL tag and paste into corresponding value in the dictionary where missing
