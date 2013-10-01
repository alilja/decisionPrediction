from decisionMatrix import *

def pearsonr(x, y):
    # Assume len(x) == len(y)
    n = len(x)
    sum_x = float(sum(x))
    sum_y = float(sum(y))
    sum_x_sq = sum(map(lambda x: pow(x, 2), x))
    sum_y_sq = sum(map(lambda x: pow(x, 2), y))
    psum = sum(map(lambda x, y: x * y, x, y))
    num = psum - (sum_x * sum_y/n)
    den = pow((sum_x_sq - pow(sum_x, 2) / n) * (sum_y_sq - pow(sum_y, 2) / n), 0.5)
    if den == 0: return 0
    return num / den

#list-of-dict, list-of-str, list-of-str --> str
def analyzeDecisionStyle(decisionList, attributes, options, minPercentage=0.7):
    if(len(decisionList) <= 1):
        return ""

    #if(searchIndex < 0):

    #####################################################
    ### CAPTURING ADD, DOM, MAJ, MCD, EBA, LEX, & REC ###
    #####################################################

    attributesViewedOrdered = [x["attribute"] for x in decisionList]
    attributeRanks = [[] for i in range(0, len(attributes))]
    for i in range(0, len(attributesViewedOrdered)):
        rank = i+1
        attributeViewed = attributesViewedOrdered[i]
        attributeNumber = attributes.index(attributeViewed)

        attributeRanks[attributeNumber].append(rank)

    ARList = []
    NBoxList = []

    for attributeRankList in attributeRanks:
        nbox = len(attributeRankList)
        gross = sum(attributeRankList)
        avg = gross/nbox

        ARList.append(avg)
        NBoxList.append(nbox)

    correlation = pearsonr(ARList, NBoxList)
    
    if(correlation < 0):
        return("EBA|LEX|REC")
    else:
        return("DOM|MAJ|ADD|MCD")




    ################################################
    ### CAPTURING EQW, LIM, LVA, MAU, DIS, & SAT ###
    ################################################

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

    if((numOPWISE/(numATTWISE+numMIXED))/OPATTRatio >= minPercentage): #higher values mean more precision, but more potential false negatives
        return "EQW|LIM|LVA|MAU"
    else:
        return "DIS|SAT"


    

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

print(analyzeDecisionStyle(decisions.getDecisionList(), decisions.getAttributes(), decisions.getOptions()))