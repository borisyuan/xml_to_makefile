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
    for i in range(2, len(buildscript)):
        if makescript[i] == "configuration":
            start_parse = True
            continue
        if makescript[i] == "toolChain":
            break
    dependencies = '-include $(wildcard $(BUILD_DIR)/*.d)\n'

def sysargv_parser(sysargv):
    if len(sysargv) < 2:
        BuildPara['BUILD_TARGET'] = "all"
    else:
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
        print(makescript)
        print(MakePara)
        print(buildscript)
        autogen_makefile(buildscript, makescript, clist, assemble)
        #generate_makefile(MakePara)


if __name__ == '__main__':
    main(sys.argv)
