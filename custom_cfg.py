# -*- coding: UTF-8 -*-
#!/usr/bin/python3

import xml.sax
import sys
import os

class CustomCfgHandler(xml.sax.ContentHandler):
    def __init__(self):
        self.CurrentData = ""

    def startElement(self, tag, attributes):
        self.CurrentData = tag
        if tag == "projects":
            print ("Start to search projects:")
            #print ("BuildGenerate:", attributes['BuildGenerate'])
            #targetlist.append(attributes['BuildGenerate'])
            #targetlist.append(tag)
    def endElement(self, tag):
        if self.CurrentData == "TargetName":
            print ("TargetName:", self.buildTarget)
            targetlist.append(self.buildTarget)
        self.CurrentData = ""
    def characters(self, content):
        if self.CurrentData == "TargetName":
            self.buildTarget = content

class BuildInfo(object):
    def __init__(self, cfg_file):
        self.cfgfile = cfg_file
        self.targetlist = []
        self.infodict = {}

    def config_parse(self):
        if not os.path.isfile(self.cfgfile):
            print("Can not find custom config file:",self.cfgfile)
            return

if __name__ == '__main__':
    print(sys.argv[0])
    cfg = sys.argv[0].replace('.py', '.xml')
    CustomBuild = BuildInfo(cfg)
    CustomBuild.config_parse()
