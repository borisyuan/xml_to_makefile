# -*- coding = UTF-8 -*-
#!/usr/bin/python3

import os, sys, projectparser

def main(argv):
    print("*************************")
    print("\'", argv[0],"\' is running to generate makefile for:", argv[1])
    print("*************************")
    print("step 1: finding the projects space and target ......")
    build = []
    projectparser.listbuild(build)
    #print(build)
    space = os.path.join(build[0], build[1])
    abs_path = os.path.abspath(space)
    #print(abs_path)
    #print(os.path.isdir(abs_path))
    if (True == os.path.isdir(abs_path)):
        print("find the space dir:", abs_path)
        projects = []
        projectparser.listproject(projects)
        print(projects)
    else :
        print("space dir can not find!")

if __name__ == '__main__':
    main(sys.argv)
