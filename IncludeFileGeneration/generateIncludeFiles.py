"""
Created on Sun Jan 22 12:00:00 2023

This file reads a table and generates include files for verilog. The files define connections that
are passing through modules in order to get to a signal between modules that are not adjcent. Each
row in the table defines an output from a source module. The modules the output needs to passthrough
and the final module to input to. The script will generate 2 files for each module that needs to be
passed through. One for defining the input and output and one for connection the input and output.

"""

table = open("Yosemite.csv", "r")

# dict to store all the files we are writing to
files = {}
folder = "IncludeFiles/"

# these are the column indices in the table of the value
inputNameIndex = 0
lengthIndex = 1
outputNameIndex = 9
blocks = [4,5,6]

# read the header row to get it out of the way
print(table.readline())

for line in table:
    # the table is a csv so split on the commas
    row = line.split(",")
    # if the input is specfic element from the wire document that
    inputWire = row[inputNameIndex].strip().split()
    #if there is no input value skip the row
    if inputWire == []:
        continue
    # if the length is 2 that means there we are indexing the input e.g. rv64_dbg_rst_l [0] is
    # turned into rv64_dbg_rst_l_0
    if len(inputWire) == 2:
        name = inputWire[0] + "_" + str(eval(inputWire[1])[0])
    else:
        name = inputWire[0]
    inputName = name

    # get the width value set correctly
    lengthString = row[lengthIndex].strip()
    lengthString = lengthString  if lengthString == "" else lengthString + " "

    # create a list of the module names this method makes it easy to see how many values there are
    modules = []
    for block in blocks:
        module = row[block].strip()
        if module == "":
            break
        modules.append(module)

    i = 0
    # loop through the modules we are passing through
    for module in modules:
        # create the new input output file and add it to the files dict if it isn't there
        fileName = module + "_InOut.vh"
        if fileName not in files:
            files[fileName] = open(folder + fileName, "w+")
        # write the input and output lines
        inputLine = "input logic " + lengthString + inputName + ",\n"
        files[fileName].write(inputLine)
        # if we are on the last module use the correct input name
        if i == len(modules)-1:
            outputName = row[outputNameIndex].strip()
        else:
            outputName = name + "_"  + module
        outputLine = "output logic " + lengthString + outputName + ",\n"
        files[fileName].write(outputLine)

        # create the new connect file and add it to the files dict if isn't there
        fileName = module + "_Connect.vh"
        if fileName not in files:
            files[fileName] = open(folder + fileName, "w+")
        # write the input output lines
        files[fileName].write("assign " + outputName + " = " + inputName + ";\n")
        # set the new input to be the output for the next file
        inputName = outputName
        i += 1

# close all the files in the dict
for f in files:
    files[f].close()
