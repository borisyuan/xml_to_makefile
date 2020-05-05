# -*- coding: UTF-8 -*-
#!/usr/bin/python3

import os
import sys
import eclipseparse

class ProjParse(object):
    def __init__(self, info):
        self.info = info
        self.sourcelist = []
        self.paradict = {}

    def target_source(self):
        if not os.path.isdir(self.info['TargetDir']):
            print("Can not find dir:", self.info['TargetDir'])
            return []
        if self.info['ProjParser'] == 'eclipseparser':
            self.sourcelist = eclipseparse.source_parse(self.info['TargetDir'])
        #print(self.sourcelist)
        return self.sourcelist

    def target_para(self):
        if not os.path.isdir(self.info['TargetDir']):
            print("Can not find dir:", self.info['TargetDir'])
            return {}
        if self.info['ProjParser'] == 'eclipseparser':
            self.paradict = eclipseparse.para_parse(self.info['TargetDir'])
        #print(self.paradict)
        return self.paradict

if __name__ == '__main__':
    print("test:", argv[0])
