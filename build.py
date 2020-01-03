# -*- coding = UTF-8 -*-
#!/usr/bin/python3

import os, sys, projectparser

def search_target(startpath, target, targetpath):
    if not os.path.isdir(startpath) :
        print('invalid startpath:', startpath)
        return False

    listsubdir =  os.listdir(startpath)

    #search dir for all targets matched
    for subdir in listsubdir:
        if subdir == target :
            print("find target:", startpath, target)
            targetpath.append(os.path.join(startpath, target))
            #print(targetpath)
        subdirpath = os.path.join(startpath, subdir)
        if os.path.isdir(subdirpath) :
            #print(subdirpath)
            search_target(subdirpath, target, targetpath)

    return True

def is_file_existed(path, filename):
    if not os.path.isdir(path) :
        print(path)
        return False

    listsubdir =  os.listdir(path)
    for subdir in listsubdir:
        if subdir == filename :
            subdirpath = os.path.join(path, subdir)
            if os.path.isfile(subdirpath) :
                print("file existed:", filename)
                return True

    return False

def check_proj_file(path, files):
    count = len(files)
    check = []
    for filename in files:
        #print(filename)
        if is_file_existed(path, filename): 
            check.append('match')
            continue
    if count == len(check):
        return True
    else :
        return False

def check_project(buildscript, files, projscript):
    if len(buildscript) < 1:
        print("Not any build info!")
        return False
    build = []
    projects = []
    projectparser.listbuild(build)
    #print(build)
    if len(build) < 3:
        print("Get build info failed!")
        return False
    if build[2] == "GNU MCU Eclipse Project":
        files.append('.project')
        files.append('.cproject')
    else:
        print("Not support!")
        return False

    space = os.path.join(build[0], build[1])
    abs_path = os.path.abspath(space)
    #print(abs_path)
    #print(os.path.isdir(abs_path))
    if not os.path.isdir(abs_path):
        print("Space dir can not find")
        return False

    print("find the space dir:", abs_path)
    projectparser.listproject(projects)
    print(projects)
    #projpath = []
    #count = len(projpath)
    #print(count)
    #the build generate operation need a default or existed dir
    #do not support to make new dir
    if not os.path.isdir(projects[0]):
        build_gen  = os.path.join(abs_path, 'build')
        print("generate to:", build_gen)
        buildscript.append(build_gen)
    else:
        print("generate to existed dir:", projects[0])
        buildscript.append(projects[0])
     
    for proj in projects :
        if proj == projects[0]:
            projscript.append(abs_path)
            continue
        SearchStatus = False
        if buildscript[0] == 'all' or buildscript[0] == proj: 
            SearchStatus = True
        if SearchStatus == True:
            projpath = []
            search_target(abs_path, proj, projpath)
            if len(projpath) == 0:
                print(proj, "is not existed!")
            else:
                for path in projpath:
                    print(":::", path, ":::")
                    if check_proj_file(path, files):
                        projscript.append(proj)
                        projscript.append(path)
                        print(proj,path)
                
    return True 

def is_target_file(clist, assemble, filename):
    if os.path.isfile(filename):
        filetype = os.path.splitext(filename)
        #print(filetype)
        if filetype[1] == ".S" or filetype[1] == ".s":
            assemble.append(filename)
        else :
            clist.append(filename)
        return True
    else: return False

def check_target_files(clist, assemble, filescript):
    if not os.path.isfile(filescript[0]):
        print("need a file path:", filescript[0])
        return False
    #get filelist and check existed
    projectparser.listfile(filescript)
    #print(filescript)
    for i in range(2, len(filescript)):
        if not is_target_file(clist, assemble, filescript[i]):
            #clist.append(filescript[i])
        #else :
            strings = filescript[i]
            listtemp = strings.split('/',1)
            pathtemp = os.path.split(filescript[0])
            if listtemp[0] == "..":
                filepath = os.path.join(pathtemp[0], filescript[i])
                is_target_file(clist, assemble, filepath)
            else :
                symbol = listtemp[0].split('-', 2)
                #print(symbol)
                if symbol[0] == "PARENT" and symbol[2] == "PROJECT_LOC":
                    num = int(symbol[1])
                    filenewpath = pathtemp[0]
                    for j in range(0, num):
                        temp = []
                        temp = os.path.split(filenewpath)
                        filenewpath = temp[0]
                    filenewpath = os.path.join(filenewpath, listtemp[1])
                    #print(filenewpath)
                    is_target_file(clist, assemble, filenewpath)

    return True

def autogen_makefile(buildscript, MakePara, clist, assemble):
    dependencies = '-include $(wildcard $(BUILD_DIR)/*.d)\n'
    print("path:",buildscript[1], "is the build dir")
    if os.path.isdir(buildscript[1]):print("the dir:",buildscript[1], "is existed!")
    else:os.mkdir(buildscript[1])
    print("Now creat the target dir for", MakePara['TARGET'], ":")
    targetdir = MakePara['TARGET'].replace('TARGET = ','')
    targetpath = os.path.join(buildscript[1], targetdir)
    if os.path.isdir(targetpath):
        print("the target dir:",targetpath, "is existed!")
    else:os.mkdir(targetpath)

    print("Autogenerate the Makefile ...............")

    filepath = os.path.join(targetpath, "Makefile")
    #fd = os.open(filepath,os.O_RDWR|os.O_CREAT)
    fd = open(filepath,"w+")
    fd.write("############## This file autogenerated by tool: build.py ##############")
    fd.write("\n\n")
    fd.write(MakePara['TARGET'] + "\n\n")
    fd.write("DEBUG = 1\n")
    fd.write("ifeq (${DEBUG}, 1)\n")
    fd.write("BUILD_DIR = debug\nelse\nBUILD_DIR = release\nendif\n\n")
    fd.write(MakePara['OPT'] + "\n\n")
    fd.write("C_SOURCES = ")
    for cfile in clist:
        fd.write("\\\n" + cfile)
    fd.write("\n")
    fd.write("AS_SOURCES = ")
    for asfile in assemble:
        fd.write("\\\n" + asfile)
    fd.write("\n\n")
    fd.write(MakePara['PREFIX'] + "\n\n")
    fd.write("ifdef GCC_PATH")
    fd.write(MakePara['CC'].replace("CC = ","\nCC = $(GCC_PATH)/"))
    fd.write(MakePara['AS'].replace("AS = ","\nAS = $(GCC_PATH)/"))
    fd.write(MakePara['CP'].replace("CP = ","\nCP = $(GCC_PATH)/"))
    fd.write(MakePara['SZ'].replace("SZ = ","\nSZ = $(GCC_PATH)/"))
    fd.write("\nelse\n")
    fd.write(MakePara['CC'] + "\n")
    fd.write(MakePara['AS'] + "\n")
    fd.write(MakePara['CP'] + "\n")
    fd.write(MakePara['SZ'] + "\n")
    fd.write("endif\n\n")
    fd.write("HEX = $(CP) -O -ihex\n")
    fd.write("BIN = $(CP) -O binary -S\n\n")
    fd.write(MakePara['THUMB'] + "\n")
    fd.write(MakePara['CPU'] + "\n")
    fd.write(MakePara['FPU'] + "\n")
    fd.write(MakePara['FLOAT_ABI'] + "\n")
    fd.write(MakePara['MCU'] + "\n")
    fd.write(MakePara['AS_DEFS'] + "\n")
    fd.write(MakePara['C_DEFS'] + "\n")
    fd.write(MakePara['AS_INCLUDES'] + "\n")
    fd.write(MakePara['C_INCLUDES'] + "\n")
    fd.write(MakePara['TOOL_FLAGS'] + "\n")
    fd.write(MakePara['ASFLAGS'] + "\n")
    fd.write(MakePara['CFLAGS'] + "\n")
    fd.write("ifeq (${DEBUG}, 1)\n")
    fd.write(MakePara['DEBUG_FLAG'] + "\nendif\n\nCFLAGS += -MMD -MP -MF\"$(@:%.o=%.d)\"\n")
    fd.write(MakePara['LDSCRIPT'] + "\n")
    fd.write("LIBS = \nLIBDIR = \n")
    fd.write(MakePara['LDFLAGS'] + "\n")
    fd.write("all: $(BUILD_DIR)/$(TARGET).elf $(BUILD_DIR)/$(TARGET).hex $(BUILD_DIR)/$(TARGET).bin\n")
    fd.write("OBJECTS = $(addprefix $(BUILD_DIR)/,$(notdir $(C_SOURCES:.c=.o)))\nvpath %.c $(sort $(dir $(C_SOURCES)))\n")
    fd.write("OBJECTS += $(addprefix $(BUILD_DIR)/,$(notdir $(AS_SOURCES:.S=.o)))\nvpath %.S $(sort $(dir $(AS_SOURCES)))\n\n")
    fd.write("$(BUILD_DIR)/%.o: %.c Makefile | $(BUILD_DIR) \n\t$(CC) -c $(CFLAGS) -Wa,-a,-ad,-alms=$(BUILD_DIR)/$(notdir $(<:.c=.lst)) $< -o $@\n\n")
    fd.write("$(BUILD_DIR)/%.o: %.S Makefile | $(BUILD_DIR)\n\t$(AS) -c $(CFLAGS) $< -o $@\n\n")
    fd.write("$(BUILD_DIR)/$(TARGET).elf: $(OBJECTS) Makefile\n\t$(CC) $(OBJECTS) $(LDFLAGS) -o $@\n\t$(SZ) $@\n\n")
    fd.write("$(BUILD_DIR)/%.hex: $(BUILD_DIR)/%.elf | $(BUILD_DIR)\n\t$(HEX) $< $@\n\n")
    fd.write("$(BUILD_DIR)/%.bin: $(BUILD_DIR)/%.elf | $(BUILD_DIR)\n\t$(BIN) $< $@\n\n")
    fd.write("$(BUILD_DIR):\n\tmkdir $@\n\n")
    fd.write("clean:\n\t-rm -fR $(BUILD_DIR)\n\n")
    fd.write(dependencies)
    fd.close()

    print("Makefile generated!")

#the function parse the system input
def sysargv_parser(sysargv):
    if len(sysargv) < 2:
        BuildPara['BUILD_TARGET'] = "all"
    else:
        if syargv[1] == "-h" or sysargv[1] == "--help":
            print("help info:")
            print(">python3 build.py targetname toolpath buildtype")
        if syargv[1] == "-r" or sysargv[1] == "--remove":
            print("remove build:")
            print("waiting for adding this feature in the next version.")
        for i in rang(1, len(sysargv)):
            if syargv[i] == "-h":
                return

def main(argv):
    buildscript = []
    files = []
    projscript = []
    print("*************************")
    print("\'", end="")
    print(argv[0], end="")
    print("\' is running to generate makefile for: ",end="")
    if len(argv) < 2:
        print("all")
        buildscript.append('all')
    else:
        print(argv[1])
        buildscript.append(argv[1])
    print("*************************")
    print("step 1: finding the projects space and target ......")

    Status = check_project(buildscript, files, projscript)
    print("projects status:",Status)
    proj_num = int((len(projscript) - 1) / 2)
    print("find",proj_num,"projects:",projscript)
    size_proj = 2
    for i in range(0,proj_num):
        filescript = []
        makescript = []
        n = (i * size_proj) + 1
        m = (i * size_proj) + 2
        filescript.append(os.path.join(projscript[m], files[0]))
        filescript.append(projscript[0])
        makescript.append(os.path.join(projscript[m], files[1]))
        makescript.append(projscript[0])
        #print(makescript)
        #print(files)
        print("parse project", (i + 1), filescript, makescript)
        clist = []
        #inclist = []
        assemble = []
        MakePara = {}
        check_target_files(clist, assemble, filescript)
        print(clist, "\n", assemble)
        MakePara = projectparser.listpara(makescript)
        #print(makescript)
        print(MakePara)
        print(buildscript)
        autogen_makefile(buildscript, MakePara, clist, assemble)


if __name__ == '__main__':
    main(sys.argv)
