These are the instructions to execute the SentenceQuery Program.

In order to execute queries, run the python program './FinalProgramDemo' (from the directory: '/var/scratch/wdps1705/felipe' on DAS).

After that you can submit queries (please refer to the sample queries in the file 'demo_tests' in the same directory as the python program)

The results will be shown after hitting <enter>, under the section: 'Final result set (after applying logical operators):'

Example Query:
SELECT * WHERE PERSON = "John" AND PERSON "work" ORGANIZATION AND ORGANIZATION = "Microsoft" OR GPE = "Brazil"

Results (given the reduced set of sample sentences - please refer to the set in the  python program):
['Richard goes to Brazil for vacations every year but he lives in Seatle.', 'John works at Microsoft which is located in San Francisco in United States.', 'John works at Microsoft which is located in Amsterdam capital of Netherlands.']