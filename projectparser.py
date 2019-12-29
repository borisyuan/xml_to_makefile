# -*- coding = UTF-8 -*-
#!/usr/bin/python3

import xml.sax

ParserStatus = False
ToolchainParse = False
ToolParse = 'NONE'

ParaDict = {}

def toolchainparser(tag, attributes):
    global ParaDict
    if tag == "option" and attributes.__contains__('name') :
        if attributes['name'] == "Optimization Level":
            if attributes['value'].endswith('.optimization.level.none'):
                ParaDict['OPT'] = "OPT = -O0"
            elif attributes['value'].endswith('.optimization.level.normal'):
                ParaDict['OPT'] = "OPT = -O1"
            elif attributes['value'].endswith('.optimization.level.more'):
                ParaDict['OPT'] = "OPT = -O2"
            elif attributes['value'].endswith('.optimization.level.most'):
                ParaDict['OPT'] = "OPT = -O3"
            elif attributes['value'].endswith('.optimization.level.size'):
                ParaDict['OPT'] = "OPT = -Os"
            elif attributes['value'].endswith('.optimization.level.debug'):
                ParaDict['OPT'] = "OPT = -Og"
            print(ParaDict['OPT'])
        if attributes['name'] == "Message length (-fmessage-length=0)":
            ParaDict['TOOL_FLAGS'] = "-fmessage-length=0 "
        if attributes['name'] == "'char' is signed (-fsigned-char)":
            ParaDict['TOOL_FLAGS'] += "-fsigned-char "
        if attributes['name'] == "Function sections (-ffunction-sections)":
            ParaDict['TOOL_FLAGS'] += "-ffunction-sections "
        if attributes['name'] == "Data sections (-fdata-sections)":
            ParaDict['TOOL_FLAGS'] += "-fdata-sections "
            print(ParaDict['TOOL_FLAGS'])
        if attributes['name'] == "Debug level":
            if attributes['value'].endswith('.debugging.level.min'):
                ParaDict['DEBUG_FLAG'] = "CFLAGS += -g1"
            if attributes['value'].endswith('.debugging.level.default'):
                ParaDict['DEBUG_FLAG'] = "CFLAGS += -g"
            if attributes['value'].endswith('.debugging.level.max'):
                ParaDict['DEBUG_FLAG'] = "CFLAGS += -g3"
        #if attributes['name'] == "Debug format":
        if attributes['name'] == "Architecture":
            ParaDict[''] = "MCU = $(CPU) $(THUMB) $(FPU) $(FLOAT-ABI)"
            #if attributes['value'].endswith('.architecture.arm'):
                #ParaDict[''] = ""
        if attributes['name'] == "ARM family":
            if attributes['value'].endswith('.target.mcpu.cortex-m4'):
                ParaDict['CPU'] = "CPU = -mcpu=cortex-m4"
        if attributes['name'] == "Instruction set":
            if attributes['value'].endswith('.thumb'):
                ParaDict['THUMB'] = "THUMB = -mthumb "
                print(ParaDict['THUMB'])
        if attributes['name'] == "Prefix":
            #print("PREFIX =",attributes['value'])
            ParaDict['PREFIX'] = "PREFIX = " + attributes['value']
            print(ParaDict['PREFIX'])
        if attributes['name'] == "C compiler":
            #print("PREFIX =",attributes['value'])
            ParaDict['CC'] = "CC = $(PREFIX)" + attributes['value']
            ParaDict['AS'] = "AS = $(PREFIX)" + attributes['value'] + " -x assembler-with-cpp"
            ParaDict['AS_FLAGS'] = "ASFLAGS = $(MCU) $(AS_DEFS) $(AS_INCLUDES) $(OPT) $(TOOL_FLAGS) "
            print(ParaDict['CC'])
            print(ParaDict['AS'])
        if attributes['name'] == "Hex/Bin converter":
            #print("PREFIX =",attributes['value'])
            ParaDict['CP'] = "CP = $(PREFIX)" + attributes['value']
            print(ParaDict['CP'])
        if attributes['name'] == "Size command":
            #print("PREFIX =",attributes['value'])
            ParaDict['SZ'] = "SZ = $(PREFIX)" + attributes['value']
            print(ParaDict['SZ'])
        #if attributes['name'] == "Build command":
        #if attributes['name'] == "Remove command":
        if attributes['name'] == "Thumb interwork (-mthumb-interwork)":
            ParaDict['THUMB'] += "-mthumb-interwork"
            print(ParaDict['THUMB'])
        if attributes['name'] == "Float ABI":
            if attributes['value'].endswith('.fpu.abi.softfp'):
                ParaDict['FLOAT_ABI'] = "FLOAT_ABI = -mfloat-abi=softfp"
                print(ParaDict['FLOAT_ABI'])
        #if attributes['name'] == "FPU Type":
            if attributes['value'].endswith('.fpu.unit.fpv4spd16'):
                ParaDict['FPU'] = "FPU = -mfpu=fpv4-sp-d16"
                print(ParaDict['FPU'])
        if attributes['name'] == "Warn if floats are compared as equal (-Wfloat-equal)":
            ParaDict['TOOL_FLAGS'] += "-Wfloat-equal "
        if attributes['name'] == "Warn if struct is returned (-Wagreggate-return)":
            ParaDict['TOOL_FLAGS'] += "-Wagreggate-return "

def buidsettinggenerate(tag, attributes):
    global ParaDict
    if ParserStatus == False:
        return
    if ToolParse == "NONE":
        if ToolchainParse == True:
            toolchainparser(tag, attributes)
    #elif ToolParse == "GNU ARM Cross Assembler":
        #toolassemblerparse(tag, attributes)
    #elif ToolParse == "GNU ARM Cross C Compiler":
        #toolcompilerparse(tag, attributes)
    elif ToolParse == "GNU ARM Cross C++ Compiler":
        print("No C++ parse by default!")
        #toolcompilerparse(tag, attributes)
    #elif ToolParse == "GNU ARM Cross C Linker" or ToolParse == "GNU ARM Cross C++ Linker" :
        #toollinkerparse(tag, attributes)
    #else:
        #toolparaparse(tag, attributes)

class MakeParaHandler(xml.sax.ContentHandler):
    def __init__(self, paralist):
        self.CurrentData = ""
        self.listOptionValue = ""

    def startElement(self, tag, attributes):
        global ParserStatus
        global ToolchainParse
        global ToolParse
        self.CurrentData = tag
        buidsettinggenerate(tag, attributes)
        if tag == "configuration" and attributes.__contains__('name'):
            if attributes['name'] == "Debug" :
                ParserStatus = True
                print(ToolParse, ParserStatus)
                paralist.append(tag)
                paralist.append(attributes['name'])
            elif attributes['name'] == "Release":
                ParserStatus = False
        if tag == "toolChain" and attributes.__contains__('name'):
            ToolchainParse = True
            paralist.append(tag)
            paralist.append(attributes['name'])
        if tag == "tool" and attributes.__contains__('name'):
            ToolParse = attributes['name']
            print(ToolParse)
        if tag == "option":
            if attributes.__contains__('name'):
            #if attributes['name'] == "Include paths (-I)" or attributes == "Defined symbols (-D)":
                paralist.append(attributes['name'])
                print(attributes['name'])
            if attributes.__contains__('value') and attributes.__contains__('valueType'):
                paralist.append(attributes['valueType'])
                paralist.append(attributes['value'])
        if tag == "listOptionValue" and attributes.__contains__('value'):
            #print(attributes['value'])
            paralist.append(attributes['value'])

    def endElement(self, tag):
        self.CurrentData = ""

    def characters(self, content):
        if self.CurrentData == "listOptionValue":
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
            print ("BuildGenerate:", attributes['BuildGenerate'])
            targetlist.append(attributes['BuildGenerate'])
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
