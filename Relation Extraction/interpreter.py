import sys
import re
query = "Select * where PER = \"John\" and PER \"works at\" ORG or ORG = \"Microsoft\""
#query_refined = query.replace("Select * where ", "")
#query_by_splitted = re.split('and | or', query_refined)

#isQueryValid = False

#obj = re.match("(.+)\s+\"(.+?)\"\s+(.+)", "PER \"works\" ORG")
#obj1 = re.match("(.+)\s(=)\s+(.+)", "PERSON = tung")
#search_obj = re.search("I \"test\"", "\"\s*.*\s*\"")
entity_types = ["PER", "ORG", "LOC"]

def find_all(a_str, sub):
    start = 0
    while True:
        start = a_str.find(sub, start)
        if start == -1: return
        yield start
        start += len(sub) # use start += 1 to find overlapping matches

def extractQuery(query):
        query_elems = []
        query_refined = query.replace("Select * where ", "")
        query_by_splitted = re.split('and | or', query_refined)

        and_word_position_list = list(find_all(query, "and"))
        and_list_len = len(and_word_position_list)
        or_word_position_list = list(find_all(query, "or "))
        or_list_len = len(or_word_position_list)

        logic_list = []
        index = 0
        i= 0
	j= 0

	if and_list_len == 0:
                logic_list = "or" * or_list_len
        elif or_list_len == 0:
                logic_list = "and" * and_list_len
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
        print "Logic:"
        print (logic_list)


        for query_elem_str in query_by_splitted:
                if "=" in query_elem_str:
                        equal_query = re.match("\s*(.+)\s(=)\s+\"(.+)\"\s*", query_elem_str)
                        if equal_query == None:
                                return []
                        if equal_query.group(1) not in entity_types:
                                return []
                        entity_type1 = equal_query.group(1)
                        value = equal_query.group(3)
                        query_elems.append((False, value, entity_type1))
                else:
                        relation_query  = re.match("(.+)\s+\"(.+)\"\s+(.+)", query_elem_str)
                        if relation_query == None:
                                return []
                        if relation_query.group(1) not in entity_types or relation_query.group(3) not in entity_types:
                                return []
                        entity_type1 = relation_query.group(1)
                        relation = relation_query.group(2)
                        entity_type2 = relation_query.group(3)
                        query_elems.append((True, relation, entity_type1, entity_type2))
        #if "=" in query_elem_str:
        print "Result:"
        print query_elems
        return query_elems

extractQuery(query)