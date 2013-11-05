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
        self._decisions = self._matrix.getDecisions()
        self._decisionsMade = self._matrix.getDecisionList()
        self._attributes = self._matrix.getAttributes()
        self._options = self._matrix.getOptions()

        self._weightedAttributes = weightedAttributes

        self._rankedDecisions = []
        for item in rankedDecisions:
            decisionEntry = self._matrix.findDecision(item)
            self._rankedDecisions.append(decisionEntry["option"])

        self._DEBUG = True

    def debugLog(self, *msg):
        if(self._DEBUG):
            print(msg)

    def pearsonr(self, x, y):
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
            print(entry)
            previousDecision = entry
        return numOPWISE, numATTWISE, numMIXED

    def calculateOptionTimes(self):
        optionTimes = {}
        for entry in self._decisionsMade:
            if(entry["option"] not in optionTimes): # sum the total amount of time
                                                    # spent looking at each option
                optionTimes[entry["option"]] = 0
            optionTimes[entry["option"]] += entry["timeViewed"]
        return optionTimes

    def caclulateSearchIndex(self):
        intra, inter, mixed = self.countTransitions()
        searchIndex = (inter - intra)/(inter + intra)
        self.debugLog(searchIndex)
        return searchIndex

    def method1(self, opWise, attWise, mixed):
        """Capture EQW, MAU, LIM and LVA"""
        OPATTRatio = ((len(self._attributes) - 1)*
                        len(self._options))/(len(self._options) - 1) #ratio of options to attributes
        return (opWise/(attWise+mixed))/OPATTRatio        

    def method2(self):
        optionTimes = self.calculateOptionTimes()
        minTime = min(optionTimes.values())
        maxTime = max(optionTimes.values())
        self.debugLog(minTime, maxTime)
        if(minTime/maxTime >= 0.8):
            return("DOM|MAJ")
        return("ADD|MCD")

    def method3(self):
        #####################################################
        ### CAPTURING ADD, DOM, MAJ, MCD, EBA, LEX, & REC ###
        #####################################################

        #grab the attributes for every decision the user made
        attributesViewedOrdered = [x["attribute"] for x in self._decisionsMade]

        #create an empty list of lists as long as there are attributes 
        attributeRanks = [[] for i in range(0, len(self._attributes))] 

        # run through and increase the rank equal to the order each decision 
        # was viewed; earlier decisions are ranked more highly
        for i in range(0, len(attributesViewedOrdered)):
            rank = i+1
            attributeViewed = attributesViewedOrdered[i] 
            attributeIndex = self._attributes.index(attributeViewed) 
            attributeRanks[attributeIndex].append(rank) 

        ARList = []
        NBoxList = []

        for attributeRankList in attributeRanks:
            nbox = len(attributeRankList)
            gross = sum(attributeRankList)
            avg = gross/nbox

            ARList.append(avg)
            NBoxList.append(nbox)

        return self.pearsonr(ARList, NBoxList)

    def method4(self):
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
                    MAUUtility += (thisDecision["utility"]* 
                                  self._weightedAttributes[thisDecision["attribute"]]) 
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

    def DecisionTracer(self, correlation = 0.7):
        searchIndex = self.caclulateSearchIndex()
        if(searchIndex > 0):
            op, att, mix = self.countTransitions()
            if(self.method1(op, att, mix) >= correlation):
                return self.method4()
            else:
                return "DIS|SAT"
        else:
            if(self.method3() < 0):
                return("EBA|LEX|REC")
            else:
                return self.method2()

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
decisionTracer = DecisionTracer(matrix=decisions, rankedDecisions=rankedDecisions, 
                        weightedAttributes={"big":0.5,"bigger":0.3,"biggest":0.2})

print(decisionTracer.DecisionTracer())