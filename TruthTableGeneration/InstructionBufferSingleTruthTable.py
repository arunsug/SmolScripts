"""
Created on Sat Dec 24 11:51:11 2022
Generates a truth table given a state of two instrcuction buffers and a
requested number of instructions then how much do we send and how many valid 
bits are left in each buffer

"""

# int valid1: number of valid bits in the first buffer
# [bool] blockSize1: true if the next block is 4 bytes False if 2
# int valid2: number of valid bits in the second buffer
# [bool] blockSize2: true if the next block is 4 bytes False if 2
# int sendRequest: number of bits being requested
# return: number of valid bits used and sent from each buffer
def numSent(valid1, valid2, blockSize1, blockSize2, sendRequest):
    sendCount1 = 0
    sendCount2 = 0
    #print(valid1, valid2, blockSize1, blockSize2)
    for i in range(sendRequest):
        if valid1 > 1 and blockSize1 and blockSize1[-1]:
            # Handle 4 byte instruction from first buffer
            valid1 -= 2
            sendCount1 += 2
            blockSize1.pop()
        elif valid1 > 0 and blockSize1 and not blockSize1[-1]:
            # Handle 2 byte instruction from first buffer
            valid1 -= 1
            sendCount1 += 1
            blockSize1.pop()
        elif valid1 == 1 and valid2 > 0 and blockSize1 and blockSize1[-1]:
            # Handle split 4 byte instruction 
            valid1 -= 1
            sendCount1 += 1
            valid2 -= 1
            sendCount2 += 1
            blockSize1.pop()
        elif valid2 > 1 and blockSize2 and blockSize2[-1]:
            # Handle 4 byte instruction from second buffer
            valid2 -= 2
            sendCount2 += 2
            blockSize2.pop()
        elif valid2 > 0 and blockSize2 and not blockSize2[-1]:
            # Handle 2 byte instruction from second buffer
            valid2 -= 1
            sendCount2 += 1
            blockSize2.pop()
        else:
            return sendCount1, valid1, sendCount2, valid2
    return sendCount1, valid1, sendCount2, valid2

validLength = 16
maxSendRequest = 8
formatString = "{:016b}"
f = open("table.txt" , "w+")
seen= {(0, "?"*validLength, '?'*validLength, "?"*validLength, "?"*validLength),
     ("?", "0"*validLength, '?'*validLength, "?"*validLength, "?"*validLength)}
repeats = {}
# loop thorugh the amount being asked for
for send in range(1, maxSendRequest+1):
    # loop the the first first valid amounts
    for v1 in range(0, validLength):
        vint = 1
        vint <<= v1
        # format the string
        validString = formatString.format(vint)
        validString = validString[:validLength-v1] + '?'*v1

        # handle if valid is 0
        if v1 == validLength:
            validString = "0"*validLength
            v1 = -1
        # cycle through the block lengths
        bits= (2**min(v1+1, send*2)) - 1
        for b1 in range(bits):
            blockSize = []
            bits = b1
            l = 0
            blockString = formatString.format(b1)
            while l  < v1+1 and len(blockSize) < send:
                if bits & 1:
                    blockSize.append(True)
                    bits >>= 2
                    l += 1
                    if l != validLength:
                        blockString = blockString[:(validLength-1)-l] + '?' +blockString[validLength-l:]
                else:
                    blockSize.append(False)
                    bits >>= 1
                l += 1
            # if our index is greater than what is valid the instruction is split
            isSplitInstruction = l > v1 + 1
            blockSize.reverse()
            wildcardAfter = min(v1+1, send*2, l)
            blockString = "?"*(validLength-wildcardAfter) + blockString[validLength-wildcardAfter:]
            # cycle through the second valid options
            for v2 in range(0, validLength+1):#(send-len(blockSize))*2 + 1):
                vint2 = 1
                vint2 <<= v2
                validString2 = formatString.format(vint2)
                validString2 = validString2[:validLength-v2] + '?'*v2
                wildcardAfter = (send - len(blockSize)) * 2
                 
                if v2 == validLength: 
                    validString2 = "0"*validLength
                    v2 = -1
                # cycle thorugh the second blockSizes
                bits2 = (2**min(v2+1, (send - len(blockSize))*2))
                for b2 in range(bits2):
                    blockSize2 = []
                    bits2 = b2
                    l2 = 0
                    blockString2 = formatString.format(b2)
                    if bits2 == (2**(v2+1)):
                        blockString = "?"*validLength
                    if isSplitInstruction:
                        blockString2 = blockString2[:validLength-1] +"?"
                        l2 = 1
                        bits2 >>= 1
                    while l2  < v2+1 and len(blockSize)+len(blockSize2) < send:
                        if bits2 & 1:
                            blockSize2.append(True)
                            bits2 >>= 2
                            l2 += 1
                            if l2 != validLength:
                                blockString2 = \
                                blockString2[:(validLength-1)-l2] + '?' + \
                                blockString2[validLength-l2:]
                        else:
                            blockSize2.append(False)
                            bits2 >>= 1
                        l2 += 1

                    wildcardAfter = min(v2+1, (send - len(blockSize)) * 2, l2)
                    blockString2 = "?"*(validLength-wildcardAfter) + \
                    blockString2[validLength-wildcardAfter:]
                    
                    blockSize2.reverse()
                    copyBlockSize = blockSize[:]
                    copyBlockSize2 = blockSize2[:]
                    result = numSent(v1+1, v2+1, copyBlockSize, blockSize2, 
                                     send)
                    inputs = (send, validString, validString2, blockString, 
                              blockString2)
                    entry = (inputs, result)
                    if entry not in seen:
                        count += 1
                        f.write(str(entry) + "\n")
                        if inputs in repeats:
                            # if this happens that means there is a bug
                            print(repeats[inputs], result)
                        else:
                            repeats[inputs] = result
                        
                        seen.add(entry)
f.close()
print("there are", len(seen), "rows") 