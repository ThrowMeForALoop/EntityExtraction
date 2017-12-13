def intersect(a, b):
    """ return the intersection of two lists """
    return list(set(a) & set(b))

def union(a, b):
    """ return the union of two lists """
    return list(set(a) | set(b))


def extract_final_result(sentences_list, operator_list):
	result= sentences_list[0]
	for i in range(0,len(operator_list)):
		if operator_list[i]=='AND':
			result=intersect(result,sentences_list[i+1])
		elif operator_list[i]=='OR':
			result=union(result,sentences_list[i+1])

	for i in range(0,len(result)):
		print " item ",i," is: ",result[i], '\n'

	return result


#test the program

sentences_list=[[' John works at Microsoft which is located in San Francisco.',
' John teaches at Xerox located in New York in United States.'],[' John works at Microsoft which is located in San Francisco.',
'Bob works at Microsoft.'],[' John works at Microsoft which is located in San Francisco.',
'Bob works at Microsoft.',
' John teaches at Microsoft located in New York in United States.']]

operator_list= ['AND', 'OR']

extract_final_result(sentences_list,operator_list)