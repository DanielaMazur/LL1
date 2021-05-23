def parseGrammar(fileName):
  vt = []
  vn = []

  grammar = dict()

  file = open(fileName, "r")
  fileContent = file.read()

  vn = (fileContent[fileContent.index("VN")+4:fileContent.index("\n")-2]).split(", ")
  vt = (fileContent[fileContent.index("VT")+4:fileContent.index("\n", fileContent.index("VT"))-2]).split(", ")

  grammarList = (fileContent[fileContent.index("P")+3:fileContent.index("\n", fileContent.index("P"))-1]).split(", ")

  for grammarRule in grammarList:
    grammarComponents = grammarRule.split(" - ")

    productionResults = list(grammarComponents[1])

    if grammarComponents[0] not in grammar:
      grammar[grammarComponents[0]] = []

    grammar[grammarComponents[0]].append(productionResults)

  from collections import defaultdict
  return defaultdict(lambda: "default", vn=vn, vt=vt, grammar=grammar)

def firstOf(nonTerminal, grammar, vt):
    first = []

    nonTerminalProductions = grammar[nonTerminal]

    for production in nonTerminalProductions:
        if production[0] in vt or production[0] == 'e':
            first.append(production[0])
            continue
        nonTerminalFirst = production[0]

        first.extend(firstOf(nonTerminalFirst, grammar, vt))
    return first

def followOf(nonTerminal, grammar, vt):
    follow = []

    RHSSearchedNonTerminaProductions = getProductionsRHSWithSearchedNonTerminal(nonTerminal, grammar) 

    if nonTerminal == 'S':
        follow.append("$")
    
    #NON TERMINAL LEFT HAND SIDE
    for nonTerminalLHS in RHSSearchedNonTerminaProductions:
        for production in RHSSearchedNonTerminaProductions[nonTerminalLHS]:
            indexOfSearchedNonTerminal = production.index(nonTerminal)

           # if right recursion
            if len(production) == indexOfSearchedNonTerminal + 1 and nonTerminalLHS == nonTerminal:
                continue

            if len(production) == indexOfSearchedNonTerminal + 1 or production[indexOfSearchedNonTerminal + 1] == "e":
                follow.extend(followOf(nonTerminalLHS, grammar, vt))
                continue

            if production[indexOfSearchedNonTerminal + 1] in vt:
                follow.append(production[indexOfSearchedNonTerminal + 1])
                continue

            follow.extend(firstOf(production[-1], grammar, vt))
                
    return follow
    
#get productions where on the right hand side includes the given searchedNonTerminal
def getProductionsRHSWithSearchedNonTerminal(searchedNonTerminal, grammar):
    productions = {}

    for nonTerminal in grammar:
        for productionResult in grammar[nonTerminal]:
            if searchedNonTerminal in productionResult:
                if nonTerminal not in productions:
                    productions[nonTerminal] = []
                
                productions[nonTerminal].append(productionResult)
    return productions


def getParsingTable(grammar, vt, vn):
    parsingTable = [[0 for _ in range(len(vt)+2)] for _ in range(len(vn) + 1)]

    columnIndexes = {}
    for i in range(len(vt)):
        columnIndexes[vt[i]] = i + 1
        parsingTable[0][i + 1] = vt[i]

    parsingTable[0][len(vt) + 1] = "$"

    for i in range(len(vn)):
        parsingTable[i + 1][0] = vn[i]
        firstOfNonTerminalList = firstOf(vn[i], grammar, vt)
        for first in firstOfNonTerminalList:
            if first == "e":
                followOfNonTerminalList = followOf(vn[i], grammar, vt)
                for follow in followOfNonTerminalList:
                    parsingTable[i + 1][columnIndexes[follow]] = "e"
                continue
            if len(grammar[vn[i]]) == 1:
                parsingTable[i + 1][columnIndexes[first]] = grammar[vn[i]][0]
                continue

            for rule in grammar[vn[i]]:
                if rule[0] == "e":
                    continue
                if rule[0] in vt:
                    if rule[0] == first:
                        parsingTable[i + 1][columnIndexes[first]] = rule
                    continue
                firstOfRule = firstOf(rule[0],grammar, vt)
                if firstOfRule[0] == columnIndexes[first]: 
                    parsingTable[i + 1][columnIndexes[first]] = rule
                    continue
    return parsingTable

def getTableNonTerminalIdexes(parsingTable):
    nonTerminalIndexes = {}
    for i in range(1, len(parsingTable)):
        nonTerminalIndexes[parsingTable[i][0]] = i
    return nonTerminalIndexes

def getTableTerminalIndexes(parsingTable):
    terminalIndexes = {}
    for i in range(1, len(parsingTable[0])):
        terminalIndexes[parsingTable[0][i]] = i
    return terminalIndexes


def parseString(inputString, parsingTable, vn):
    inputStringCopy = inputString + "$"
    currentInputSymbol = inputStringCopy[0]
    stack = ['S','$']

    nonTerminalIndexes = getTableNonTerminalIdexes(parsingTable)
    terminalIndexes = getTableTerminalIndexes(parsingTable)

    while(len(stack)):
        currentStackSymbol = stack[0]
        if currentStackSymbol == currentInputSymbol and currentStackSymbol == "$":
            return #success
        if currentStackSymbol == currentInputSymbol:
            inputStringCopy = inputStringCopy[1 : len(inputStringCopy)]
            stack.pop(0)

            currentInputSymbol = inputStringCopy[0]
            continue
        if currentStackSymbol in vn:
            replacementProduction = parsingTable[nonTerminalIndexes[currentStackSymbol]][terminalIndexes[currentInputSymbol]]
            stack.pop(0)

            for symbol in reversed(replacementProduction):
                if symbol == 'e':
                    continue
                stack.insert(0, symbol)
            print(currentStackSymbol + ' -> ' + "".join(replacementProduction))

parsedGrammar = parseGrammar("v12")
parsingTable = getParsingTable(parsedGrammar['grammar'],  parsedGrammar['vt'], parsedGrammar['vn'])
parseString("abgdcf", parsingTable, parsedGrammar['vn'])
