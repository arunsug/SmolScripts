""" 
Created on Friday Feb 17 10:38 2023

Check how many elements are covered in our table.
"""

import threading

table1Size = 0
table2Size = 0

def CheckTruthTable(tableFileName, table1):
    covered = 0
    rows = 0
    with open(tableFileName, "r") as tableFile:
        for line in tableFile:
            questionMarkCount = line.count("?")
            covered += 2 ** questionMarkCount
            rows += 1
            
    if table1:
        global table1Size
        table1Size = covered
    else:
        global table2Size
        table2Size = covered

t1 = threading.Thread(target=CheckTruthTable, args=("Table1.txt", True,))
t2 = threading.Thread(target=CheckTruthTable, args=("Table2.txt", False,))
t1.start()
t2.start()
t1.join()
t2.join()

print("Table One Covered:", table1Size == 68719476736)
print("Table Two Covered:", table2Size == 137438953472)
