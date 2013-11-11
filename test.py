from styleAnalyzer import DecisionMatrix

decisions = DecisionMatrix()
data = ""
rankedDecisions = []

preBuiltDecisions = [1,7,4,3,9,5] #[1,4,7,2,5,8,3,6,9] #[1,2,3,4,5,6,7,8,9] #


selectedOptions = [4]

for i, viewed in enumerate(preBuiltDecisions):
    decisions.view("d0"+str(viewed))
    decisions.viewedDecisions[-1]["timeViewed"] = 3*i

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

op, att, mix = decisionTracer.countTransitions()
print(op, att, mix)
print(decisionTracer.calculateSearchMeasure(op, att, mix))
print(decisionTracer.calculateSearchIndex(op, att, mix))
print(decisionTracer.pearsonr([4.5, 10.5, 13.5],[8,4,2]))
print(decisionTracer.DecisionTracer())