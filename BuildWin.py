import html
import sys

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import GLib, Gio, Gtk
import os
from Proj import Proj
from Job import Job, MakePkgJob, PrepareDirJob, RepoAddJob, PackageInstallJob, GitPullJob
from Runner import Runner
from MsgListener import MsgListenerInterface

@Gtk.Template(filename="BuildWin.ui")
class BuildWin(Gtk.ApplicationWindow):
    __gtype_name__ = "buildWin"

    # python's way for constants property without setter ...
    @property    # related: see column indexes glade
    def COLUMN_INDEX_NAME(self) -> int:
        return 0
    @property
    def COLUMN_INDEX_TIME(self) -> int:
        return 1
    @property
    def COLUMN_INDEX_PROJ (self) -> int:
        return 2

    table = Gtk.Template.Child()
    text = Gtk.Template.Child()
    build = Gtk.Template.Child()

    def __init__(self, *args, **kwargs):
       super().__init__(*args, **kwargs)
       self.runner = None
       model = self.list()
       sorted_model = Gtk.TreeModelSort(model=model)
       sorted_model.set_sort_column_id(self.COLUMN_INDEX_TIME, Gtk.SortType.ASCENDING)   # s used iso date to be sortable as text
       self.table.set_model(sorted_model)
       renderName = Gtk.CellRendererText()
       columnName = Gtk.TreeViewColumn("Name", renderName, text=self.COLUMN_INDEX_NAME)
       columnName.set_sort_column_id(self.COLUMN_INDEX_NAME)
       self.table.append_column(columnName)
       renderTime = Gtk.CellRendererText()
       columnTime = Gtk.TreeViewColumn("Time", renderTime, text=self.COLUMN_INDEX_TIME)
       columnTime.set_sort_column_id(self.COLUMN_INDEX_TIME)
       #columnTime .set_cell_data_func(renderTime, color_by_length)
       self.table.append_column(columnTime)
       self.build.connect("clicked",self.on_build)
       buf = self.text.get_buffer()
       self.warn_tag = buf.create_tag('warnTag', foreground='orange')
       self.good_tag = buf.create_tag('goodTag', foreground='green')
       self.fail_tag = buf.create_tag('failTag', background='red')

    #def color_by_length(self,column, cellrenderer, model, iter, user_data):
    #    text = model[iter][0]
    #    if len(text) < 10:
    #        cellrenderer.set_property('foreground', 'green')
    #    elif len(text) < 20:
    #        cellrenderer.set_property('foreground', 'blue')
    #    else:
    #        cellrenderer.set_property('foreground', 'red')

    def list(self):
        # sort will be handled with table
        #lstProj: list[Proj]=[]
        store = Gtk.ListStore(str, str, object)
        with os.scandir(Proj.getMainBuildDir()) as d:
            for e in d:
                if e.is_dir() and not e.name.startswith('.'):
                    ctime = os.path.getctime(e)
                    f = Proj(e.name, e.path, ctime)
                    #lstProj.append(f)
                    store.append([f.name, f.formatedTime(), f])
        # this is a sort with python approach, alternative sorted model above
        #lstProj = sorted(lstProj, key=lambda file: file.timestamp)
        #for e in lstProj:
        #    store.append([e.name, e.formatedTime(), e])
        return store

    # this summarizes the steps need to
    #   build a project
    #   this creates the build directory if it is missing
    #   see the PKGBUILD templates for additional project options
    def doBuild(self, proj: Proj):
        jobs: list[Job] = []
        jobs.append(GitPullJob(proj, self))
        jobs.append(PrepareDirJob(proj, self))
        jobs.append(MakePkgJob(proj, self))
        jobs.append(RepoAddJob(proj, self))
        jobs.append(PackageInstallJob(proj, self))
        self.runner = Runner(jobs)
        self.runner.next()

    def on_build(self, widget):
        model, treeiter = self.table.get_selection().get_selected()
        if treeiter is not None:
            proj = model.get_value(treeiter, self.COLUMN_INDEX_PROJ)
            self.doBuild(proj)
        else:
            dialog = Gtk.MessageDialog(
                transient_for=self,
                flags=0,
                message_type=Gtk.MessageType.WARNING,
                buttons=Gtk.ButtonsType.CANCEL,
                text="No selection",
            )
            dialog.run()

    def onDestroy(self, *args):
        self.hide()

    def out(self,msg : str) -> None:
        GLib.idle_add(self.mainOut,msg)   # forward to main-thread

    def err(self,msg: str) -> None:
        GLib.idle_add(self.mainErr,msg)   # forward to main-thread

    def closed(self,status):
        GLib.idle_add(self.mainClosed,status)   # forward to main-thread

    def mainOut(self,msg: str):
        self.appendMsg(msg)

    def mainErr(self,msg: str):
        self.appendMsg(msg, self.warn_tag)

    def appendMsg(self,msg: str, tag=None):
        buf = self.text.get_buffer()
        if  tag is None :
            buf.insert(buf.get_end_iter(), msg + '\n')
        else:
            buf.insert_with_tags(buf.get_end_iter(), msg + '\n', tag)
        self.text.scroll_to_iter(buf.get_end_iter(),0.0,False,1.0,0.0)

    def mainClosed(self,status):
        self.appendMsg(f'Finished {status}', self.good_tag if status == 0 else self.fail_tag )
        self.runner.done()
        if status == 0:
            self.runner.next()
