#
# -*- coding: utf-8 -*-
import os
from abc import ABC, abstractmethod
from Proj import Proj
from PipeThread import PipeThread
from MsgListener import MsgListenerInterface

class Job(ABC):
    @abstractmethod
    def do(self):
        """Job do"""
        pass

    @abstractmethod
    def done(self):
        """Job done"""
        pass

    def getAskPass(self):
        cwd = os.getcwd()
        return os.path.join(cwd, 'AskPass.py')

class GitPullJob(Job):
    def __init__(self, proj: Proj, msgListener: MsgListenerInterface):
        self.proj = proj
        self.msgListener = msgListener
        self.pt = None

    def do(self):
        env: dict[str,str] = {'SSH_ASKPASS': self.getAskPass()
                             , 'ASKPASS_HINT': 'ssh'}
        cmd : list[str] = ['setsid']        # to detach from console
        cmd.extend(self.proj.getGitPullCmd())
        self.pt = PipeThread(cmd = cmd
                           , dir = self.proj.getProjDir()
                           , env = env
                           , msgLsnr = self.msgListener)

    def done(self):
        if not self.pt is None:
            self.pt.join()

class PrepareDirJob(Job):
    def __init__(self, proj: Proj, msgListener: MsgListenerInterface):
        self.proj = proj
        self.msgListener = msgListener

    def do(self):
        self.proj.prepareDir(self.msgListener)
        self.msgListener.closed(0)

    def done(self):
        pass

class MakePkgJob(Job):
    def __init__(self, proj: Proj, msgListener: MsgListenerInterface):
        self.proj = proj
        self.msgListener = msgListener
        self.pt = None

    def do(self):
       self.pt = PipeThread(cmd = self.proj.getMakePkgCmds()
                          , dir = self.proj.getBuildDir()
                          , msgLsnr = self.msgListener)

    def done(self):
        if not self.pt is None:
            self.pt.join()

class RepoAddJob(Job):  # done in foreground as this is expected to be quick
    def __init__(self, proj: Proj, msgListener: MsgListenerInterface):
        self.proj = proj
        self.msgListener = msgListener

    def do(self):
        p = self.proj.repoAdd(self.msgListener)
        self.msgListener.closed(p.returncode)

    def done(self):
        pass

class PackageInstallJob(Job):
    def __init__(self, proj: Proj, msgListener: MsgListenerInterface):
        self.proj = proj
        self.msgListener = msgListener
        self.pt = None

    def do(self):
        env: dict[str,str] = {'SUDO_ASKPASS': self.getAskPass()
                             , 'ASKPASS_HINT': 'sudo'}
        cmd : list[str] = ['setsid']    # detach from term
        cmd.extend(self.proj.getPackageInstallCmd())
        self.pt = PipeThread(cmd = cmd
                           , dir = self.proj.getBuildDir()
                           , env = env
                           , msgLsnr = self.msgListener)
        #p = self.proj.packageInstall(self.msgListener)
        #self.msgListener.closed(p.returncode)

    def done(self):
        if not self.pt is None:
            self.pt.join()