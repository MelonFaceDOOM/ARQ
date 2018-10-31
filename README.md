# ARQ
Python code used for cleaning loss and theft/seizure data

Losses and Thefts
At the time of the 2017 ARQ, CSPS (the source for loss and theft data) did not include Cannabis. Therefore, cannabis losses and thefts were extracted from the CDSD. The ARQ includes forgery data as well, which isn’t part of CSPS, so forgeries were also extracted from the CDSD. Cannabis losses and thefts, as well as forgeries, were then combined with the rest of the CSPS loss and theft data.

Summary of steps:
1)	Extract Cannabis losses and thefts from CDSD
2)	Extract Forgeries from CDSD
3)	Request Loss and Theft data from CSPS (confirm that forgeries and cannabis are still not included, since this may change for next year)
4)	Merge
5)	Clean
6)	Analyse


Seizures
Seizure data was extracted from CDSD. All RCMP data was deleted, and then replaced with a more up-to-date submission obtained directly from the RMCP. This is a necessary step because of the protocol involved in the RCMP submitting data into CDSD. The data they store in their own records is not subject to the same protocol delays and is therefore a better source, especially since the ARQ deals with such recent data.

Summary of steps:
1)	Extract seizure data from CDSD
2)	Delete RCMP cases from extracted data
3)	Request seizure data directly from RCMP (for 2017, this was requested on May 15 and submitted on August 1st, to give an idea of the expected delay). 
4)	Merge and analyze


How to access data sources
See HC network drive file
