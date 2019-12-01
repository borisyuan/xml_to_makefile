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
    projpath = []
    count = len(projpath)
    print(count)
    if buildscript[0] == 'all':
        for proj in projects :
            if proj == projects[0]:
                projscript.append(abs_path)
                continue
            projpath = []
            search_target(abs_path, proj, projpath)
            if len(projpath) == 0:
                print(proj, "is not existed!")
            else:
                for path in projpath:
                    print(":::",path)
                    if check_proj_file(path, files):
                        projscript.append(proj)
                        projscript.append(path)
                        print(proj,path)
                
    return True 

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

    check_project(buildscript, files, projscript)
    print(projscript)

if __name__ == '__main__':
    main(sys.argv)
