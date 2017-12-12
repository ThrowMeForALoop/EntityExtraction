import nltk
import os
import re
from nltk.sem.relextract import extract_rels, rtuple
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk import ne_chunk, pos_tag, word_tokenize
from pyspark import SparkContext
import sys
import collections
from bs4 import BeautifulSoup
from bs4.element import Comment
import urllib
from operator import add

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



def get_entity_type():
    named_entity=""
    choice= raw_input ("select your choice by number \n 1.Person \n 2.Organization \n 3.Location \n")
    if choice=='1':
        named_entity='PER'
    elif choice=='2':
        named_entity='ORG'
    elif choice=='3':
        named_entity='GPE'
    else:
        print "Invalid Input, try again"
    return named_entity

def get_relation_list():
    relations=[]
    while True:
        relation= raw_input('enter the regular expression for desired relation or type skip \n')
        if relation=='skip':
            return relations
        relations.append(relation)


def extract_relations(text):

            # Splitting the text in multiple sentences.
            tokenizedSentences = sent_tokenize(text)

            # For debug purposes only - Prints the different extracted sentences.
            for tokenized_sentence in tokenizedSentences:
                print ("Tokenized sentence: " + str(tokenized_sentence))

            # For each of the sentences tokenizes its words.
            listSentencesWithTokenizedWords = [word_tokenize(sentence) for sentence in tokenizedSentences]

            # Each tokenized word recieves now a tag 'part of speach'
            tagged_sentences = [nltk.tag.pos_tag(sentence) for sentence in listSentencesWithTokenizedWords]

            # List that will contain all the extracted relations
            relations = []

            # For each of the already tagged sentences the program will try to find the specfic relation
            # based on the type of NE and a given 'filling' regular expression.
            for i, tagged_sentence in enumerate(tagged_sentences):
                # Uses nltk's taggger to assign a class to the Named Entyties using already tagged words as input
                chunked_sentence = nltk.chunk.ne_chunk(tagged_sentence)

                # print("This is the content of sent after chunk:" + str(chunked_sentence) + " and this is the content of i:"+ str(i))

                for relation_type in relation_types:
                        REL_RE = re.compile('.*(%s).*'%relation_type)

                        # Extracts the relation.
                        rels = extract_rels(named_entity_1, named_entity_2, chunked_sentence, corpus='ace', pattern=REL_RE, window=10)
                        # rels = extract_rels('GPE', 'GPE', chunked_sentence, corpus='ace', pattern=REL_RE, window=10)


                        for rel in rels:
                                # print(rtuple(rel))
                                # Adds the relation to the final list of relations.
                                relations.append(rel)

            # Prints the extracted relations
            for relation in relations:
                    print("Element of final relations list: " + rtuple(relation))
            return relations

def find_main_relations(record):
    html=''
    text=''
    key=''
    foundhdrstart = True
    #force a user to enter query according this steps
    named_entity_1=""
    named_entity_2=""
    value_1=""
    value_2=""
    relation_types=[]
    while True:
        #get the first named entity
        named_entity_1=get_entity_type()
        print "here: ",named_entity_1
        if named_entity_1=="":
            named_entity_1=get_entity_type()
        #get the value of first entity
        value_1= raw_input("enter the value or type skip \n")
        if value_1=='skip':
            value_1=""
        #get the list of relatiotypes
        relation_types=get_relation_list()
        #get the second named entity
        named_entity_2=get_entity_type()
        if named_entity_2=="":
            named_entity_2=get_entity_type()
        #get the value of second entity
        value_2= raw_input("enter the value or type skip \n")
        if value_2=='skip':
            value_2=""

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
        relations=extract_relations(text)
        yield relations
        # break


print "start-----------------------------------------\n"
rdd_rels=rdd.flatMap(find_main_relations)
print "done------------------------------------------\n"

