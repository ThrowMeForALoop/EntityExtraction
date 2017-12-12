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

sample = 'Bob works at Microsoft in New York.'
sample2 = ' John works at Microsoft which is located in San Francisco.'
sample3 = ' Eduard is a developer at Microsoft in London.'
sample4 = ' John teaches at Xerox located in New York in United States.'
sample5 = ' The president Obama says to Hillary Clinton to try the elections for president of United States.'
sample6 = ' John goes to Brazil for vacations every year but he lives in Seatle.'


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

                for typeRelation in typeRelations:
                        REL_RE = re.compile('.*(%s).*'%typeRelation)

                        # Extracts the relation.
                        rels = extract_rels('PER', 'ORG', chunked_sentence, corpus='ace', pattern=REL_RE, window=10)
                        rels2 = extract_rels('ORG', 'GPE', chunked_sentence, corpus='ace', pattern=REL_RE, window=10)

                        rels3 = extract_rels('PER', 'PER', chunked_sentence, corpus='ace', pattern=REL_RE, window=10)
                        rels4 = extract_rels('PER', 'GPE', chunked_sentence, corpus='ace', pattern=REL_RE, window=10)

                        for rel in rels:
                                print(rtuple(rel))
                                # Adds the relation to the final list of relations.
                                relations.append(rel)

                        for rel in rels2:
                                print(rtuple(rel))
                                # Adds the relation to the final list of relations.
                                relations.append(rel)


                        for rel in rels3:
                                print(rtuple(rel))
                                # Adds the relation to the final list of relations.
                                relations.append(rel)

                        for rel in rels4:
                                print(rtuple(rel))
                                # Adds the relation to the final list of relations.
                                relations.append(rel)



            # Prints the extracted relations
            for relation in relations:
                    print("Element of final relations list: " + rtuple(relation))

if __name__ == '__main__':

        text= sample + sample2+sample3+sample4+sample5+sample6

        typeRelations = []
        typeRelations.append('works')
        typeRelations.append('is.*at')
        typeRelations.append('located')
        typeRelations.append('say')
        typeRelations.append('go')

        extract_relations(text,typeRelations)
