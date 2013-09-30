from decisionMatrix import *

#list-of-dict, list-of-str, list-of-str --> 
def analyzeDecisionStyle(decisionList, attributes, options):
	if(len(decisionList) <= 1):
		return
	transitionList = []
	numOPWISE = 0
	numATTWISE = 0
	numMIXED = 0

	OPATTRatio = ((len(attributes) - 1)*len(options))/(len(options) - 1)

	previousDecision = decisionList[0]
	for i in range(1, len(decisionList)):
		if(previousDecision["attribute"] == decisionList[i]["attribute"]):
			transitionList.append("ATT_WISE") #within attribute; option changes
			numATTWISE += 1
		elif(previousDecision["option"] == decisionList[i]["option"]):
			transitionList.append("OP_WISE") #within option; attribute changes
			numOPWISE += 1
		else:
			transitionList.append("MIXED")
			numMIXED += 1
		print("prev: "+previousDecision["name"]+"  this:"+decisionList[i]["name"]+"  "+transitionList[-1])
		previousDecision = decisionList[i]
	print(numOPWISE/(numATTWISE+numMIXED))
	print(OPATTRatio)

decisions = DecisionMatrix()
data = ""
oldData = ""

while(data != "quit"):
    decisions.display()
    data = input("Your decision: ")
    if(data == oldData):
        print("You have selected decision "+data+".")
        break
    else:
    	print(decisions.view(data)+"\n\n")
    oldData = data

analyzeDecisionStyle(decisions.getDecisionList(), decisions.getAttributes(), decisions.getOptions())