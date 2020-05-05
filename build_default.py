# -*- coding = UTF-8 -*-
#!/usr/bin/python3

import os
import sys
from custom_cfg import BuildInfo
from proj_parse import ProjParse
from custom_make import AutoMake

def main(argv):
    Custom = BuildInfo(sys.argv)
    Custom.cfgfile = 'custom_cfg.xml'
    Custom.sysargv_parse()
    if len(Custom.info) < 1:
        return
    Custom.config_parse()
    #print(Custom.info)
    #print(Custom.targetlist)
    if Custom.info.__contains__('BUILD_TARGET') and not Custom.info['BUILD_TARGET'].startswith('all'):
        for target in Custom.targetlist:
            if Custom.info['BUILD_TARGET'].startswith(target):
                Custom.info['TargetDir'] = os.path.join(Custom.info['TargetPath'], target)
                print("parse one target:", target, 'in path ' + Custom.info['TargetPath'])
                parser = ProjParse(Custom.info)
                make = AutoMake(parser)
                make.autogen()
                make.run_make()
    else:
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
