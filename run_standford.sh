TT=${1:-"WARC-Record-ID"}
INFILE=${2:- "hdfs:///user/bbkruit/CC-MAIN-20160924173739-00000-ip-10-143-35-109.ec2.internal.warc.gz"}

DATE=`date '+%Y_%m_%d_%H_%M_%S'`
OUTFILE=${3:-"Output_$DATE"}
DRIVER_PROGRAM=entity_linking_standford.py


echo "Start driver program =============> Output: $DATE"

spark-submit --conf spark.yarn.appMasterEnv.PYSPARK_PYTHON=./NLTK/nltk_env/bin/python --conf spark.yarn.appMasterEnv.NLTK_DATA=./ --master yarn-cluster --num-executors 16 --executor-cores 4  --executor-memory 4G  --files english.all.3class.distsim.crf.ser.gz,english-left3words-distsim.tagger,stanford-ner.jar,stanford-postagger-3.8.0.jar --py-files dependencies02.zip  --archives nltk_env.zip#NLTK,tokenizers.zip#tokenizers,taggers.zip#taggers,chunkers.zip#chunkers --conf spark.yarn.maxAppAttempts=1 $DRIVER_PROGRAM $ATT $INFILE $OUTFILE

echo "End driver program ================"
