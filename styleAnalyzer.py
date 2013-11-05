#!/usr/bin/python3
from decisionMatrix import *

class DecisionTracer:
    _attributes = []
    _options = []
    _decisions = []

    _decisionsMade = []
    _rankedDecisions = []
    _weightedAttributes = {}

    def __init__(self, matrix, rankedDecisions, weightedAttributes):
        self._matrix = matrix
        self.decisions = self._matrix.getDecisions()
        self.decisionsMade = self._matrix.getDecisionList()
        self.attributes = self._matrix.getAttributes()
        self.options = self._matrix.getOptions()

        self._weightedAttributes = weightedAttributes

        self.rankedDecisions = []
        for item in rankOrder:
            decisionEntry = self.matrix.findDecision(item)
            self.rankedDecisions.append(decisionEntry["option"])

    _DEBUG = True
    def debugLog(*msg):
        if(self._DEBUG):
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
        den = pow((sum_x_sq - pow(sum_x, 2) / n) * 
                    (sum_y_sq - pow(sum_y, 2) / n), 0.5)
        if den == 0: return 0
        return num / den

    def countTransitions(self):
        numOPWISE = 0
        numATTWISE = 0
        numMIXED = 0

        iterDecisionList = iter(self._decisionsMade)
        iterDecisionList.__next__()
        previousDecision = self._decisionsMade[0]
        for entry in iterDecisionList:
            #within attribute switch; option changes #intradimensional
            if(previousDecision["attribute"] == entry["attribute"]): 
                numATTWISE += 1
            #within option switch; attribute changes #interdimensional
            elif(previousDecision["option"] == entry["option"]):     
                numOPWISE += 1
            #both the option and attribute change
            else:                                                    
                numMIXED += 1
        return numOPWISE, numATTWISE, numMIXED

    def calculateOptionTimes(self):
        optionTimes = {}
        for entry in self._decisionsMade:
            if(entry["option"] not in optionTimes): # sum the total amount of time
                                                    # spent looking at each option
                optionTimes[entry["option"]] = 0
            optionTimes[entry["option"]] += entry["timeViewed"]
        return optionTimes

    def searchIndex(self):
        intra, inter, mixed = countTransitions()
        searchIndex = (inter - intra)/(inter + intra)
        debugLog(searchIndex)
        return searchIndex

    def method1(self, opWise, attWise, mixed, correlation = 0.7):
        """Capture EQW, MAU, LIM and LVA"""
        OPATTRatio = ((len(self._attributes) - 1)*len(self._options))
                        /(len(self._options) - 1) #ratio of options to attributes
        if((opWise/(attWise+mixed))/OPATTRatio < correlation):
            return "DIS|SAT"
        else:
            ###################################
            # SEPARATE EQW, MAU, LIM, AND LVA #
            ###################################
            # EQW ranking of options is just the sum of all the option's 
            #     utility values.
            # MAU ranking is sum of all utility values, with weights according 
            #     to how good each attribute is (weights must add up to 1)
            # LIM chooses the option with the worst value of the least important
            #     attribute
            # LVA chooses the option with the least variance across attribute 
            #     values

            ranks = {"MAU":[],"LIM":[],"LVA":[], "EQW":[]}

            lowestAttribute = min(self._weightedAttributes, 
                                  key=self._weightedAttributes.get)

            for option in self._options: #iterate through each option and grab a
                                         #list of all the decisions connected to it
                    #grab all the decisions that belong to that option
                    thisOptionsDecisions = [d for d in self._decisions
                                            if d["option"] == option] 

                    utilityValues = [d["utility"] for d in thisOptionsDecisions]
                    utilityAverage = sum(utilityValues)/len(self._options)

                    #EQW ranks
                    ranks["EQW"].append((sum(utilityValues), option))

                    MAUUtility = 0
                    variance = 0

                    #flip through each decision in the ones we grabbed
                    for thisDecision in thisOptionsDecisions: 
                        #MAU ranks
                        #weight that thisDecision's utility by the attribute weight
                        MAUUtility += thisDecision["utility"] * 
                                      self._weightedAttributes[thisDecision["attribute"]] 
                                      #the weight of the attribute currently being looked at
                                      #by thisDecision

                        #LIM ranks
                        if(thisDecision["attribute"] == lowestAttribute):
                            ranks["LIM"].append((thisDecision["utility"], option))

                        #LVA ranks
                        variance += (thisDecision["utility"] - utilityAverage) ** 2

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
                currentUtilities, currentOptions = zip(*currentList)

                for predictedItemRank, predictedItem in enumerate(currentOptions):
                    #grab the rank of that option in the user-inputed rank list
                    empiricalRank = rankedDecisions.index(predictedItem) 
                    deviation = (predictedItemRank - empiricalRank) ** 2    

                if(deviation < bestMatchScore):
                    bestMatchScore = deviation
                    bestMatchName = style

            return bestMatchName




#list-of-dict, list-of-str, list-of-str --> str
def analyzeDecisionStyle(matrix, rankOrder, weightedAttributes, minCorrelationPercentage=0.7, timeTolerance=0.8):
    decisionsMade = matrix.getDecisionList()
    attributes = matrix.getAttributes()
    options = matrix.getOptions()

    rankedDecisions = []
    for item in rankOrder:
        decisionEntry = matrix.findDecision(item)
        rankedDecisions.append(decisionEntry["option"])

    optionTimes = {}

    numOPWISE = 0
    numATTWISE = 0
    numMIXED = 0

    # Figure out what the ratio of option-wise, attribute-wise, and mixed transitions there are
    iterDecisionList = iter(decisionsMade)
    iterDecisionList.__next__()
    previousDecision = decisionsMade[0]
    for entry in iterDecisionList:
        if(previousDecision["attribute"] == entry["attribute"]): #within attribute switch; option changes #intradimensional
            numATTWISE += 1
        elif(previousDecision["option"] == entry["option"]):     #within option switch; attribute changes #interdimensional
            numOPWISE += 1
        else:                                                    #both the option and attribute change
            numMIXED += 1
        if(entry["option"] not in optionTimes): # sum the total amount of time
                                                  # spent looking at each option
            optionTimes[entry["option"]] = 0
        optionTimes[entry["option"]] += entry["timeViewed"]

        previousDecision = entry

    searchIndex = (numOPWISE - numATTWISE)/(numOPWISE + numATTWISE)
    debugLog(searchIndex)

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

            # TODO(alilja@iastate.edu) for some reason EQW/LIM and MAU/LVA are getting called at the same time. It's probably because of the matrix settings.

            ranks = {"MAU":[],"LIM":[],"LVA":[], "EQW":[]}

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
                currentUtilities, currentOptions = zip(*currentList)

                for predictedItemRank, predictedItem in enumerate(currentOptions):
                    #grab the rank of that option in the user-inputed rank list
                    empiricalRank = rankedDecisions.index(predictedItem) 
                    deviation = (predictedItemRank - empiricalRank) ** 2    

                if(deviation < bestMatchScore):
                    bestMatchScore = deviation
                    bestMatchName = style

            return bestMatchName
        else:
            return "DIS|SAT"

    elif(searchIndex < 0):

        #####################################################
        ### CAPTURING ADD, DOM, MAJ, MCD, EBA, LEX, & REC ###
        #####################################################

        #grab the attributes for every decision the user made
        attributesViewedOrdered = [x["attribute"] for x in decisionsMade]

        #create an empty list of lists as long as there are attributes 
        attributeRanks = [[] for i in range(0, len(attributes))] 

        # run through and increase the rank equal to the order each decision 
        # was viewed; earlier decisions are ranked more highly
        for i in range(0, len(attributesViewedOrdered)):
            rank = i+1
            attributeViewed = attributesViewedOrdered[i] # the attribute 
                                                         # that was viewed
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
            minTime = min(optionTimes.values())
            maxTime = max(optionTimes.values())
            debugLog(minTime, maxTime)
            if(minTime/maxTime >= 0.8):
                return("DOM|MAJ")
            return("ADD|MCD")
    else:
        return "ERR: Search index = 0.0"

decisions = DecisionMatrix()
data = ""
rankedDecisions = []

preBuiltDecisions = [1,2,3,4,5,6,7,8,9] #[1,4,7,2,5,8,3,6,9]


selectedOptions = [7, 4, 1]

for viewed in preBuiltDecisions:
    decisions.view("d0"+str(viewed))
    decisions.viewedDecisions[-1]["timeViewed"] = 1

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

print(analyzeDecisionStyle(matrix=decisions, rankOrder=rankedDecisions, 
                        weightedAttributes={"big":0.5,"bigger":0.3,"biggest":0.2}))