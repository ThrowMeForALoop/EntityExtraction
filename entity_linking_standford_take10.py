from pyspark import SparkContext
import sys
import os
import collections
from bs4 import BeautifulSoup
from bs4.element import Comment
import urllib
#from lxml.html import html5parser
import nltk
from nltk.tag import StanfordNERTagger
from nltk.tokenize.stanford import StanfordTokenizer
from nltk.tag.stanford import StanfordPOSTagger
from nltk.tokenize import sent_tokenize
import requests
import json, re
import math

from pyspark.files import SparkFiles
#nltk.data.path.append("hdfs:///user/wdps1705/nltk_data/")

#sc = SparkContext("local", "wdps1705")
sc = SparkContext("yarn", "wdps1705")

record_attribute = sys.argv[1]
in_file = sys.argv[2]

rdd = sc.newAPIHadoopFile(in_file,
    "org.apache.hadoop.mapreduce.lib.input.TextInputFormat",
    "org.apache.hadoop.io.LongWritable",
    "org.apache.hadoop.io.Text",
    conf={"textinputformat.record.delimiter": "WARC/1.0"})

def tag_visible(element):
        if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]', 'html']:
                return False
        if isinstance(element, Comment):
                return False
        return True


def text_from_html(body):
	visible_texts= ""
	try:
        	#soup = BeautifulSoup(body,"lxml")
		soup = BeautifulSoup(body, 'html.parser')
		texts = soup.findAll(text=True)
        	visible_texts = filter(tag_visible, texts)
        	return u" ".join(t.strip() for t in visible_texts)
	except:
		print "convert html to text error"
		return u" ".join(t.strip() for t in visible_texts) 

def is_ascii(text):
    if isinstance(text, unicode):
        try:
            text.encode('ascii')
        except UnicodeEncodeError:
            return False
    else:
        try:
            text.decode('ascii')
        except UnicodeDecodeError:
            return False
    return True

#stranford stack
# I want to select the first classifier model
#stanford_classifier = SparkFiles.get("english.all.3class.distsim.crf.ser.gz")
stanford_classifier = "english.all.3class.distsim.crf.ser.gz"

# For getting the path for StanfordNERTagger
#stanford_ner_path = SparkFiles.get("stanford-ner.jar")
stanford_ner_path = "stanford-ner.jar"

# Pos tagging path
standford_pos_tagging_path = "stanford-postagger-3.8.0.jar"
standford_post_tagging_model = "english-left3words-distsim.tagger"


# Creating Tagger Object
st = StanfordNERTagger(stanford_classifier, stanford_ner_path, encoding='utf-8')
tokenizer = StanfordTokenizer(standford_pos_tagging_path, encoding='utf-8')
pos_tagger = StanfordPOSTagger(standford_post_tagging_model, standford_pos_tagging_path)

def findEntitiesInSentence(sentence):
	recognized_entities=[]
	try:
        	tokenized_text = tokenizer.tokenize(sentence)
        	recognized_entities = st.tag(tokenized_text)
		return recognized_entities
	except:
		print "findEntitiesInSentence error"
		return recognized_entities

def refineDocument(document):
        sentences = sent_tokenize(document)
        named_entities = []
	try:
       		for sentence in sentences:
        		entities_for_sentence = findEntitiesInSentence(sentence)
			if len(entities_for_sentence)==0:
				continue
                	named_entities.extend(entities_for_sentence)
        	return named_entities
	except:
		print "refineDocument error"
		return named_entities

ELASTICSEARCH_URL = 'http://10.149.0.127:9200/freebase/label/_search'
TRIDENT_URL = 'http://10.141.0.125:9001/sparql'
#TRIDENT_URL = sys.argv[3]

def find_entity_freebase_id(query):
    if is_ascii(query)==False:
	return
    print('Searching for "%s"...' % query)
    try:
    	response = requests.get(ELASTICSEARCH_URL, params={'q': query, 'size':100})
    except:
	print "send request for elastic search error"
	return []
    ids = set()
    labels = {}
    scores = {}

    if response:
        response = response.json()
        for hit in response.get('hits', {}).get('hits', []):
            freebase_id = hit.get('_source', {}).get('resource')
            label = hit.get('_source', {}).get('label')
            score = hit.get('_score', 0)

            ids.add( freebase_id )
            scores[freebase_id] = max(scores.get(freebase_id, 0), score)
            labels.setdefault(freebase_id, set()).add( label )
    else:
	return[]
    #print('Found %s results.' % len(labels))


    prefixes = """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX fbase: <http://rdf.freebase.com/ns/>
    """
    same_as_template = prefixes + """
    SELECT DISTINCT ?same WHERE {
        ?s owl:sameAs %s .
        { ?s owl:sameAs ?same .} UNION { ?same owl:sameAs ?s .}
    }
    """
    po_template = prefixes + """
    SELECT DISTINCT * WHERE {
        %s ?p ?o.
    }
    """

    print('Counting KB facts...')
    facts  = {}
    for i in ids:
	try:	
		response = requests.post(TRIDENT_URL, data={'print': False, 'query': po_template % i})
        except:
		print "send request to trident error"
		facts[i] = 1
		continue
	if response:
            response = response.json()
            n = int(response.get('stats',{}).get('nresults',0))
            #print(i, ':', n)
            sys.stdout.flush()
            facts[i] = n
	else:
	    facts[i] = 1

    def get_best(i):
        return math.log(facts[i]) * scores[i]

    #print('Best matches:')
    sorted(ids, key=get_best, reverse=True)
    ranking_list=list(ids)
    if len(ranking_list)>0:
    	return ranking_list[0].replace('fbase:','')
    else:
	return []

def find_entities_freebase_id(named_entities,record_attribute):
    	retval_list=[]
    	for i in range (0,len(named_entities)):
        	retval=[]
		if named_entities[i][1]=='LOCATION' or named_entities[i][1]=='PERSON' or named_entities[i][1]=='ORGANIZATION':
            		element=named_entities[i][0]
            		f_id=find_entity_freebase_id(element)
            		retval.append(record_attribute)
            		retval.append(element)
            		retval.append(f_id)
            		retval_list.append(retval)
	return retval_list

def find_entities(record):
        res_found=0
        html=''
        text=''
        key=''
	foundhdrstart = True
        _, payload = record
        for line in payload.splitlines():
                if line.startswith('WARC-Type: response'):
                        res_found=1
                elif line.startswith(record_attribute) and res_found==1 :
                        key = line.split(': ')[1]
                elif foundhdrstart is False and res_found==1 :
                        html+=line
                elif line.startswith('Content-Length: 0') and res_found==1 :
                        yield
                elif line.startswith('Content-Type: text/html'):
                        foundhdrstart=False
        text=text_from_html(html)
        named_entities= refineDocument(text)
        #print "------------Entities in documents: ---------------",named_entities
        #print "text is:", text.encode("utf8")
	retval= find_entities_freebase_id(named_entities,key)
        #print "retval_list is: ", retval
        yield retval

print "start-----------------------\n"
rdd_entities=rdd.flatMap(find_entities)


for x in rdd_entities.take(10):
       print x
#rdd_entities.saveAsTextFile("wdps1705_output_sample_ss_5")       

print "done------------------------\n"


# Output
# [(u'Manash', u'O'), (u'is', u'O'), (u'awesome!', u'O')]
