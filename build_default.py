# -*- coding = UTF-8 -*-
#!/usr/bin/python3

import os
import sys
from custom_cfg import BuildInfo
from proj_parse import ProjParse
from custom_make import AutoMake

targetpath = []
def search_target(startpath, target):
    global targetpath
    if not os.path.isdir(startpath) :
        print('invalid startpath:', startpath)
        return targetpath

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
            search_target(subdirpath, target)

    return targetpath

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

def main(argv):
    Custom = BuildInfo(sys.argv)
    Custom.cfgfile = 'custom_cfg.xml'
    Custom.sysargv_parse()
    Custom.config_parse()
    print(Custom.info)
    print(Custom.targetlist)
    for target in Custom.targetlist:
        Custom.info['TargetDir'] = os.path.join(Custom.info['TargetPath'], target)
        print("parse target:", target, 'in path ' + Custom.info['TargetPath'])
        parser = ProjParse(Custom.info)
        make = AutoMake(parser)
        make.autogen()
        make.run_make()
    return

if __name__ == '__main__':
    main(sys.argv)
