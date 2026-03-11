#
# -*- coding: utf-8 -*-
import threading
import selectors
import select
import os
import subprocess
from MsgListener import MsgListenerInterface

# run process asynchronously
#   and allow watching output
class PipeThread:
    msgLsnr: MsgListenerInterface
    proc: subprocess.Popen
    thread: threading.Thread
    @property
    def PROCESS_TIMEOUT(self) -> float: # allow e.g. makepkg -> takes time to compile
        return 5.0 * 60.0     # 5Min as seconds

    def __init__(self
                , cmd: list[str]
                , dir: str
                , env: dict[str,str] = None
                , msgLsnr: MsgListenerInterface = None):
        #print(f'PipeThread __init__ {cmd}')
        self.msgLsnr = msgLsnr
        proc_env = os.environ.copy()
        if not env is None:
            for e in env:
                proc_env[e] = env[e]
        self.proc = subprocess.Popen(cmd
                         , env=proc_env
                         , cwd=dir
                         , text=True
                         , stdout=subprocess.PIPE
                         , stderr=subprocess.PIPE
                         , stdin=subprocess.PIPE)
        self.thread = threading.Thread(target=self.thread_run_function, args=())
        self.thread.start()

    def join(self):
        if not self.thread is None:
            self.thread.join()
    def thread_run_function(self):
        while self.proc.poll() is None:
            # wlist with  self.proc.stdin will always be 'ready'
            #  ssh passphrase is not 'captured' -> use setsid + SSH_ASKPASS
            inputready, outputready, exceptready = select.select([self.proc.stdout, self.proc.stderr], [], [self.proc.stdout], self.PROCESS_TIMEOUT)
            for inrdy in inputready:
                if inrdy == self.proc.stdout:
                    line = self.proc.stdout.readline()      # risky to read line but don't want to garble output
                    line = line.strip(' \t\r\n')            # avoid extra newlines
                    if line != '':
                        self.msgLsnr.out(line)
                elif inrdy == self.proc.stderr:
                    line = self.proc.stderr.readline()
                    line = line.strip(' \t\r\n')
                    if line != '':
                        self.msgLsnr.err(line)
                else:
                    print(f'thread_run_function in {inrdy} other ')
            #for outrdy in outputready:
            #    if outrdy == self.proc.stdin:
                    #print('expecting input ')
                    #self.proc.stdin.writelines(['06486'])
            #    else:
            #        print(f'thread_run_function out {outrdy} other')
            for excrdy in exceptready:
                print(f'thread_run_function exp {excrdy} stdout {self.proc.stdout} other')
        # if we get a result process has ended
        self.msgLsnr.closed(self.proc.poll())