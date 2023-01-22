import pandas as pd

files = {}
table = open("Yosemite.csv", "r")

folder = "IncludeFiles/"
inputNameIndex = 0
lengthIndex = 1
outputNameIndex = 10
blocks = [4,5,6]
print(table.readline())

for line in table:
    row = line.split(",")
    inputWire = row[inputNameIndex].strip().split()
    if inputWire == []:
        continue
    if len(inputWire) == 2:
        inputName = inputWire[0] + "_" + str(eval(inputWire[1])[0])
    else:
        inputName = inputWire[0]
    lengthString = row[lengthIndex].strip()
    lengthString = lengthString  if lengthString == "" else lengthString + " "
    i = 0
    for block in blocks:
        module = row[block].strip()
        if module != "":
            fileName = module + "_InOut.vh"
            if fileName not in files:
                files[fileName] = open(folder + fileName, "w+")
            inputLine = "input logic " + lengthString + inputName + ",\n"
            files[fileName].write(inputLine)
            if i == len(blocks)-1:
                outputName = row[outputNameIndex].strip()
            else:
                outputName = inputName + "_"  + module
            outputLine = "output logic " + lengthString + outputName + ",\n"
            files[fileName].write(outputLine)

            fileName = module + "_Connect.vh"
            if fileName not in files:
                files[fileName] = open(folder + fileName, "w+")
            files[fileName].write("assign " + outputName + " = " + inputName + ";\n")
            inputName = outputName
            i += 1

for f in files:
    files[f].close()
