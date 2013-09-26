from decisionMatrix import *

#list-of-dict, list-of-str, list-of-str --> 
def analyzeDecisionStyle(decisionList, attributes, options):
	transitionList = []
	numOPWISE = 0
	numATTWISE = 0
	numMIXED = 0
	previousDecision = decisionList[0]
	for i in range(1, len(decisionList)):
		if(previousDecision["attribute"] == decisionList[i]["attribute"]):
			transitionList.append("OP_WISE")
			numOPWISE += 1
		elif(previousDecision["option"] == decisionList[i]["option"]):
			transitionList.append("ATT_WISE")
			numATTWISE += 1
		else:
			transitionList.append("MIXED")
			numMIXED += 1