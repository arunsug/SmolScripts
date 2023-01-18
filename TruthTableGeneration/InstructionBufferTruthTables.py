"""
Created on Mon Dec 26 22:25:59 2022

The script two truth tables written to a file table1.txt and table2.txt.
The tables are to quickly index the final state a buffer given an input state
details on the inputs and outputs are in the comments.

"""
import math

# processes buffer info and returns the state it will reach after sending the
# instrcutions that it can
# int valid: the number of valid bits in the buffer
# [bool] blockSize: size of each instruction in the buffer True=4, False=2
# int sendRequest: the number of instructions that have been requested
# [bool] hasSplit: hasSplit[0] True if there is a preceding buffer
#                  hasSplit[1] True if previous buffer has split intstruction
# return: 
#   int sendCount: the number of bits sent
#   int valid: the number of remaining valid bits
#   int sendRequest: the number of remaing instructions to send
#   bool isSplit/UsedSplit: if hasSplit[0] is true retrun usedSplit indicating 
#                           if the rest of the instruction was sent. If not 
#                           returns if there is a split instruction
#   ((bool, bool, int),) instructionData: (is it split, len 2 or 4, position) 
def numSent(valid, blockSize, sendRequest, hasSplit):
    sendCount = 0
    isSplit = False
    usedSplit = False
    instructionData = []

    # handle if there is a split instruction
    if hasSplit[1] and valid > 0:
        valid -= 1
        sendRequest -= 1
        blockSize.pop()
        usedSplit = True
        sendCount += 1
    # processes and attempt to send the requested number of instructions 
    for i in range(sendRequest):
        if valid > 1 and blockSize and blockSize[-1]:
            # handle 4 byte instruction
            instructionData.append((False, blockSize[-1], sendCount))
            valid -= 2
            sendCount += 2
            sendRequest -= 1
            blockSize.pop()
        elif valid > 0 and blockSize and not blockSize[-1]:
            # handle 2 byte instruction
            instructionData.append((False, blockSize[-1], sendCount))
            valid -= 1
            sendCount += 1
            sendRequest -= 1
            blockSize.pop()
        elif valid == 1 and blockSize and blockSize[-1]:
            # handle if an instruction is split
            instructionData.append((True, blockSize[-1], sendCount))
            isSplit = True
            break
        else:
            # if none of the other cases happen we are done and exit early
            break
        
    if hasSplit[0]:
        # if this is the second buffer return if we used a split instruction
        # and don't return sendRequest
        return sendCount, valid, usedSplit, tuple(instructionData),
    else:
        # if not return if there was a split
        return sendCount, valid, sendRequest, isSplit, tuple(instructionData),

# generates a table of buffer input states and the resulting output states
# [bool, bool] isSplit: first bool is there a preceeding buffer
#                       second is there a split instruction we need to handle
# range(int) sendRange: the possible number of instructions needed
# range(int) validRange: the possible number of valid bits
# int validLength: number of bits in the valid buffer
# return: set table:
def generateTable(isSplit, sendRange, validRange, validLength):
    table = set()
    # cycle through the send amounts
    for send in sendRange:
        # cycle through the valid amounts
        for v1 in validRange:
            vint = 1
            vint <<= v1
            # format the string for the valid buffer
            validString = validFormatString.format(vint)
            validString = validString[:validLength-v1] + '?'*v1
            if v1 == validLength:
                validString = "0"*validLength
                v1 = -1
            # cycle through the block lengths
            bits= (2**min(v1+1, send*2))
            for b1 in range(bits):
                # create an array of the block lenghts values for ease of use
                blockSize = []
                l = 0
                # format the string of block lengths
                blockString = validFormatString.format(b1)
                # handle if there is a split instruction in the previous buffer
                if isSplit[1]:
                    l += 1
                    b1 >>= 1
                    blockSize.append(None)
                    blockString = blockString[:validLength-1] + '?'
                # loop through to wildcard what can be wildcarded and fill the
                # blockSize list
                while l  < v1+1 and len(blockSize) < send:
                    if b1 & 1:
                        # add a True indicating length 4 instruction
                        blockSize.append(True)
                        b1 >>= 2
                        l += 1
                        # if the value is 1  wildcard the next bi
                        blockString = blockString[:(validLength-1)-l] + '?' + \
                                      blockString[validLength-l:]
                    else:
                        # add a False indicating length 2 instruction
                        blockSize.append(False)
                        b1 >>= 1
                    l += 1
                # flip list so pop access values at the start of the buffer
                blockSize.reverse()
                # find the smallest value we can wildcard after and wildcard
                wildcardAfter = min(v1+1, send*2, l)
                blockString = "?"*(validLength-wildcardAfter) + \
                              blockString[validLength-wildcardAfter:]
                # calculate the state of the buffer after a cycle
                result = numSent(v1+1, blockSize, send, isSplit)
                # create input tuple
                if isSplit[0]:
                    inputs = (send, validString, blockString, isSplit[1])
                else:
                    inputs = (send,  validString, blockString)
                # if the entry is in the table don't readd it
                if (inputs, result) not in table:
                    table.add((inputs, result))
    return table

print("Generating Truth Tables")
maxSendRequest = 8
validLength = maxSendRequest*2
validFormatString = "{:0"+ str(validLength) +"b}"
validPreString = str(validLength) + "\'b"

sendStringLength = int(math.log(maxSendRequest, 2) + 1)
sendFormatString = str(sendStringLength)+"\'b{:0" + str(sendStringLength)+"b}"

validNumLength = int(math.log(validLength, 2)) + 1
validNumFormatString = str(validNumLength)+"\'b{:0" + str(validNumLength)+"b}"

falseString = "1\'b0"
trueString = "1\'b1"

# table 1 represents the first buffer
# no preceding buffer and at least 1 instruction will be requested and at least
# one valid bit will be present
print("Generating table 1...")
table1 = generateTable([False, False], range(1, maxSendRequest+1), 
                       range(0, validLength), validLength)
# Add entries to handle impossible inputs
table1.add(((0,"?"*validLength, "?"*validLength), (0,0,0,False,())))
for i in range(1, maxSendRequest+1):
    table1.add(((i, "0"*validLength, "?"*validLength), (0,0,0,False,())))
for i in range(maxSendRequest+1, maxSendRequest*2):
    table1.add(((i,"?"*validLength, "?"*validLength),(0,0,0,False,())))

# table 2 represents the second buffer
# there is a preceding buffer tha can have carry over a split instruction
# if there cannot be 0 instructions to send if there is a split and there
# cannot be 4 instructions to send if there is no split
print("Generating table 2...")
table2 = generateTable([True, True], range(1, maxSendRequest+1), 
                       range(0, validLength+1), validLength)
table2.update(generateTable([True, False], range(0, maxSendRequest), 
                            range(0, validLength+1), validLength))
# Add entries to handle impossible inputs
table2.add(((maxSendRequest, "?"*validLength, "?"*validLength, False), (0,0,False,())))
table2.add(((0, "?"*validLength, "?"*validLength, True), (0,0,False,())))
for b in [True, False]:
    for i in range(maxSendRequest+1, maxSendRequest*2):
        table2.add(((i,"?"*validLength, "?"*validLength, b),(0,0,False,())))

print("Number of entries:     Table1", len(table1), "    Table2", len(table2))

f = open("Table1.txt" , "w+")

# helper function for converting instruction data into a string
# ((bool, bool, bool, int), ...) instructionData: the instruction data
# int numInstructions: The maximum number of instructions we expect to see in InstructionData
def formatInstructionData(instructionData, numInstructions):
    instructionDataString = ""
    positionLength = int(math.log(validLength,2))
    positionFormatString = "{:0" + str(positionLength)+"b}"
    i = 0
    # the format is 3 bits indicating valid, split, length, then the poistion bits which depends on 
    # the buffer size
    for instruction in instructionData:
        isValid = "1"
        isSplit = "1" if instruction[0] else "0"
        isFourLength = "1" if instruction[1] else "0"
        position = positionFormatString.format(instruction[2])
        instructionDataString +=  ", " + str(3+positionLength) + "\'b" + isValid + isSplit + \
                                    isFourLength + position
        i += 1
    
    # fill in the rest of the entries as not valid if there are no more instructions
    for i in range(i, numInstructions):
        instructionDataString += ", " + str(3+positionLength) + "\'b000" + "0"*positionLength
    return instructionDataString
    
# sample format
#{4'b0110, 16'b0001????????????, 16'b001????????0?100}: outmask = {4'b0100, 4'b0001, 4'b0000, 1'b0};

print("Writing truth table 1...")
table1 = list(table1)
table1.sort()
for entry in table1:
    row = "{"+sendFormatString.format(entry[0][0])+", "+ \
            validPreString+entry[0][1]+", " + validPreString + entry[0][2] + \
            "}: outmask = {"+validNumFormatString.format(entry[1][0]) + \
            ", " + validNumFormatString.format(entry[1][1]) + ", " + \
            sendFormatString.format(entry[1][2]) + ", " + \
            (trueString if entry[1][3] else falseString) + \
            formatInstructionData(entry[1][4], maxSendRequest) + "}\n"
    f.write(row)
f.close()

f = open("Table2.txt" , "w+")
print("Writing truth table 2...")
table2 = list(table2)
table2.sort()
for entry in table2:
    row = "{"+sendFormatString.format(entry[0][0])+", "+ \
            validPreString+entry[0][1]+", " + validPreString + entry[0][2] + \
            ", " + (trueString if entry[0][3] else falseString) + \
            "}: outmask = {"+validNumFormatString.format(entry[1][0]) + \
            ", " + validNumFormatString.format(entry[1][1]) + ", " + \
            (trueString if entry[1][2] else falseString) + \
            formatInstructionData(entry[1][3], maxSendRequest-1) +"}\n"
    f.write(row)
f.close()

print("Done!")   



    

