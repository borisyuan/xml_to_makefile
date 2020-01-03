# -*- coding = UTF-8 -*-
#!/usr/bin/python3

import xml.sax
import os

ParserStatus = False
ToolchainParse = False
ToolParse = 'NONE'
ProjDir = ''
ListOption = ''
ParaDict = {}

def toollinkerparser(tag, attributes):
    global ProjDir
    if tag == "option" and attributes.__contains__('name'):
        if attributes['name'] == "Script files (-T)":
            ParaDict['LDSCRIPT'] = "LDSCRIPT = "
        elif (attributes['name'].find(' (-') > 0) and attributes.__contains__('value') and attributes['value'] == 'true':
            para = attributes['name'].split('(',1)
            flag = para[1].replace(')', ' ')
            if ParaDict.__contains__('LDFLAGS'):
                ParaDict['LDFLAGS'] += flag
            else:
                ParaDict['LDFLAGS'] = "LDFLAGS = $(MCU) -T$(LDSCRIPT) $(LIBDIR) $(LIBS) -Wl,-Map=$(BUILD_DIR)/$(TARGET).map,--cref " + flag
        print(ParaDict['LDFLAGS'])
    elif tag == "listOptionValue" and attributes.__contains__('value'):
        if os.path.isfile(attributes['value']):
            ParaDict['LDSCRIPT'] += attributes['value']
        else:
            if attributes['value'].startswith('"${ProjDirPath}/'):
                pathtemp = attributes['value'].replace('"${ProjDirPath}/', '')
                ldpath = pathtemp.replace('"', '')
                ldscript = os.path.join(ProjDir, ldpath)
                ParaDict['LDSCRIPT'] += ldscript
            else:
                ldscript = os.path.join(ProjDir, attributes['value'])
                if os.path.isfile(ldscript):
                    ParaDict['LDSCRIPT'] += ldscript
                else:
                    print("can not find ldscript file!\n path :", attributes['value'])
        print(ParaDict['LDSCRIPT'])
def comfirm_includes(includes):
    global ProjDir
    print(includes)
    if os.path.isdir(includes):
        return includes
    else:
        if includes.startswith('"${ProjDirPath}'):
            # the includes path combine the variable ${ProjDirPath}
            pathtemp = includes.replace('"${ProjDirPath}/', '')
            incpath = pathtemp.replace('"', '')
            #print(incpath)
            retstr= os.path.join(ProjDir, incpath)
            print("+ include dir:", retstr)
            return retstr
        else:
            # the path is in the current project dir
            incpath = os.path.join(ProjDir, includes)
            if os.path.isdir(incpath):
                print("+ ~include dir:", incpath)
                return incpath
            else:
                print("Can not parse this include:", includes)
                return ''
def toolcompilerparser(tag, attributes):
    global ParaDict
    global ListOption
    if tag == "option" and attributes.__contains__('name'):
        if (attributes['name'] == "Defined symbols (-D)"):
            ParaDict['C_DEFS'] = "C_DEFS ="
            ListOption = 'C_DEFS'
        elif (attributes['name'] == "Include paths (-I)"):
            ParaDict['C_INCLUDES'] = "C_INCLUDES ="
            ListOption = 'C_INCLUDES'
    elif tag == "listOptionValue" and attributes.__contains__('value'):
        if ListOption == 'C_DEFS':
            Defs = " \\\n -D" + attributes['value']
            ParaDict['C_DEFS'] += Defs
            print(ParaDict['C_DEFS'])
        elif ListOption == 'C_INCLUDES':
            Icludes = " \\\n -I" + comfirm_includes(attributes['value'])
            ParaDict['C_INCLUDES'] += Icludes
            print(ParaDict['C_INCLUDES'])

def toolassemblerparser(tag, attributes):
    global ParaDict
    if tag == "option" and attributes.__contains__('name'):
        if (attributes['name'] == "Use preprocessor") and attributes.__contains__('value') and attributes['value'] == 'true':
            ParaDict['AS_DEFS'] = "AS_DEFS = "
            ParaDict['AS_INCLUDES'] = "AS_INCLUDES = "

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
        elif attributes['name'] == "Debug level":
            if attributes['value'].endswith('.debugging.level.min'):
                ParaDict['DEBUG_FLAG'] = "CFLAGS += -g1"
            if attributes['value'].endswith('.debugging.level.default'):
                ParaDict['DEBUG_FLAG'] = "CFLAGS += -g"
            if attributes['value'].endswith('.debugging.level.max'):
                ParaDict['DEBUG_FLAG'] = "CFLAGS += -g3"
        #if attributes['name'] == "Debug format":
        elif attributes['name'] == "Architecture":
            ParaDict['MCU'] = "MCU = $(CPU) $(THUMB) $(FPU) $(FLOAT-ABI)"
            #if attributes['value'].endswith('.architecture.arm'):
                #ParaDict[''] = ""
        elif attributes['name'] == "ARM family":
            #if attributes['value'].endswith('.target.mcpu.cortex-m4'):
            if  attributes.__contains__('value'):
                vstr = attributes['value'].split('.')
                ParaDict['CPU'] = "CPU = -mcpu=" + vstr[len(vstr) - 1]
                #ParaDict['CPU'] = "CPU = -mcpu=cortex-m4"
        elif attributes['name'] == "Instruction set":
            if attributes['value'].endswith('.thumb'):
                ParaDict['THUMB'] = "THUMB = -mthumb "
                print(ParaDict['THUMB'])
        elif attributes['name'] == "Prefix":
            #print("PREFIX =",attributes['value'])
            ParaDict['PREFIX'] = "PREFIX = " + attributes['value']
            print(ParaDict['PREFIX'])
        elif attributes['name'] == "C compiler":
            #print("PREFIX =",attributes['value'])
            ParaDict['CC'] = "CC = $(PREFIX)" + attributes['value']
            ParaDict['AS'] = "AS = $(PREFIX)" + attributes['value'] + " -x assembler-with-cpp"
            ParaDict['ASFLAGS'] = "ASFLAGS = $(MCU) $(AS_DEFS) $(AS_INCLUDES) $(OPT) $(TOOL_FLAGS) "
            ParaDict['CFLAGS'] = "CFLAGS = $(MCU) $(C_DEFS) $(C_INCLUDES) $(OPT) $(TOOL_FLAGS) "
            print(ParaDict['CC'])
            print(ParaDict['AS'])
        elif attributes['name'] == "Hex/Bin converter":
            #print("PREFIX =",attributes['value'])
            ParaDict['CP'] = "CP = $(PREFIX)" + attributes['value']
            print(ParaDict['CP'])
        elif attributes['name'] == "Size command":
            #print("PREFIX =",attributes['value'])
            ParaDict['SZ'] = "SZ = $(PREFIX)" + attributes['value']
            print(ParaDict['SZ'])
        #if attributes['name'] == "Build command":
        #if attributes['name'] == "Remove command":
        elif attributes['name'] == "Float ABI":
            if attributes['value'].endswith('.fpu.abi.softfp'):
                ParaDict['FLOAT_ABI'] = "FLOAT_ABI = -mfloat-abi=softfp"
                print(ParaDict['FLOAT_ABI'])
        elif attributes['name'] == "FPU Type":
            if attributes['value'].endswith('.fpu.unit.fpv4spd16'):
                ParaDict['FPU'] = "FPU = -mfpu=fpv4-sp-d16"
                print(ParaDict['FPU'])
        elif (attributes['name'].find(' (-') > 0) and attributes.__contains__('value') and attributes['value'] == 'true':
            para = attributes['name'].split('(',1)
            flag = para[1].replace(')', ' ')
            if flag.find('thumb') > 0:
                if ParaDict.__contains__('THUMB'): ParaDict['THUMB'] += flag
                print(ParaDict['THUMB'])
            else:
                if ParaDict.__contains__('TOOL_FLAGS'): ParaDict['TOOL_FLAGS'] += flag
                else: ParaDict['TOOL_FLAGS'] = "TOOL_FLAGS = " + flag
            print(ParaDict['TOOL_FLAGS'])

def buidsettinggenerate(tag, attributes):
    global ParaDict
    if ParserStatus == False:
        return
    if ToolParse == "NONE":
        if ToolchainParse == True:
            toolchainparser(tag, attributes)
    elif ToolParse == "GNU ARM Cross Assembler":
        toolassemblerparser(tag, attributes)
    elif ToolParse == "GNU ARM Cross C Compiler":
        toolcompilerparser(tag, attributes)
    elif ToolParse == "GNU ARM Cross C++ Compiler":
        print("No C++ compiler parser by default!")
        #toolcompilerparser(tag, attributes)
    elif ToolParse == "GNU ARM Cross C++ Linker" :
        print("No C++ Linker parser by default!")
    elif ToolParse == "GNU ARM Cross C Linker":
        toollinkerparser(tag, attributes)
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
                #paralist.append(tag)
                #paralist.append(attributes['name'])
            elif attributes['name'] == "Release":
                ParserStatus = False
        elif tag == "toolChain" and attributes.__contains__('name'):
            ToolchainParse = True
            #paralist.append(tag)
            #paralist.append(attributes['name'])
        elif tag == "tool" and attributes.__contains__('name'):
            ToolParse = attributes['name']
            print(ToolParse)
        #if tag == "option":
        #    if attributes.__contains__('name'):
        #    #if attributes['name'] == "Include paths (-I)" or attributes == "Defined symbols (-D)":
        #        paralist.append(attributes['name'])
        #        print(attributes['name'])
        #    if attributes.__contains__('value') and attributes.__contains__('valueType'):
        #        paralist.append(attributes['valueType'])
        #        paralist.append(attributes['value'])
        #if tag == "listOptionValue" and attributes.__contains__('value'):
        #    #print(attributes['value'])
        #    paralist.append(attributes['value'])

    def endElement(self, tag):
        self.CurrentData = ""

    def characters(self, content):
        if self.CurrentData == "listOptionValue":
            self.listOptionValue = content

def listpara(parascript):
    global ProjDir
    global ParaDict
    ProjDir = os.path.dirname(parascript[0])
    print("Project Dir:", ProjDir)
    temp = os.path.split(ProjDir)
    ParaDict['TARGET'] = "TARGET = " + temp[1]
    print(ParaDict['TARGET'])
    parser = xml.sax.make_parser()
    parser.setFeature(xml.sax.handler.feature_namespaces, 0)
    global paralist
    paralist = []
    Handler = MakeParaHandler(paralist)
    parser.setContentHandler(Handler)
    parser.parse(parascript[0])
    parascript.extend(paralist)
    print(ParaDict.values())
    return ParaDict


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
