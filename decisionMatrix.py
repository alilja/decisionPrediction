import yaml

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

    def __str__(self):
        return self.name

    def search(self, decisionList, option, attribute):
        return [element for element in decisionList if element['attribute'] == attribute and element['option'] == option]

    def display(self):
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
                    output += " | " + self.formatting.centerText(item[0]["name"], longestAttributeLength)
                else:
                    output += " | " + " "*longestAttributeLength
            output += "\n"

        print(output)

    def findDecision(self, decision):
        decisionEntry = (element for element in self.decisions if element["name"] == decision).__next__()
        return decisionEntry

    def view(self, decision):
        self.viewedDecisions.append(decision)
        selectedDecision = self.findDecision(decision)
        return selectedDecision["info"]

    def getOptions(self):
        return self.options

    def getAttributes(self):
        return self.attributes

    def getDecisions(self):
        return self.decisions

    def getMatrix(self):
        return self._matrix

    
decisions = DecisionMatrix()
data = ""
oldData = ""

while(data != "quit"):
    decisions.display()
    data = input("Your decision: ")
    if(data == oldData):
        decisions.view(data)
        print("You have selected decision "+data+".")
        data = "quit"
    print(decisions.view(data)+"\n\n")
    oldData = data