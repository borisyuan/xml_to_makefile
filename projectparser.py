# -*- coding = UTF-8 -*-
#!/usr/bin/python3

import xml.sax

class MakeParaHandler(xml.sax.ContentHandler):
    def __init__(self, paralist):
        self.CurrentData = ""
        self.listOptionValue = ""

    def startElement(self, tag, attributes):
        self.CurrentData = tag
        if tag == "configuration" and attributes.__contains__('name'):
            if attributes['name'] == "Debug" or attributes['name'] == "Release":
                paralist.append(tag)
                paralist.append(attributes['name'])
        if (tag == "toolChain" or tag == "tool") and attributes.__contains__('name'):
            paralist.append(tag)
            paralist.append(attributes['name'])
        if tag == "option":
            if attributes.__contains__('name'):
            #if attributes['name'] == "Include paths (-I)" or attributes == "Defined symbols (-D)":
                paralist.append(attributes['name'])
            if attributes.__contains__('value') and attributes.__contains__('valueType'):
                paralist.append(attributes['valueType'])
                paralist.append(attributes['value'])
        if tag == "listOptionValue" and attributes.__contains__('value'):
            print(attributes['value'])
            paralist.append(attributes['value'])

    def endElement(self, tag):
        self.CurrentData = ""

    def characters(self, content):
        if self.CurrentData == "liastOptionValue":
            self.listOptionValue = content

def listpara(parascript):
    parser = xml.sax.make_parser()
    parser.setFeature(xml.sax.handler.feature_namespaces, 0)
    global paralist
    paralist = []
    Handler = MakeParaHandler(paralist)
    parser.setContentHandler(Handler)
    parser.parse(parascript[0])
    parascript.extend(paralist)


class CfileHandler(xml.sax.ContentHandler):
    def __init__(self, flist):
        self.CurrentData = ""
        self.name = ""
        self.type = ""
        self.locationURI = ""

    def startElement(self, tag, attributes):
        self.CurrentData = tag
        #if tag == "link":
            #print ("link:")
    def endElement(self, tag):
        #if self.CurrentData == "name":
            #print ("name:", self.name)
        #if self.CurrentData == "type":
            #print ("type:", self.type)
        if self.CurrentData == "locationURI":
            #print ("locationURI:", self.locationURI)
            if self.type == "1" :
                flist.append(self.locationURI)
        self.CurrentData = ""
    def characters(self, content):
        if self.CurrentData == "name":
            self.name = content
        if self.CurrentData == "type":
            self.type = content
        if self.CurrentData == "locationURI":
            self.locationURI = content
def listfile(filescript):
    parser = xml.sax.make_parser()
    parser.setFeature(xml.sax.handler.feature_namespaces, 0)
    global flist
    flist = []
    Handler = CfileHandler(flist)
    parser.setContentHandler(Handler)
    parser.parse(filescript[0])
    filescript.extend(flist)

class BuildHandler(xml.sax.ContentHandler):
    def __init__(self, buildlist):
        self.CurrentData = ""
        self.buildSpace = ""
        self.spacePath  = ""
        self.projectComment = ""
        #self.buildTarget = ""

    def startElement(self, tag, attributes):
        self.CurrentData = tag
        if tag == "buildDescription":
            print ("buildDescription:")
    def endElement(self, tag):
        if self.CurrentData == "buildSpace":
            print ("buildSpace:", self.buildSpace)
        if self.CurrentData == "spacePath":
            print ("spacePath:", self.spacePath)
        if self.CurrentData == "projectComment":
            print ("projectComment:", self.projectComment)
            if self.projectComment == "GNU MCU Eclipse Project" :
                buildlist.append(self.spacePath)
                buildlist.append(self.buildSpace)
                buildlist.append(self.projectComment)
            else :
                print("Only support the GNU MCU Eclipse Project!")
                print(self.projectComment, "parser is NOT ready now.")
        self.CurrentData = ""
    def characters(self, content):
        if self.CurrentData == "buildSpace":
            self.buildSpace = content
        if self.CurrentData == "spacePath":
            self.spacePath = content
        if self.CurrentData == "projectComment":
            self.projectComment = content
def listbuild(build):
    parser = xml.sax.make_parser()
    parser.setFeature(xml.sax.handler.feature_namespaces, 0)
    global buildlist
    buildlist = []
    Handler = BuildHandler(buildlist)
    parser.setContentHandler(Handler)
    parser.parse("build.xml")
    build.extend(buildlist)

class TargetHandler(xml.sax.ContentHandler):
    def __init__(self, targetlist):
        self.CurrentData = ""
        self.buildTarget = ""

    def startElement(self, tag, attributes):
        self.CurrentData = tag
        if tag == "projects":
            print ("find projects:")
            print ("BuildInPath:", attributes['BuildInPath'])
            targetlist.append(attributes['BuildInPath'])
    def endElement(self, tag):
        if self.CurrentData == "buildTarget":
            print ("buildTarget:", self.buildTarget)
            targetlist.append(self.buildTarget)
        self.CurrentData = ""
    def characters(self, content):
        if self.CurrentData == "buildTarget":
            self.buildTarget = content
def listproject(projects):
    parser = xml.sax.make_parser()
    parser.setFeature(xml.sax.handler.feature_namespaces, 0)
    global targetlist
    targetlist = []
    Handler = TargetHandler(targetlist)
    parser.setContentHandler(Handler)
    parser.parse("build.xml")
    projects.extend(targetlist)
