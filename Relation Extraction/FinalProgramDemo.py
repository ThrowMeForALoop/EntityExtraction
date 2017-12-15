#!/usr/bin/python

# -*- coding: utf-8 -*-
import sys
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
sample2 = ' John works at Microsoft which is located in San Francisco in United States.'
sample3 = ' Eduard is a developer at Microsoft in London.'
sample4 = ' John teaches at Xerox located in New York in United States.'
sample5 = ' The president Obama says to Hillary Clinton to try the elections for president of United States.'
sample6 = ' Richard goes to Brazil for vacations every year but he lives in Seatle.'
sample7 = ' The Dutch National Bank is located in Amsterdam capital of Netherlands.'
sample8 = ' John works at Microsoft which is located in Amsterdam capital of Netherlands.'
sample9 = ' Eduard is located in San Francisco in United States.'


def extractSentencesFromSpecificValue(typeRelation, sentenceList):

        filteredSentences = []

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

def intersect(a, b):
    """ return the intersection of two lists """
    return list(set(a) & set(b))

def union(a, b):
    """ return the union of two lists """
    return list(set(a) | set(b))


def extract_final_result(sentences_list, operator_list):

        if sentences_list is not None and len(sentences_list) > 0:
                result= sentences_list[0]

                if operator_list is not None:
                        for i in range(0,len(operator_list)):
                                if operator_list[i].upper() == 'AND':
#                                       print("!!!! Lists to be combined"+str(result)+" "+str(operator_list[i].upper())+" "+str(sentences_list[i+1]))
                                        result=intersect(result,sentences_list[i+1])
#                                       print("log op: "+str(result))
                                elif operator_list[i].upper() == 'OR':
                                        result=union(result,sentences_list[i+1])
#                                       print("log op: "+str(result))

                        return result

def find_all(a_str, sub):
    start = 0
    while True:
        a_str_lower = a_str.lower() # This is necessary in order to allow a search which is non case-sentitive
        sub_lower = sub.lower()

        start = a_str_lower.find(sub_lower, start)
        if start == -1: return
        yield start
        start += len(sub) # use start += 1 to find overlapping matches


def extractQuery(query):
        query_elems = []
        logic_list = []
        entity_types = ["PERSON", "ORGANIZATION", "GPE"]
        query_refined = query.replace(";", "")

        pattern_to_remove_select_where = re.compile("\s*select\s+\*\s+where\s+", re.IGNORECASE)
        select_where_match = pattern_to_remove_select_where.match(query_refined)

        if select_where_match == None:
                return logic_list, query_elems

        end_of_select_where = select_where_match.end()
        query_refined = query_refined[end_of_select_where:]
        query_by_splitted = re.split('and\s|or\s|AND\s|OR\s', query_refined)

        # Find all position of logic operator
        and_word_position_list = list(find_all(query, "and"))
        and_list_len = len(and_word_position_list)
        or_word_position_list = list(find_all(query, "or "))
        or_list_len = len(or_word_position_list)

        # Base on position of "and", "or" operator -> merge it into an ascending list
        index = 0
        i= 0
        j= 0

        if and_list_len == 0:
                logic_list = ["or"] * or_list_len
                j = or_list_len
        elif or_list_len == 0:
                logic_list = ["and"] * and_list_len
                i = and_list_len
        else:
                while index < (and_list_len + or_list_len):
                        if (and_word_position_list[i] <= or_word_position_list[j]):
                                logic_list.append("and")
                                i = i + 1
                                if i == and_list_len:
                                        break
                        else:
                                logic_list.append("or")
                                j = j + 1
                                if j == or_list_len:
                                        break
                        index = index + 1

        while i < and_list_len:
                logic_list.append("and")
                i = i + 1
        while j < or_list_len:
                logic_list.append("or")
                j = j + 1

        # Find query elem based on regular expression
        for query_elem_str in query_by_splitted:

                if "=" in query_elem_str:
                        equal_query = re.match("\s*(.+)\s(=)\s+\"(.+)\"\s*", query_elem_str)
                        if equal_query == None:
                                print "Equal not match"
                                query_elems = []
                                break

                        entity_type1 = str(equal_query.group(1).strip())
                        if entity_type1 not in entity_types:
                                query_elems = []
                                print "Equal entity type wrong"
                                break
                        value = str(equal_query.group(3))
                        query_elems.append((False, value, entity_type1))
                else:
                        relation_query  = re.match("(.+)\s+\"(.+)\"\s+(.+)", query_elem_str)
                        if relation_query == None:
                                print "Binary relation not match"
                                query_elems = []
                                break
                        entity_type1 = str(relation_query.group(1).strip())
                        entity_type2 = str(relation_query.group(3).strip())
                        if entity_type1  not in entity_types or entity_type2 not in entity_types:
                                print entity_types
                                print "Binary relation type wrong"
                                print entity_type1
                                print entity_type2
                                query_elems = []
                                break
                        relation = str(relation_query.group(2))
                        query_elems.append((True, relation, entity_type1, entity_type2))
        return  logic_list, query_elems

if __name__ == '__main__':

        text= sample + sample2+sample3+sample4+sample5+sample6+sample7+sample8+sample9

#       Examples of possible types of relation:
#       typeRelations['works'] = ['PER','ORG']
#       typeRelations['is.*a.*developer.*at'] = ['PER','ORG']
#       typeRelations['located'] = ['ORG','GPE']
#       typeRelations['say'] = ['PER','PER']
#       typeRelations['go'] = ['PER','GPE']

        query = raw_input("Enter your query: ").decode("utf-8")
        final_logic_list, final_query_elems = extractQuery(query)

        sentences = extractSentences(text)

        # Example of Binary Relation
#       testCriteria.append([True,'go','PERSON','GPE'])
        # Example of specific query
#       testCriteria.append([False,'Richard','PERSON'])
#        testCriteria.append([False,'Brazil', 'GPE'])

        filteredSentences = []
        filteredSentences = querySentencesByMultipleCriteria(final_query_elems, sentences)

        print("\n")
        print("Preliminary results before applying logical operators:")
        print("\n")
        print(str(filteredSentences))

        sentencesAfterLogicalOperators = extract_final_result(filteredSentences, final_logic_list)
        print("\n")
        print("Final result set (after applying logical operators):")
        print("\n")
        print(str(sentencesAfterLogicalOperators))