# -*- coding: UTF-8 -*-
#!/usr/bin/python3

import xml.sax
import os

# parse the .project and get target source
def comfirm_source(projdir, source):
    print(source)
    if os.path.isfile(source):
        return source
    if source.startswith('PARENT-'):
        part = source.split('/', 1)
        symble = part[0].split('-', 2)
        if len(symble) < 3:
            print("error prefix:", part[0])
            return ''
        parent = ''
        for i in range(int(symble[1])):
            parent += '../'
        parentdir = os.path.join(projdir, parent)
        retsource = os.path.join(parentdir, part[1])
        if os.path.isfile(retsource):
            print("+src:", retsource)
            return retsource
        else:
            return ''
    elif source.startswith('"${ProjDirPath}'):
        # the source path combine the variable ${ProjDirPath}
        pathtemp = source.replace('"${ProjDirPath}/', '')
        part = pathtemp.replace('"', '')
        retstr= os.path.join(projdir, part)
        print("+ src:", retstr)
        return retstr
    else:
        # the path is in the current project dir
        return ''

class SourceHandler(xml.sax.ContentHandler):
    def __init__(self, projdir):
        self.CurrentData = ""
        self.name = ""
        self.type = ""
        self.locationURI = ""
        self.sourcelist = []
        self.projdir = os.path.abspath(projdir)

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
                sourcefile = comfirm_source(self.projdir, self.locationURI)
                self.sourcelist.append(sourcefile)
        self.CurrentData = ""
    def characters(self, content):
        if self.CurrentData == "name":
            self.name = content
        if self.CurrentData == "type":
            self.type = content
        if self.CurrentData == "locationURI":
            self.locationURI = content

def source_parse(projdir):
    if not os.path.isdir(projdir):
        print("invalid project path:", projdir)
        return ''
    projxml = os.path.join(os.path.abspath(projdir), ".project")
    print("parse source:", projxml)
    parser = xml.sax.make_parser()
    parser.setFeature(xml.sax.handler.feature_namespaces, 0)
    Handler = SourceHandler(projdir)
    parser.setContentHandler(Handler)
    parser.parse(projxml)
    #print(Handler.sourcelist)
    return Handler.sourcelist

# parse the .cproject and get build para
def linker_para_parse(paradict, tag, attributes):
    if tag == "option" and attributes.__contains__('name'):
        if attributes['name'] == "Script files (-T)":
            paradict['LDSCRIPT'] = "LDSCRIPT = "
        elif (attributes['name'].find(' (-') > 0) and attributes.__contains__('value') and attributes['value'] == 'true':
            para = attributes['name'].split('(',1)
            flag = para[1].replace(')', ' ')
            if paradict.__contains__('LDFLAGS'):
                paradict['LDFLAGS'] += flag
            else:
                paradict['LDFLAGS'] = "LDFLAGS = -T$(LDSCRIPT) $(LIBDIR) $(LIBS) -Wl,-Map=$(BUILD_DIR)/$(TARGET).map " + flag
            print(paradict['LDFLAGS'])
    elif tag == "listOptionValue" and attributes.__contains__('value'):
        print(attributes['value'])
        if os.path.isfile(attributes['value']):
            paradict['LDSCRIPT'] += attributes['value']
        else:
            if attributes['value'].startswith('"${ProjDirPath}/'):
                pathtemp = attributes['value'].replace('"${ProjDirPath}/', '')
                ldpath = pathtemp.replace('"', '')
                ldscript = os.path.join(paradict['projdir'], ldpath)
                paradict['LDSCRIPT'] += ldscript
            else:
                ldscript = os.path.join(paradict['projdir'], attributes['value'])
                if os.path.isfile(ldscript):
                    paradict['LDSCRIPT'] += ldscript
                else:
                    print("can not find ldscript file!\n path :", attributes['value'])
        #print(paradict['LDSCRIPT'])

def comfirm_includes(projdir, includes):
    print(includes)
    if os.path.isdir(includes):
        return includes
    else:
        if includes.startswith('"${ProjDirPath}'):
            # the includes path combine the variable ${ProjDirPath}
            pathtemp = includes.replace('"${ProjDirPath}/', '')
            incpath = pathtemp.replace('"', '')
            #print(incpath)
            retstr= os.path.join(projdir, incpath)
            print("+ include dir:", retstr)
            return retstr
        else:
            # the path is in the current project dir
            if includes.startswith('"../'):
                #this means dufault eclipse setting use the subdir Debug or Release
                temppath = includes.replace('"../', '')
                incdir = temppath.replace('"', '')
                incpath = os.path.join(projdir, incdir)
            else:incpath = os.path.join(projdir, includes)
            if os.path.isdir(incpath):
                print("+ ~include dir:", incpath)
                return incpath
            else:
                print("Can not parse this include:", includes, incpath)
                return ''

def compiler_para_parse(status, paradict, tag, attributes):
    if tag == "option" and attributes.__contains__('valueType'):
        if attributes['valueType'] == "definedSymbols" or (attributes.__contains__('name') and attributes['name'] == "Defined symbols (-D)"):
            paradict['C_DEFS'] = "C_DEFS ="
            status['option'] = 'C_DEFS'
        elif attributes['valueType'] == "includePath" or (attributes.__contains__('name') and attributes['name'] == "Include paths (-I)"):
            paradict['C_INCLUDES'] = "C_INCLUDES ="
            status['option'] = 'C_INCLUDES'
    elif tag == "listOptionValue" and attributes.__contains__('value'):
        if status['option'] == 'C_DEFS':
            Defs = " \\\n -D" + attributes['value']
            paradict['C_DEFS'] += Defs
            print("+ define symble:", attributes['value'])
            #print(paradict['C_DEFS'])
        elif status['option'] == 'C_INCLUDES':
            Icludes = " \\\n -I" + comfirm_includes(paradict['projdir'], attributes['value'])
            paradict['C_INCLUDES'] += Icludes
            #print(paradict['C_INCLUDES'])

def assembler_para_parse(paradict, tag, attributes):
    if tag == "option" and attributes.__contains__('name'):
        if (attributes['name'] == "Use preprocessor") and attributes.__contains__('value') and attributes['value'] == 'true':
            paradict['AS_DEFS'] = "AS_DEFS = "
            paradict['AS_INCLUDES'] = "AS_INCLUDES = "

def tool_para_parse(paradict, tag, attributes):
    if tag == "option" and attributes.__contains__('name') :
        if attributes['name'] == "Optimization Level":
            if attributes['value'].endswith('.optimization.level.none'):
                paradict['OPT'] = "OPT = -O0"
            elif attributes['value'].endswith('.optimization.level.normal'):
                paradict['OPT'] = "OPT = -O1"
            elif attributes['value'].endswith('.optimization.level.more'):
                paradict['OPT'] = "OPT = -O2"
            elif attributes['value'].endswith('.optimization.level.most'):
                paradict['OPT'] = "OPT = -O3"
            elif attributes['value'].endswith('.optimization.level.size'):
                paradict['OPT'] = "OPT = -Os"
            elif attributes['value'].endswith('.optimization.level.debug'):
                paradict['OPT'] = "OPT = -Og"
            print(paradict['OPT'])
        elif attributes['name'] == "Debug level":
            if attributes['value'].endswith('.debugging.level.min'):
                paradict['DEBUG_FLAG'] = "CFLAGS += -g1"
            if attributes['value'].endswith('.debugging.level.default'):
                paradict['DEBUG_FLAG'] = "CFLAGS += -g"
            if attributes['value'].endswith('.debugging.level.max'):
                paradict['DEBUG_FLAG'] = "CFLAGS += -g3"
        #if attributes['name'] == "Debug format":
        elif attributes['name'] == "Architecture":
            paradict['MCU'] = "MCU = $(CPU) $(THUMB) $(FPU) $(FLOAT_ABI)"
            #if attributes['value'].endswith('.architecture.arm'):
                #paradict[''] = ""
        elif attributes['name'] == "ARM family":
            #if attributes['value'].endswith('.target.mcpu.cortex-m4'):
            if  attributes.__contains__('value'):
                vstr = attributes['value'].split('.')
                paradict['CPU'] = "CPU = -mcpu=" + vstr[len(vstr) - 1]
                #paradict['CPU'] = "CPU = -mcpu=cortex-m4"
        elif attributes['name'] == "Instruction set":
            if attributes['value'].endswith('.thumb'):
                paradict['THUMB'] = "THUMB = -mthumb "
                print(paradict['THUMB'])
        elif attributes['name'] == "Prefix":
            #print("PREFIX =",attributes['value'])
            paradict['PREFIX'] = "PREFIX = " + attributes['value']
            print(paradict['PREFIX'])
        elif attributes['name'] == "C compiler":
            #print("PREFIX =",attributes['value'])
            paradict['CC'] = "CC = $(PREFIX)" + attributes['value']
            paradict['AS'] = "AS = $(PREFIX)" + attributes['value'] + " -x assembler-with-cpp"
            paradict['ASFLAGS'] = "ASFLAGS = $(MCU) $(OPT) $(TOOL_FLAGS) $(AS_DEFS) $(AS_INCLUDES) "
            paradict['CFLAGS'] = "CFLAGS = $(MCU) $(OPT) $(TOOL_FLAGS) $(C_DEFS) $(C_INCLUDES) "
            print(paradict['CC'])
            print(paradict['AS'])
        elif attributes['name'] == "Hex/Bin converter":
            #print("PREFIX =",attributes['value'])
            paradict['CP'] = "CP = $(PREFIX)" + attributes['value']
            print(paradict['CP'])
        elif attributes['name'] == "Size command":
            #print("PREFIX =",attributes['value'])
            paradict['SZ'] = "SZ = $(PREFIX)" + attributes['value']
            print(paradict['SZ'])
        #if attributes['name'] == "Build command":
        #if attributes['name'] == "Remove command":
        elif attributes['name'] == "Float ABI":
            if attributes['value'].endswith('.fpu.abi.softfp'):
                paradict['FLOAT_ABI'] = "FLOAT_ABI = -mfloat-abi=softfp"
                print(paradict['FLOAT_ABI'])
        elif attributes['name'] == "FPU Type":
            if attributes['value'].endswith('.fpu.unit.fpv4spd16'):
                paradict['FPU'] = "FPU = -mfpu=fpv4-sp-d16"
                print(paradict['FPU'])
        elif (attributes['name'].find(' (-') > 0) and attributes.__contains__('value') and attributes['value'] == 'true':
            para = attributes['name'].split('(',1)
            flag = para[1].replace(')', ' ')
            if flag.find('thumb') > 0:
                if paradict.__contains__('THUMB'): paradict['THUMB'] += flag
                print(paradict['THUMB'])
            else:
                if paradict.__contains__('TOOL_FLAGS'): paradict['TOOL_FLAGS'] += flag
                else: paradict['TOOL_FLAGS'] = "TOOL_FLAGS = " + flag
                print("TOOL_FLAGS +", flag)
            #print(paradict['TOOL_FLAGS'])
        elif attributes['name'].startswith('Other ') and attributes.__contains__('valueType') and attributes['valueType'] == 'string':
            if paradict.__contains__('TOOL_FLAGS'): paradict['TOOL_FLAGS'] += attributes['value'] + ' '
            else: paradict['TOOL_FLAGS'] = "TOOL_FLAGS = " + attributes['value']
            print("TOOL_FLAGS +", attributes['value'])

def build_para(status, paradict, tag, attributes):
    if status['parsestart'] == False:
        return
    if status['toolname'] == "NONE":
        if status['parsetool'] == True:
            tool_para_parse(paradict, tag, attributes)
    elif status['toolname'] == "GNU ARM Cross Assembler":
        assembler_para_parse(paradict, tag, attributes)
    elif status['toolname'] == "GNU ARM Cross C Compiler":
        compiler_para_parse(status, paradict, tag, attributes)
    elif status['toolname'] == "GNU ARM Cross C++ Compiler":
        print("No C++ compiler parser by default!")
        #toolcompilerparser(tag, attributes)
    elif status['toolname'] == "GNU ARM Cross C++ Linker" :
        print("No C++ Linker parser by default!")
    elif status['toolname'] == "GNU ARM Cross C Linker":
        linker_para_parse(paradict, tag, attributes)
    #else:
        #toolparaparse(tag, attributes)

class ParaHandler(xml.sax.ContentHandler):
    def __init__(self):
        self.CurrentData = ""
        self.listOptionValue = ""
        self.paradict = {}
        self.status = {'parsestart':False, 'parsetool':False, 'toolname':"NONE"}

    def startElement(self, tag, attributes):
        self.CurrentData = tag
        build_para(self.status, self.paradict, tag, attributes)
        if tag == "configuration" and attributes.__contains__('name'):
            if attributes['name'] == "Debug" :
                self.status['parsestart'] = True
                #print(status['toolname'], status['parsestart'])
            elif attributes['name'] == "Release":
                self.status['parsestart'] = False
        elif tag == "toolChain" and attributes.__contains__('name'):
            self.status['parsetool'] = True
        elif tag == "tool" and attributes.__contains__('name'):
            self.status['toolname'] = attributes['name']
            #print(status['toolname'])

    def endElement(self, tag):
        self.CurrentData = ""

    def characters(self, content):
        if self.CurrentData == "listOptionValue":
            self.listOptionValue = content

def para_parse(projdir):
    if not os.path.isdir(projdir):
        print("invalid project path:", projdir)
        return ''
    abspath_projdir = os.path.abspath(projdir)
    projxml = os.path.join(abspath_projdir, ".cproject")
    print("parse build para:", projxml)
    parser = xml.sax.make_parser()
    parser.setFeature(xml.sax.handler.feature_namespaces, 0)
    Handler = ParaHandler()
    Handler.paradict['projdir'] = abspath_projdir
    print("Project Dir:", abspath_projdir)
    temp = os.path.split(abspath_projdir)
    Handler.paradict['TARGET'] = "TARGET = " + temp[1]
    Handler.paradict['LDFLAGS'] = "LDFLAGS = -T$(LDSCRIPT) $(LIBDIR) $(LIBS) -Wl,-Map=$(BUILD_DIR)/$(TARGET).map "
    print(Handler.paradict['TARGET'])
    parser.setContentHandler(Handler)
    parser.parse(projxml)
    #print(Handler.paradict)
    return Handler.paradict

if __name__ == '__main__':
    #projdir = '../../../mcu_projects/ide/gnu-mcu-eclipse/stm32f407_test'
    projdir = 'demo_proj/'
    source_parse(projdir)
    #xmlfile = os.path.join(os.path.abspath(projdir), ".cproject")
    para_parse(projdir)
