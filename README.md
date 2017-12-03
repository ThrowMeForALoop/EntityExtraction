# EntityExtraction
Team project (Group 5) for extracting entities and their links

To run entirely your project, please use the following commands:

Come to your source directory:

		 cd FinalProject/

1) If you want to test with small group of data (take(10)), please use command below:

		./runnable_take10.sh

Run entirely  application with Standford Stack:

		./run_standford.sh (This script will run your application in yarn cluster and use StandfordNER.jar to find entities => slower but more accurate than nltk chunk)

Or Run application with Nltk module (similar function to Standford Stack):

		./run_nltk.sh



*** NOTE ***:
- The default input for run script is the WARC Record Id and hdfs input file, which were mentioned by TA.

- The output will be written to default folder in hdfs. Please see log in run script to get the output directory which is named by current date

- If you want to change WARC Record ID and Hdfs input file and output file,  please use command below:

		./run_standford.sh "WARC_Recrod_Id" "Hdfs file path" "Output Directory"

- To view the output, please use commands below:

  	hdfs dfs -ls "Output Directory"

		hdfs dfs -cat "File in output directory"


Thannks - Regards,

