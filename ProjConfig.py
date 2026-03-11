#
# -*- coding: utf-8 -*-

import pathlib
import os
import sys
import gi
gi.require_version("GLib", "2.0")
from gi.repository import GLib, Gio

class ProjConfig:
    @property    # related: see column indexes glade
    def GROUP_MAIN(self) -> str:
        return 'Main'
    @property
    def BUILD_DIR_KEY(self) -> str:
        return 'BuildDir'
    @property
    def REPO_DIR_KEY(self) -> str:
        return 'RepoDir'
    @property
    def REPO_NAME_KEY(self) -> str:
        return 'RepoName'
    @property
    def DEFAULT_TARGET_KEY(self) -> str:
        return 'DefaultTarget'

    def __init__(self):
        self.confFile = self.getConfigName()
        if pathlib.Path.is_file(self.confFile):
            self.config = GLib.KeyFile.load_from_file(self.confFile)
        else:
            self.config = GLib.KeyFile()
        # fill in missing keys, so they can be changed all at once
        added: bool = False
        if not self.isGroupKey(self.GROUP_MAIN, self.REPO_DIR_KEY):
            self.config.set_string(self.GROUP_MAIN, self.REPO_DIR_KEY, '/var/local/pacman')
            added = True
        if not self.isGroupKey(self.GROUP_MAIN, self.BUILD_DIR_KEY):
            home = pathlib.Path.home()
            buildDir = os.path.join(home, 'csrc.git')
            self.config.set_string(self.GROUP_MAIN, self.BUILD_DIR_KEY, buildDir)
            added = True
        if not self.isGroupKey(self.GROUP_MAIN, self.REPO_NAME_KEY):
            self.config.set_string(self.GROUP_MAIN, self.REPO_NAME_KEY, 'custom.db.tar.gz')
            added = True
        if not self.isGroupKey(self.GROUP_MAIN, self.DEFAULT_TARGET_KEY):
            defaultTarget = "/usr" if ProjConfig.isLinux() else "/ucrt64"
            self.config.set_string(self.GROUP_MAIN, self.DEFAULT_TARGET_KEY, defaultTarget)
            added = True
        if added:
            self.config.save_to_file(self.getConfigName())

    @staticmethod
    def isLinux() -> bool:
        return sys.platform == "linux"
    def getConfigName(self) -> str:
        home = pathlib.Path.home()
        return os.path.join(home , '.config', 'pyBuild.conf')

    def isGroupKey(self,group: str, key: str):
        if self.config.has_group(group):
            try:
                value = self.config.get_value(group, key)
                return True
            except Exception as e:  # see no other option to check key
                pass
        return False

    def getMainBuildDir(self) -> str:
        return self.config.get_string(self.GROUP_MAIN, self.BUILD_DIR_KEY)

    def getPacmanRepo(self) -> str:
        return self.config.get_string(self.GROUP_MAIN, self.REPO_DIR_KEY)

    def getCustomRepoName(self) -> str:
        return self.config.get_string(self.GROUP_MAIN, self.REPO_NAME_KEY)

    def getDefaultTarget(self) -> str:
        return self.config.get_string(self.GROUP_MAIN, self.DEFAULT_TARGET_KEY)