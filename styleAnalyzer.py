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
def analyzeDecisionStyle(matrix, rankOrder, weightedAttributes, minCorrelationPercentage=0.7, timeTolerance=0.8):
    attributes = matrix.getAttributes()
    options = matrix.getOptions()
    decisionList = matrix.getDecisionList()

    if(len(decisionList) <= 1):
        return ""

    #if(searchIndex < 0):

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
        #print("prev: "+previousDecision["name"]+"  this:"+decisionList[i]["name"]+"  "+transitionList[-1])
        previousDecision = decisionList[i]

    print(numOPWISE/(numATTWISE+numMIXED))

    if((numOPWISE/(numATTWISE+numMIXED))/OPATTRatio >= minCorrelationPercentage): #, timeTolerance=0.8higher values mean more precision, but more potential false negatives
        
        # EQW ranking of options is just the sum of all the option's utility values.
        # MAU ranking is sum of all utility values, with weights according to how good each attribute is (weights must add up to 1)
        # LIM chooses the option with the worst value of the least important attribute
        # LVA chooses the option with the least variance across attribute values

        EQWRanks = {}
        MAURanks = {}
        LIMRanks = {}
        LVARanks = {}

        lowestAttribute = min(weightedAttributes, key=weightedAttributes.get)

        for option in options: #iterate through each option and grab a list of all the decisions connected to it
                optionDecisions = [d for d in matrix.getDecisions() if d["option"] == option]

                #EQW ranks
                EQWRanks[option] = sum([d["utility"] for d in optionDecisions])
                print(EQWRanks)

                #MAU and LIM ranks
                MAUUtility = 0
                for decision in optionDecisions: #flip through each decision in the ones we grabbed
                    MAUUtility += decision["utility"] * weightedAttributes[decision["attribute"]] #weight that decision's utility by the attribute weight

                MAURanks[option] = MAUUtility

                #LIM ranks
                #for decision in 
                #if(optionDecisions["attribute"] == lowestAttribute and optionDecisions[])

        return "EQW|LIM|LVA|MAU"

    else:
        return "DIS|SAT"

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

decisions = DecisionMatrix()

data = ""
rankedDecisions = []

while(data != "quit"):
    decisions.display(True)
    print("Enter the decision name to view the decision.\nType \"done\" to make your selection.")
    data = input("> ")
    if(data.lower() == "done"):
        print("Enter your top four choices separated by spaces.")
        choices = input("> ")
        rankedDecisions = " ".split(choices)
        break
    else:
        print(decisions.view(data)+"\n\n")

print(analyzeDecisionStyle(decisions, rankedDecisions, {"big":0.5,"bigger":0.3,"biggest":0.2}))

