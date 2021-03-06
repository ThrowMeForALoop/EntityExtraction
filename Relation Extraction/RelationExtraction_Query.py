#!/usr/bin/python

# -*- coding: utf-8 -*-

import nltk
import os
import re
from nltk.sem.relextract import extract_rels, rtuple
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk import ne_chunk, pos_tag, word_tokenize

#Making sure that python will reach the user local installation of the nltk library.
os.environ["PYTHONPATH"] = "${PYTHONPATH}:/home/wdps1705/.local/lib/python2.6/site-packages"
nltk.data.path.append('/var/scratch/wdps1705/nltk_data/')

#Defines the position of each element on the relation dictionary: [relation, 1st Entity Type, 2nd Entity Type]
RELATION_REG_EXP = 0
ENTITIES = 1
TYPE_ENTITY_1 = 0
TYPE_ENTITY_2 = 1

# Example of sentences:
sample = 'Bob works at Microsoft in New York.'
sample2 = ' John works at Microsoft which is located in San Francisco.'
sample3 = ' Eduard is a developer at Microsoft in London.'
sample4 = ' John teaches at Xerox located in New York in United States.'
sample5 = ' The president Obama says to Hillary Clinton to try the elections for president of United States.'
sample6 = ' Richard goes to Brazil for vacations every year but he lives in Seatle.'
sample7 = ' The Dutch National Bank is located in Amsterdam capital of Netherlands.'

def extract_relations(text, typeRelations):

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

                print("This is the content of sent after chunk:" + str(chunked_sentence) + " and this is the content of i:"+ str(i))

                for typeRelation in typeRelations.iteritems():
                        # Compiling the 'filling' regular expression which will be used to extract the relations.
                        REL_RE = re.compile('.*(%s).*'%str(typeRelation[RELATION_REG_EXP]))

                        # Extracts the relation, this approach extracts only binary relation.
                        rels = extract_rels(str(typeRelation[ENTITIES][TYPE_ENTITY_1]),str(typeRelation[ENTITIES][TYPE_ENTITY_2]), chunked_sentence, corpus='ace', pattern=REL_RE, window=10)

                        for rel in rels:
                                print(rtuple(rel))
                                # Adds the relation to the final list of relations.
                                relations.append(rel)

            # Prints the extracted relations
            for relation in relations:
                    print("Element of final relations list: " + rtuple(relation))

# Binary relation
#[true, type_relation, type1, type2]

# Specific query
#[false, value, type]

def extractSentencesFromSpecificValue(typeRelation, sentenceList):

        filteredSentences = []
# For test only
#        typeRelation = ['John','PERSON']

#        print(str(typeRelation[0]))
#        print(str(typeRelation[1]))
########## Test ##############

        for sentence in sentenceList:
                # For each of the sentences tokenizes its words.
                sentenceWithTokenizedWords = word_tokenize(sentence)

                # Each tokenized word recieves now a tag 'part of speach'
                tagged_sentence = nltk.tag.pos_tag(sentenceWithTokenizedWords)

                # For the tagged sentence the program will try to find the specfic relation
                # based on the type of NE and a given 'filling' regular expression.
                # Uses nltk's taggger to assign a class to the Named Entyties using already tagged words as input
                chunked_sentence = nltk.chunk.ne_chunk(tagged_sentence)

                for item in chunked_sentence:
                        if hasattr(item,'label'):
                                if str(item[0][0]) == str(typeRelation[0]) and str(item.label()) == str(typeRelation[1]):
                                        filteredSentences.append(sentence)

        return filteredSentences





def extractSentencesFromRelations(typeRelation, sentenceList):

# For test only
        #typeRelation = ['works','PER','ORG']

        #print(str(typeRelation[0]))
        #print(str(typeRelation[1]))
########## Test ##############

        # List that will contain all the extracted relations
        relations = []

        for sentence in sentenceList:
                # For each of the sentences tokenizes its words.
                sentenceWithTokenizedWords = word_tokenize(sentence)

                # Each tokenized word recieves now a tag 'part of speach'
                tagged_sentence = nltk.tag.pos_tag(sentenceWithTokenizedWords)

                # For the tagged sentence the program will try to find the specfic relation
                # based on the type of NE and a given 'filling' regular expression.
                # Uses nltk's taggger to assign a class to the Named Entyties using already tagged words as input
                chunked_sentence = nltk.chunk.ne_chunk(tagged_sentence)

                print("This is the content of sent after chunk:" + str(chunked_sentence))

                # Compiling the 'filling' regular expression which will be used to extract the relations.
                REL_RE = re.compile('.*(%s).*'%str(typeRelation[RELATION_REG_EXP]))

                # Extracts the relation, this approach extracts only binary relation.
                rels = extract_rels(str(typeRelation[1]),str(typeRelation[2]), chunked_sentence, corpus='ace', pattern=REL_RE, window=10)
                if len(rels) > 0:
                        relations.append(sentence)
                        # Adds the relation to the final list of relations.
        return relations

# input: list of tuples in which each element is ([true|false] for binary relation, [relation|specific_value][, type_entity1, type_entity2])
def querySentencesByMultipleCriteria(listCriteria, sentenceList):

        resultSentences = []

# For test only
        #testCriteria = [True,'works','PER','ORG']
        #testListCriteria = []
        #testListCriteria.append(testCriteria)

        #listCriteria = testListCriteria
################# Test ###########


        for criteria in listCriteria:
                #Depending on the type of criteria the selection process occurs in a different manner.
                if criteria[0]: # In this case the search is for a binary relation PER "work" ORG
                        typeRelation = [criteria[1],criteria[2],criteria[3]]
                        sentences = extractSentencesFromRelations(typeRelation, sentenceList)
                        if len(sentences) > 0:
                                resultSentences.append(sentences)
                else:
                        # Example of this relation: 'John', PERSON
                        typeRelation = [criteria[1],criteria[2]]
                        sentences = extractSentencesFromSpecificValue(typeRelation, sentenceList)
                        if len(sentences) > 0:
                                resultSentences.append(sentences)
        return resultSentences

def extractSentences(text):
        # Splitting the text in multiple sentences.
        tokenizedSentences = sent_tokenize(text)
        return tokenizedSentences


if __name__ == '__main__':

        text= sample + sample2+sample3+sample4+sample5+sample6+sample7

#       Examples of possible types of relation:
#       typeRelations['works'] = ['PER','ORG']
#       typeRelations['is.*a.*developer.*at'] = ['PER','ORG']
#       typeRelations['located'] = ['ORG','GPE']
#       typeRelations['say'] = ['PER','PER']
#       typeRelations['go'] = ['PER','GPE']

#       extract_relations(text,typeRelations)

        sentences = extractSentences(text)

# Test criteria - To be replaced by Tung output with the list of criteria:
        testCriteria = []
        # Example of Binary Relation
        testCriteria.append([True,'go','PERSON','GPE'])
        # Example of specific query
        testCriteria.append([False,'Bob','PERSON'])

        print(str(querySentencesByMultipleCriteria(testCriteria,sentences)))

