import yaml
import time

class TextFormatting:
    #centerText: str, int -> str
    def centerText(self, text, width):
        if(len(text) > width):
            return text[0:width]
        else:
            numSpaces = width - len(text)
            if(numSpaces % 2 == 0): #even length
                return " "*int(numSpaces/2) + text + " "*int(numSpaces/2)
            else:
                return " "*int((numSpaces-1)/2) + text + " "*int((numSpaces+1)/2)
        return text

    #standardizeCellWidths: list-of-str, int -> list-of-str
    def standardizeCellWidths(self, listOfItems, standardWidth):
        output = []
        for item in listOfItems:
            output.append(self.centerText(item, standardWidth))
        return output

class DecisionMatrix:
    options = []
    attributes = []
    decisions = []
    name = ""
    viewedDecisions = []

    def __init__(self, matrixFile = "matrix.yaml"):
        self.formatting = TextFormatting()  
        self._matrix = yaml.load(open(matrixFile,"r"))
        print(self._matrix)

        self.attributes = [d["name"] for d in self._matrix["attributes"]]
        self.options = [d["name"] for d in self._matrix["options"]]
        self.name = self._matrix["matrix_name"]
        self.decisions = self._matrix["decisions"]

        self.viewedDecisions = []

    def __str__(self):
        return self.name

    def search(self, decisionList, option, attribute):
        return [element for element in decisionList if element['attribute'] == attribute and element['option'] == option]

    def display(self, showUtilities = False):
        longestOptionLength = len(max(self.options, key=len))
        longestAttributeLength = len(max(self.attributes, key=len))

        #render attributes
        output = " "*longestOptionLength + " | " + " | ".join(self.formatting.standardizeCellWidths(self.attributes, longestAttributeLength)) + "\n"

        #render options
        for option in self.options:
            output += self.formatting.centerText(option, longestOptionLength)
            for attribute in self.attributes:
                item = self.search(self.decisions, option, attribute)
                if(item):
                    displayText = item[0]["name"]
                    if(showUtilities):
                        displayText += " " + str(item[0]["utility"])
                    output += " | " + self.formatting.centerText(displayText, longestAttributeLength)
                else:
                    output += " | " + " "*longestAttributeLength
            output += "\n"

        print(output)

    def findDecision(self, decision):
        decisionEntry = [element for element in self.decisions if element["name"] == decision]
        print(decisionEntry)
        return decisionEntry[0]

    def view(self, decision):
        selectedDecision = self.findDecision(decision)
        selectedDecision["timeViewed"] = time.clock()
        self.viewedDecisions.append(selectedDecision)
        return selectedDecision["info"]

    def getOptions(self):
        return self.options

    def getAttributes(self):
        return self.attributes

    def getDecisions(self):
        return self.decisions

    def getDecisionList(self):
        return self.viewedDecisions

    def getMatrix(self):
        return self._matrix

    def getDecisionInfo(self, decisionName):
        return self.findDecision(decisionName)

    def getDecisionAttribute(self, decisionName):
        info = self.findDecision(decisionName)/
        return info["attribute"]

    def getDecisionOption(self, decisionName):
        return self.findDecision(decisionName)["option"]


test = DecisionMatrix()
test.display(True)
    
