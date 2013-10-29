#!/usr/bin/python3
from decisionMatrix import *

_DEBUG = True
def debugLog(msg):
    if(_DEBUG):
        print(msg)

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
    decisionList = matrix.getDecisionList()
    if(len(decisionList) <= 1):
        return ""
    attributes = matrix.getAttributes()
    options = matrix.getOptions()
    decisionRankList = []

    for item in rankOrder:
        decisionEntry = matrix.findDecision(item)
        decisionRankList.append(decisionEntry["option"])

    numOPWISE = 0
    numATTWISE = 0
    numMIXED = 0

    # Figure out what the ratio of option-wise, attribute-wise, and mixed transitions there are
    previousDecision = decisionList[0]
    for i in range(1, len(decisionList)):
        if(previousDecision["attribute"] == decisionList[i]["attribute"]): #within attribute switch; option changes #intradimensional
            numATTWISE += 1
        elif(previousDecision["option"] == decisionList[i]["option"]): #within option switch; attribute changes #interdimensional
            numOPWISE += 1
        else: #both the option and attribute change
            numMIXED += 1
        previousDecision = decisionList[i]

    searchIndex = (numOPWISE - numATTWISE)/(numOPWISE + numATTWISE)
    debugLog(searchIndex) #debug

    if(searchIndex > 0):

        ################################################
        ### CAPTURING EQW, LIM, LVA, MAU, DIS, & SAT ###
        ################################################

        OPATTRatio = ((len(attributes) - 1)*len(options))/(len(options) - 1) #ratio of options to attributes
        if((numOPWISE/(numATTWISE+numMIXED))/OPATTRatio >= minCorrelationPercentage): #higher values mean more precision, but more potential false negatives
            
            ###################################
            # SEPARATE EQW, MAU, LIM, AND LVA #
            ###################################
            # EQW ranking of options is just the sum of all the option's utility values.
            # MAU ranking is sum of all utility values, with weights according to how good each attribute is (weights must add up to 1)
            # LIM chooses the option with the worst value of the least important attribute
            # LVA chooses the option with the least variance across attribute values

            ranks = {"EQW":[],"MAU":[],"LIM":[],"LVA":[]}

            lowestAttribute = min(weightedAttributes, key=weightedAttributes.get)

            for option in options: #iterate through each option and grab a list of all the decisions connected to it
                    optionDecisions = [d for d in matrix.getDecisions() if d["option"] == option] #grab all the decisions that belong to that option

                    utilityValues = [d["utility"] for d in optionDecisions]
                    utilityAverage = sum(utilityValues)/len(options)

                    #EQW ranks
                    ranks["EQW"].append((sum(utilityValues), option))

                    MAUUtility = 0
                    variance = 0

                    for decision in optionDecisions: #flip through each decision in the ones we grabbed
                        #MAU ranks
                        MAUUtility += decision["utility"] * weightedAttributes[decision["attribute"]] #weight that decision's utility by the attribute weight

                        #LIM ranks
                        if(decision["attribute"] == lowestAttribute):
                            ranks["LIM"].append((decision["utility"], option))

                        #LVA ranks
                        variance += (decision["utility"] - utilityAverage) ** 2

                    variance = variance / (len(options) - 1)
                    ranks["LVA"].append((variance, option))

                    ranks["MAU"].append((MAUUtility, option))

            ranks["EQW"].sort(reverse=True)
            ranks["MAU"].sort(reverse=True)
            ranks["LIM"].sort()
            ranks["LVA"].sort()

            bestMatchName = ""
            bestMatchScore = 1000

            for style, currentList in ranks.items():            
                deviation = 0

                print(style, currentList)

                for predictedItemRank in range(0, len(currentList)):
                    predictedRankName = currentList[predictedItemRank][1]     #grab the option name of the current decision in the rank list we're looking at
                    empiricalRank = decisionRankList.index(predictedRankName) #grab the rank of that option in the user-inputed rank list

                    deviation = (predictedItemRank - empiricalRank) ** 2      #calcuate deviation

                if(deviation < bestMatchScore):
                    bestMatchScore = deviation
                    bestMatchName = style

                i += 1

            return bestMatchName
        else:
            return "DIS|SAT"

    elif(searchIndex < 0):

        #####################################################
        ### CAPTURING ADD, DOM, MAJ, MCD, EBA, LEX, & REC ###
        #####################################################

        attributesViewedOrdered = [x["attribute"] for x in decisionList] #grab the attributes for every decision the user made
        attributeRanks = [[] for i in range(0, len(attributes))] #create an empty list of lists as long as there are attributes
        #run through and increase the rank equal to the order each decision was viewed; earlier decisions are ranked more highly
        for i in range(0, len(attributesViewedOrdered)):
            rank = i+1
            attributeViewed = attributesViewedOrdered[i] #the attribute that was viewed
            attributeNumber = attributes.index(attributeViewed) 

            attributeRanks[attributeNumber].append(rank) 

        ARList = []
        NBoxList = []

        for attributeRankList in attributeRanks: #math
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
    else:
        return "FATAL ERROR. searchIndex = 0.0"

decisions = DecisionMatrix()
data = ""
rankedDecisions = []

preBuiltDecisions = [1,2,3,
                     4,5,6,
                     7,8,9]
                     
selectedOptions = [1, 5, 9]

for viewed in preBuiltDecisions:
    decisions.view("d0"+str(viewed))

for selected in selectedOptions:
    rankedDecisions.append("d0"+str(selected))

"""while(data != "quit"):
    decisions.display(True)
    print("Enter the decision name to view the decision.\nType \"done\" to make your selection.")
    data = input("> ")
    if(data.lower() == "done"):
        print("Enter your top four choices separated by spaces.")
        choices = input("> ")
        rankedDecisions = choices.split(" ")
        print(rankedDecisions)
        break
    else:
        print(decisions.view(data)+"\n\n")"""

print(analyzeDecisionStyle(decisions, rankedDecisions, {"big":0.5,"bigger":0.3,"biggest":0.2}))

