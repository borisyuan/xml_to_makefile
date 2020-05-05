# -*- coding: UTF-8 -*-
#!/usr/bin/python3

import xml.sax
import sys
import os

class CustomCfgHandler(xml.sax.ContentHandler):
    def __init__(self):
        self.CurrentData = ""
        self.submodule = ""
        self.submodulelist = []
        self.buildinfo = {}

    def startElement(self, tag, attributes):
        self.CurrentData = tag
        if tag == "ProjectScript":
            print("Start to search projects:")
            if attributes.__contains__('BuildRule'):
                self.buildinfo['BuildRule'] = attributes['BuildRule']
                print ("Build Rule:", self.buildinfo['BuildRule'])
            if attributes.__contains__('BuildPath'):
                self.buildinfo['BuildPath'] = attributes['BuildPath']
                print ("Build Path:", self.buildinfo['BuildPath'])
            if attributes.__contains__('SubModulePath'):
                self.buildinfo['SubModulePath'] = attributes['SubModulePath']
                print ("SubModule Path:", self.buildinfo['SubModulePath'])
        if tag == "ToolScript":
            if attributes.__contains__('GccPath'):
                self.buildinfo['GccPath'] = attributes['GccPath']
                print("default gcc tool path:", self.buildinfo['GccPath'])

    def endElement(self, tag):
        if self.CurrentData == "SubModule":
            print ("SubModule:", self.submodule)
            self.submodulelist.append(self.submodule)
        self.CurrentData = ""

    def characters(self, content):
        if self.CurrentData == "ProjName":
            self.buildinfo['ProjName'] = content
        if self.CurrentData == "ProjPath":
            self.buildinfo['ProjPath'] = content
        if self.CurrentData == "ProjectParser":
            self.buildinfo['ProjectParser'] = content
        if self.CurrentData == "SubModule":
            self.submodule = content

#this class parse the sys.argv and custom config file
#the result saved in self.info and self.targetlist
class BuildInfo(object):
    def __init__(self, sys_argv):
        self.cfgfile = ''
        self.sysargv = sys_argv
        self.targetlist = []
        self.info = {}

    def sysargv_parse(self):
        if len(self.sysargv) < 2:
            self.info['BUILD_TARGET'] = "all"
            self.info['BUILD_TYPE'] = "debug"
            #if no input cmd, then execute the default process: build all target
            return self.info
        else:
            if self.sysargv[1] == "-h" or self.sysargv[1] == "--help":
                print("help info:")
                print(">python3 build.py targetname toolpath buildtype")
                return self.info
            elif self.sysargv[1] == "-r" or self.sysargv[1] == "--remove":
                print("remove build:")
                print("waiting for adding this feature in the next version.")
                return self.info

            elif self.sysargv[1].startswith('-'):
                print("Can not parse", self.sysargv[1])
                print("waiting for adding this feature in the next version.")
                return self.info
            else:
                self.info['BUILD_TARGET'] = self.sysargv[1]
                for i in range(2, len(self.sysargv)):
                    if self.sysargv[i] == "debug" or self.sysargv[i] == "release":
                        self.info['BUILD_TYPE'] = sysargv[i]
                    elif self.sysargv[i].startswith('GCC_PATH='):
                        self.info['GCC_PATH'] = sysargv[i]
                    else:
                        self.info['BUILD_TARGET'] = sysargv[i]
                if not self.info.__contains__('BUILD_TYPE'):
                    self.info['BUILD_TYPE'] = "debug"
                return self.info

    def config_parse(self):
        if not os.path.isfile(self.cfgfile):
            print("Can not find custom config file:",self.cfgfile)
            return
        print("parse source:", self.cfgfile)
        cfgpath = os.path.split(os.path.abspath(self.cfgfile))[0]
        os.chdir(cfgpath)
        print("current dir:", os.getcwd())
        parser = xml.sax.make_parser()
        parser.setFeature(xml.sax.handler.feature_namespaces, 0)
        Handler = CustomCfgHandler()
        parser.setContentHandler(Handler)
        parser.parse(self.cfgfile)
        print(Handler.buildinfo)
        if Handler.buildinfo.__contains__('ProjName') and Handler.buildinfo.__contains__('ProjPath'):
            projdir = os.path.join(os.path.abspath(Handler.buildinfo['ProjPath']), Handler.buildinfo['ProjName'])
            if os.path.isdir(projdir):
                self.info['ProjDir'] = projdir
                print("find project dir:", projdir)
            else:
                print("project dir error:", projdir)
                return False
        else:
            print("no project to buid!")
            return False
        if Handler.buildinfo.__contains__('BuildPath'):
            if os.path.isdir(Handler.buildinfo['BuildPath']):
                self.info['BuildPath'] = os.path.abspath(Handler.buildinfo['BuildPath'])
            elif Handler.buildinfo['BuildPath'].startswith('${ProjDir}'):
                buildpath = os.path.join(self.info['ProjDir'], Handler.buildinfo['BuildPath'].replace('${ProjDir}/', ''))
                self.info['BuildPath'] = os.path.abspath(buildpath)
        if self.info.__contains__('GCC_PATH'):
            gccpath = self.info['GCC_PATH'].replace('GCC_PATH=', '')
        else:
            gccpath = ''
        if Handler.buildinfo.__contains__('GccPath') and not os.path.isdir(gccpath):
            if os.path.isdir(Handler.buildinfo['GccPath']):
                #if self.info.__contains__('GCC_PATH') and not os.path.isdir(self.info['GCC_PATH']):
                self.info['GCC_PATH'] = 'GCC_PATH=' + Handler.buildinfo['GccPath']
                print("set default gcc path:", self.info['GCC_PATH'])
            else:
                print("can not find gcc path:", Handler.buildinfo['GccPath'])
        if Handler.buildinfo.__contains__('ProjectParser'):
            if Handler.buildinfo['ProjectParser'] == 'GNU MCU Eclipse Project':
                self.info['ProjParser'] = 'eclipseparser'
            else:
                print("do not support:", Handler.buildinfo['ProjectParser'])
                return False
        else:
            print("no project parser!")
            return False
        if Handler.buildinfo.__contains__('BuildRule'):
            if Handler.buildinfo['BuildRule'] == 'only build sub module':
                if Handler.buildinfo.__contains__('SubModulePath'):
                    if os.path.isdir(Handler.buildinfo['SubModulePath']):
                        self.targetlist = os.listdir(Handler.buildinfo['SubModulePath'])
                        self.info['TargetPath'] = os.path.abspath(Handler.buildinfo['SubModulePath'])
                    elif Handler.buildinfo['SubModulePath'].startswith('${ProjDir}'):
                        subpath = os.path.join(self.info['ProjDir'], Handler.buildinfo['SubModulePath'].replace('${ProjDir}/', ''))
                        self.targetlist = os.listdir(subpath)
                        self.info['TargetPath'] = os.path.abspath(subpath)
                    else:
                        print("sub module path error:", Handler.buildinf['SubModulePath'])
                        return False
                    print("ignore sub module list:", Handler.submodulelist)
                else:
                    print("no sub module path! need find it in the project dir...")
            elif Handler.buildinfo['BuildRule'] == 'only build project':
                print("build target:", Handler.buildinfo['ProjName'])
            else:
                ("build rule error!")
                return
        else:
            print("no build rule!")
            return

if __name__ == '__main__':
    print(sys.argv[0])
    default_cfg = sys.argv[0].replace('.py', '.xml')
    CustomBuild = BuildInfo(sys.argv)
    CustomBuild.cfgfile = default_cfg
    CustomBuild.sysargv_parse()
    print(CustomBuild.info)
    CustomBuild.config_parse()
    print(CustomBuild.targetlist)
    print(CustomBuild.info)
