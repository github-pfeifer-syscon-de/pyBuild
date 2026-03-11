#
# -*- coding: utf-8 -*-
import os
import subprocess
import datetime
import sys
import pathlib
from  PipeThread import PipeThread
from MsgListener import MsgListenerInterface
from ProjConfig import ProjConfig

class Proj():
    config: ProjConfig = None
    def __init__(self, name, path, ts):
        self.name = name
        self.path = path
        self.timestamp = ts
        self.time = datetime.datetime.fromtimestamp(self.timestamp)
    def __repr__(self):
        return f'{self.name:24} {self.formatedTime()}' #  git : {self.gitInfo()}'

    def formatedTime(self) -> str:
        return self.time.strftime("%Y-%m-%d %H:%M:%S")
    def git(self,param) -> bool:
        cmd=['git']
        cmd += param
        print(f'calling  {cmd} for {self.name} ------------------------------')
        try:
            p = subprocess.run(cmd, cwd=self.path)    # , shell=True
            #     print (f'git {p.returncode}')
            return p.returncode == 0
        except Exception as e:
            print(f'error {e} pull in {self.name}')
        return False
    def meson(self,param):
        cmd=['meson', param]
        print(f'calling {cmd} on {self.name} ------------------------------')
        try:
            p = subprocess.run(cmd, cwd=self.getBuildDir())   # , shell=True
            return p.returncode == 0
        except Exception as e:
            print(f'error {e} meson {cmd} in {self.name}')
        return False

    def getBuildName(self) -> str:
        return 'build'
    def getBuildDir(self) -> str:
        return os.path.join(self.path, self.getBuildName())
    def getProjDir(self) -> str:
        return self.path

    def check(self):
        cmd=['meson', 'setup', self.getBuildName()]
        if os.path.isdir(self.getBuildDir()):
            cmd.append('--reconfigure')
            cmd.append('--wipe')
        else:    # create if not existing
            cmd.append('-Dprefix=' + self.defTarget())
        print(f'Check {self.name}')
        try:
            p = subprocess.run(cmd, cwd=self.path)    # , shell=True
            return p.returncode == 0
        except Exception as e:
            print(f'error {e} meson setup ')
        return False

    def prepareDir(self,msgLsnr: MsgListenerInterface):
        if not os.path.isdir(self.getBuildDir()):
            os.makedirs(self.getBuildDir())
        packs = self.findFile(self.getBuildDir(), self.isPackage)
        msgLsnr.out(f"cleaning {len(packs)} package files for {self.name} ------------------------------")
        for pack in packs:
            pack.unlink()
        # create symbolic link
        source = os.path.join(Proj.getMainBuildDir(), self.name + 'PKGBUILD')
        target = os.path.join(self.getBuildDir(), 'PKGBUILD')
        if not os.path.islink(target):
            os.symlink(source, target)

    def repoAdd(self,msgLsnr: MsgListenerInterface):
        toadd: list[str]=[]
        packs = self.findFile(self.getBuildDir(), self.isPackage)
        msgLsnr.out(f'found {len(packs)} package files for {self.name} ------------------------------')
        for pack in packs:
            pack.move_into(self.getPacmanRepo())
            toadd.append(pack.name)
        msgLsnr.out(f'repo-add files for {self.name} ------------------------------')
        cmd = ['repo-add', self.getPacmanRepoDb()]
        cmd += toadd
        p = subprocess.run(cmd, cwd=self.getPacmanRepo(),capture_output=True,text=True)
        msgLsnr.err(p.stderr)
        msgLsnr.out(p.stdout)
        return p

    def getGitPullCmd(self) -> list[str]:
        return ['git','pull']
    def getPackageInstallCmd(self) -> list[str]:
        return ['sudo', '-u', 'root', '--', 'pacman', '--noconfirm', '-Sy', self.name, self.name+'-debug']

    def packageInstall(self,msgLsnr: MsgListenerInterface):
        p = subprocess.run(self.getPackageInstallCmd()
                         , cwd=self.getBuildDir()
                         , capture_output=True
                         , text=True)
        msgLsnr.err(p.stderr)
        msgLsnr.out(p.stdout)
        return p

    def getMakePkgCmds(self) -> list[str]:
        return ['makepkg', '--syncdeps', '--force']
    def makepkg(self,msgLsnr: MsgListenerInterface) -> int:
        self.prepareDir(msgLsnr)
        msgLsnr.out(f'makepackage package files for {self.name} ------------------------------')
        #pipeThread = PipeThread(cmd, self.getBuildDir(), msgLsnr)
        p = subprocess.run(self.getMakePkgCmds()
                         , cwd=self.getBuildDir()
                         , capture_output=True
                         , text=True)
        msgLsnr.err(p.stderr)
        msgLsnr.out(p.stdout)
        if p.returncode == 0:
            p = self.repoAdd(msgLsnr)
            if p.returncode == 0:
                p = self.packageInstall(msgLsnr)
        return p.returncode

    def build(self,msgLsnr: MsgListenerInterface):
        if not ProjConfig.isLinux():
            r = self.git(['pull'])
            if r :
                r = self.check()
            if r :
                r = self.meson('compile')
            if r :
                r = self.meson('install')
        else:
            r = self.makepkg(msgLsnr)
        return  r
    def captOut(self,cmd) -> str:
        try:
            p = subprocess.run(cmd, cwd=self.name, capture_output=True, text=True)
            return p.stdout.strip() + ' ' + p.stderr.strip()
        except Exception as e:
            return f'Error {e} calling {cmd[0]}'

    def gitInfo(self) -> str:
        gitDir = os.path.join(self.path, '.git')
        if os.path.isdir(gitDir):
            self.captOut(['git','fetch'])
            return self.captOut(['git', 'rev-list', '--left-right', '--count', 'main...origin/main'])
        return 'Not a git dir'
    @staticmethod
    def getConfig():
        if Proj.config is None:
            Proj.config = ProjConfig()
        return Proj.config

    # used as store for PKGBUILD templates
    #   with project name as prefix e.g. fractPKGBUILD
    @staticmethod
    def getMainBuildDir():
        return Proj.getConfig().getMainBuildDir()


    def defTarget(self) -> str:
        return Proj.getConfig().getDefaultTarget()
    # check for path if it is a package file for archlinux/pacman
    def isPackage(self,p) -> bool:
        return p.is_file() and p.name.endswith('.zst')
    # find files in dir matching criteria func, and return as list of pathlib.Path
    def findFile(self,dir,func) -> list[pathlib.Path]:
        list: list[pathlib.Path]=[]
        with os.scandir(dir) as d:
            for e in d:
                if func(e):
                    list.append(pathlib.Path(e.path))
        return list
    # get local pacman repo dir
    def getPacmanRepo(self) -> str:
        return Proj.getConfig().getPacmanRepo()

    def getPacmanRepoDb(self) -> str:
        return os.path.join(self.getPacmanRepo(), Proj.getConfig().getCustomRepoName())