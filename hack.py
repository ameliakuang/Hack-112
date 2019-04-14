from flask import Flask, render_template, request
from jinja2 import Environment, PackageLoader, select_autoescape
import ast

env = Environment(
    loader=PackageLoader('flask', 'templates'),
    autoescape=select_autoescape(['html', 'xml'])
)

app = Flask(__name__)

#####
# def readFile(path):
#     with open(path, "rt") as f:
#         return f.read()

def ownerShip(hwLines):
    hwLines = hwLines[:11]
    result = ""
    ID = False
    Section = False
    for i in range(len(hwLines)):
        line = hwLines[i]
        line = line.lower()
        id = line.find("andrewid")
        sec = line.find("section")
        if id != -1:
            ID = True
            line = line[id + 9:]
            if not line.islower():
                result += "After 'andrewID:'please write your andrewID." + "\n"
        elif sec != -1:
            Section = True
            line = line[sec + 7:]
            if not line.islower() and not line.isupper():
                result += "After 'section:' please write your section" + "\n"
    if not Section or not ID:
        result += "Please write your andrewID and section!" + "\n"
    return result


# 完成
def comments(hwLines):
    instruction = False
    violation = ''
    if hwLines[0].startswith("#####"):
        instruction = True
    elif hwLines[0].startswith("def "):
        result1 = "Please write comments at line" + "0" + "\n"
        violation += result1
    index = 1
    while index < len(hwLines):
        if hwLines[index].startswith("def ") and \
                hwLines[index].find("Collaborators") == -1 and not \
                hwLines[index - 1].startswith("#") and \
                not hwLines[index][4:].startswith("test") and not \
                hwLines[index][4:].startswith("main") and not \
                hwLines[index][4:].startswith("run("):
            result2 = "Please write comments at line" + str(index) + "\n"
            violation += result2
        elif hwLines[index].startswith("#####"):
            instruction = not instruction
        elif instruction == False and hwLines[index].startswith("#"):
            count = 0
            i = 0
            while (i + index <= len(hwLines) - 1 and hwLines[index + \
                                                             i].startswith("#")):
                count += 1
                i += 1
            if count >= 3:
                result3 = "Better be more concise around line" + str(index) + '\n'
                violation += result3
            index += (i - 1)
        index += 1
    return violation


def globalVariables(hwLines, detect=True):
    result = ""
    for i in range(len(hwLines)):
        line = hwLines[i]
        if ("'''" in line):
            detect = not detect
        if detect:
            if not (line.startswith("#") or line.startswith("def") \
                    or line.startswith("\t") or line.startswith("\n") \
                    or line.startswith(" ") or line.startswith("import") \
                    or line.startswith("class") or line.startswith("if") \
                    or line.startswith("") or line.startswith("from")):
                result += "Line " + str(i) + ": please do not use global variables!" + "\n"
    return result


def unusedCode(hwLines):
    result = ""
    for i in range(len(hwLines) - 1):
        currLine = hwLines[i]
        if ("return" in currLine) and currLine[0] != "#":
            indentation = 0
            detect = True
            for c in currLine:
                if detect:
                    if c == " ":
                        indentation += 1
                    else:
                        detect = False
                        break
            nextLine = hwLines[i + 1]
            onTheSameLevel = True
            if (indentation < len(nextLine)):
                for j in range(indentation):
                    if (nextLine[j] != " "):
                        onTheSameLevel = False
                        break
            if indentation < len(nextLine) and onTheSameLevel \
                    and (nextLine[indentation] != " "):
                result += "Line " + str(i) + "you may have dead codes here:)" + "\n"
    for i in range(len(hwLines)):
        line = hwLines[i]
        if ("print" in line) and not "Test" in line and not "Pass" in line:
            result += "Line " + str(i) + "you may want to check for debugging code here:)" + "\n"
    return result


def formatting(hwLines):
    result = ""
    for i in range(len(hwLines)):
        yesSymbol = False
        line = hwLines[i]
        if "=" in line:
            checkList = ["+=", "-=", "*=", "/=", "//=", "%=", "!="]
            for symbol in checkList:
                if (symbol in line):
                    yesSymbol = True
                    index = line.find(symbol)
                    if (line[index - 1] == " " and line[index + 2] != " ") or (
                            line[index - 1] != " " and line[index + 2] == " "):
                        result += "Line " + str(i) + ": you may have inconsistent white space here:)" + "\n"
        if (not yesSymbol):
            if (line.find("==") != -1):
                index = line.find("==")
                if (line[index - 1] == " " and line[index + 2] != " ") or (
                        line[index - 1] != " " and line[index + 2] == " "):
                    result += "Line " + str(i) + ": you may have inconsistent white space here:)" + "\n"
            else:
                if "==" not in line and (line.find("=") != -1):
                    index = line.find("=")
                    if (line[index - 1] == " " and line[index + 1] != " ") or (
                            line[index - 1] != " " and line[index + 1] == " "):
                        result += "Line " + str(i) + ": you may have inconsistent white space here:)" + "\n"

    return result


# 完成
def helperFunctions(hwLines):
    violation = ''
    functions = []
    inComments = False
    index = 0
    while index < len(hwLines):
        if hwLines[index].startswith("def "):
            startIndex = index + 1
            end = hwLines[index].find("(")
            functionName = hwLines[index][4:end]
            if not functionName.startswith("test") or functionName \
                    != "run" or functionName != "main":
                tempList = [hwLines[index]]
                i = 1
                while i + index < len(hwLines):
                    line = hwLines[i + index]
                    if line.startswith("def "):
                        break
                    if line.find("'''") != -1: inComments = not inComments
                    if inComments == True:
                        tempList += [line]
                    elif not (line.isspace() or line == "" or \
                              line.strip().startswith("#")) and line[0].isspace():
                        tempList += [line]
                    i += 1
                functions += [(startIndex, tempList, functionName)]
                index += i - 1
        index += 1
    for function in functions:
        startIndex, tempList, functionName = function
        if len(tempList) >= 30:
            result = "Function <%s> is more than 30 lines!" % (functionName) + '\n'
            violation += result
    return violation


def variableNames(hwLines):
    hw = ""
    for i in range(len(hwLines)):
        hw += hwLines[i]
    lstVar = list(hackVariables(hw))
    result = ""
    for var in lstVar:
        var = str(var)
        if "-" in var or "_" in var:
            result = result + var + "--Please use camelCase for 112!" + "\n"
        if not var in ["i", "j", "hi", "lo", "c"] and len(var) <= 2:
            result = result + var + "--Please use a meaningful variable name " + "\n"
        if var in ["dict", "dir", "id", "input", "int", "len", "list", "map", \
                   "max", "min", "next", "object", "set", "str", "sum", "type", "tuple", \
                   "continue", "return"]:
            result = result + var + "--This variable name is used by Python, change it!" + "\n"
        if not var[0].islower:
            result = result + var + "--Please start with a lower-case letter" + "\n"
    return result


def testFunctions(hwLines):
    hw = ""
    for i in range(len(hwLines)):
        hw += hwLines[i]
    lstFunc = list(hackFunctionNames(hw))
    result = ""
    hasTest = False
    tests = set()
    funcs = []
    for func in lstFunc:
        if func in ["main", "run", "testAll", "readFile", "almostEqual", \
                    "writeFile", "init", "redrawAll", "keyPressed", "mousePressed", \
                    "timerfired"]:
            continue
        elif len(func) >= 13 and func[-13:] == "Collaborators":
            continue
        if func.startswith("test"):
            hasTest = True
            tests.add(func)
        else:
            funcs += [func]
    for func in funcs:
        testFunc = "test" + func[0].upper() + func[1:]
        if testFunc not in tests:
            result += "Function <%s> does not have a test function \n" % (func)
    return result


def hackVariables(hw):
    root = ast.parse(hw)
    for node in ast.walk(root):
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            yield node.id


def hackFunctionNames(hw):
    root = ast.parse(hw)
    for node in ast.walk(root):
        if isinstance(node, ast.FunctionDef):
            yield node.name


def hackAttributes(hw):
    root = ast.parse(hw)
    for node in ast.walk(root):
        if isinstance(node, ast.Attribute):
            yield node.attr


def startCommonSubString(s1, s2):
    if (not s1.isalpha()) or (not s2.isalpha()):
        return ""
    i = 1
    while i <= len(s1):
        if s1[:i] in s2:
            i += 1
        else:
            break
    return s1[:i - 1]


def longestCommonSubstring(s1, s2):
    longest = startCommonSubString(s1, s2)
    currentLongest = " "
    while s1 != "":
        currentLongest = startCommonSubString(s1, s2)
        if len(longest) < len(currentLongest):
            longest = currentLongest
        if len(longest) == len(currentLongest) and longest >= currentLongest:
            longest = currentLongest
        if currentLongest == "":
            s1 = s1[1:]
        else:
            s1 = s1.replace(currentLongest, "")
    return longest


def repetitiveCode(hwLines):
    rep = {}
    result = ""
    for i in range(len(hwLines)):
        for j in range(i + 1, len(hwLines)):
            longStr = longestCommonSubstring(hwLines[i], hwLines[j])
            if len(longStr) >= 6:
                if longStr in rep:
                    rep[longStr].add(j + 1)
                else:
                    rep[longStr] = set([i + 1, j + 1])
    for key in rep.keys():
        if len(rep[key]) >= 3:
            temp = "Code %s was repeated more than 3 times #" % (key)
            result += temp
    return result


def styleChecker(hw):
    hwLines = hw.splitlines()
    result = ""
    result += ownerShip(hwLines)
    result += comments(hwLines)
    result += globalVariables(hwLines)
    result += formatting(hwLines)
    result += unusedCode(hwLines)
    result += repetitiveCode(hwLines)
    result += testFunctions(hwLines)
    result += variableNames(hwLines)
    result += helperFunctions(hwLines)
    return result

#####

#
# def readFile(path):
#     with open(path, "rt") as f:
#         return f.read()
#
# def writeFile(path, contents):
#     with open(path, "wt") as f:
#         f.write(contents)

def processFile(inputFile): # return the processed output
    return styleChecker(inputFile)

@app.route('/')
def index():
    return render_template('tryit.html')

@app.route('/', methods=["POST"])
def getValue():
    hwFile = request.form['hwFile']
    andrewId = request.form['andrewId'] # takes in andrew ID
    styleComments = processFile(hwFile)
    # print(hwFile)
    return render_template('fixerResult.html', sc=styleComments, hw=hwFile, aid=andrewId)

if __name__ == '__main__':
    app.run()
