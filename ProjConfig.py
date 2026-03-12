#
# -*- coding: utf-8 -*-

import pathlib
import os
import sys
import gi
gi.require_version("GLib", "2.0")
from gi.repository import GLib, Gio

class ConfKey:
    sect: ConfSection
    key: str
    type: type
    def __init__(self, sect: ConfSection, key: str, defaultValue: any):
        self.sect = sect
        self.key = key
        self.type = type(defaultValue)
        self.sect.checkDefaultValue(key, defaultValue)
    @property
    def value(self) -> any:
        return self.sect.getValue(self.key,self.type)
    @value.setter
    def value(self,value: any):
        if not type(value) is type:
            raise ValueError(f'value setting changing type {type} now given {type(value)}')
        self.sect.setValue(self.key, value)

class ConfSection:
    sectionName: str
    projConfig: ProjConfig
    def __init__(self, sectionName: str, projConfig: ProjConfig):
        self.sectionName = sectionName
        self.projConfig = projConfig
    def checkDefaultValue(self, key: str, value: any):
        if not self.projConfig.isGroupKey(self.sectionName, key):
            self.projConfig.setDefaultValue(self.sectionName, key, value)
    def getValue(self, key: str, type: type):
        return self.projConfig.getValue(self.sectionName, key, type)
    def setValue(self, key: str, value: any):
        return self.projConfig.setValue(self.sectionName, key, value)

class MainSection(ConfSection):
    buildDir: ConfKey
    repoDir: ConfKey
    repoName: ConfKey
    def __init__(self, projConfig: ProjConfig):
        super().__init__('Main', projConfig)
        home = pathlib.Path.home()
        buildDirDefValue = os.path.join(home, 'csrc.git')
        self.buildDir = ConfKey(self,'BuildDir', buildDirDefValue)
        self.repo = ConfKey(self,'Repo', '/var/local/pacman/custom.db.tar.gz')
        defaultTarget = "/usr" if ProjConfig.isLinux() else "/ucrt64"
        self.defaultTarget = ConfKey(self,'DefaultTarget', defaultTarget)
    @property
    def BuildDir(self) -> ConfKey:
        return self.buildDir
    @property
    def Repo(self) -> ConfKey:
        return self.repo
    @property
    def DefaultTarget(self) -> ConfKey:
        return self.defaultTarget
class ProjConfig:


    def __init__(self):
        confFile = self.getConfigName()
        self.config = GLib.KeyFile()
        if pathlib.Path.is_file(confFile):
            GLib.KeyFile.load_from_file(self.config,confFile,GLib.KeyFileFlags.KEEP_COMMENTS)
        # the initalisation fills in missing keys, so they can be seen
        self.added: bool = False
        self.mainSection = MainSection(self)
        if self.added:
            self.config.save_to_file(self.getConfigName())

    @staticmethod
    def isLinux() -> bool:
        return sys.platform == "linux"
    def getConfigName(self) -> str:
        home = pathlib.Path.home()
        return os.path.join(home , '.config', 'pyBuild.conf')
    @property
    def Main(self) -> MainSection:
        return self.mainSection
    def isGroupKey(self,group: str, key: str):
        if self.config.has_group(group):
            try:
                value = self.config.get_value(group, key)
                return True
            except Exception as e:  # see no other option to check key
                pass
        return False
    def setDefaultValue(self, sectionName: str, key: str, value:any):
        self.added = True
        self.setValue(sectionName, key, value)

    def setValue(self, sectionName: str, key: str, value:any):
        if type(value) is int:
            self.config.set_integer(sectionName, key, int(value))
        if type(value) is str:
            self.config.set_string(sectionName, key, str(value))
        print(f'Setting value for sect {sectionName} key {key} type {type(value)} is not supported!')
    def getValue(self, sectionName: str, key: str, type: type):
        if type is int:
            return self.config.get_integer(sectionName, key)
        if type is str:
            return self.config.get_string(sectionName, str(key))
        print(f'Getting value for sect {sectionName} key {key} type {type} is not supported!')
        return None
