"""
Created on Tues Jan 24 11:47 2023

Generates a  mesh file of switches. For linking hubs and cpus on a chip.

"""

# the mesh size
x = 5
y = 6

meshFile = open("MeshFile.v", "w+")

cpuModuleInOutString = "{put} {put}_cpu{index}_{loc}, "
hubModuleInOutString = "{put} {put}_hub{index}_{loc}, "


meshFile.write("module mesh(")
for i in range(x):
    for j in range(y):
        locString = str(i)+str(j)
        meshFile.write("\n  ")
        for c in range(5):
            meshFile.write(cpuModuleInOutString.format(put="input", index=c, loc=locString))
        for c in range(5):
            meshFile.write(cpuModuleInOutString.format(put="output", index=c, loc=locString))
        meshFile.write("\n  ")
        for h in range(5):
            meshFile.write(hubModuleInOutString.format(put="input", index=h, loc=locString))
        for h in range(5):
            meshFile.write(hubModuleInOutString.format(put="output", index=h, loc=locString))

meshFile.write("\n)\n\n")

switchInOutString = "  .{put}{axis}{dir}(connect{axis}{sloc}_{eloc}),\n"
switchConnectString = "logic connect{axis}{sloc}_{eloc};\n"

cpuInOutString = ".{put}_cpu{index}({put}_cpu{index}_{loc}), "
hubInOutString = ".{put}_hub{index}({put}_hub{index}_{loc}), "

for i in range(x):
    for j in range(y):
        locString = str(i) + str(j)

        if i+1 < x:
            meshFile.write(switchConnectString.format(axis="x", sloc=str(i+1)+str(j), eloc=locString))
            meshFile.write(switchConnectString.format(axis="x", sloc=locString, eloc=str(i+1)+str(j)))
        if j+1 < y:
            meshFile.write(switchConnectString.format(axis="y", sloc=str(i)+str(j+1), eloc=locString))
            meshFile.write(switchConnectString.format(axis="y", sloc=locString, eloc=str(i)+str(j+1)))

        meshFile.write("Switch switch" + locString + "(\n")

        if i-1 > 0:
            meshFile.write(switchInOutString.format(put="input",axis="x",dir=0,sloc=str(i-1)+str(j), 
                            eloc=locString))
            meshFile.write(switchInOutString.format(put="output", axis="x", dir=0, sloc=locString, 
                            eloc=str(i-1)+str(j)))

        if i+1 < x:
            meshFile.write(switchInOutString.format(put="input",axis="x",dir=1,sloc=str(i+1)+str(j), 
                            eloc=locString))
            meshFile.write(switchInOutString.format(put="output", axis="x", dir=1, sloc=locString, 
                            eloc=str(i+1)+str(j)))

        if j-1 > 0:
            meshFile.write(switchInOutString.format(put="input",axis="y",dir=0,sloc=str(i)+str(j-1), 
                            eloc=locString))
            meshFile.write(switchInOutString.format(put="output", axis="y", dir=0, sloc=locString, 
                            eloc=str(i)+str(j-1)))

        if j+1 < y:
            meshFile.write(switchInOutString.format(put="input",axis="y",dir=1,sloc=str(i)+str(j+1), 
                            eloc=locString))
            meshFile.write(switchInOutString.format(put="output", axis="y", dir=1, sloc=locString, 
                            eloc=str(i)+str(j+1)))

        meshFile.write("  ")
        for c in range(5):
            meshFile.write(cpuInOutString.format(put="input", index=c, loc=locString))
        for c in range(5):
            meshFile.write(cpuInOutString.format(put="output", index=c, loc=locString))
        meshFile.write("\n  ")
        for h in range(5):
            meshFile.write(hubInOutString.format(put="input", index=h, loc=locString))
        for h in range(5):
            meshFile.write(hubInOutString.format(put="output", index=h, loc=locString))        
        meshFile.write("\n")

        meshFile.write(");\n\n")

meshFile.close()
