#!/bin/python3
# -*- coding: utf-8 -*-
import os
import sys
from typing_extensions import override
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import GLib, Gio, Gtk

# a graphical password helper
#   offers two options to display a hint together with label
#   ASKPASS_HINT as environment option
#   --hint=NNN or -h NNN as parameters
class AskPassApp(Gtk.Application):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            application_id="de.pfeifer_syscon.askPass",
            flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE,
            **kwargs
        )
        self.window = None
        self.password = None
        self.visible = None
        self.hint = os.environ.get('ASKPASS_HINT')  # since parameters are not working use environment (or leave it as None)

        optEntry = GLib.OptionEntry()
        optEntry.arg=GLib.OptionArg.STRING
        optEntry.description="Text added to label as hint what is requested"
        #optEntry.arg_data= 'type' #self.type_callback
        #optEntry.flags=GLib.OptionFlags.OPTIONAL_ARG   # works without, but this may go with arg_data to use a parse function
        optEntry.long_name="hint"
        optEntry.short_name = ord("h")
        self.add_main_option_entries([optEntry])

    @override
    def do_startup(self):
        Gtk.Application.do_startup(self)

    def createWindow(self) -> Gtk.ApplicationWindow:
        window = Gtk.ApplicationWindow(application=self, title="AskPass")
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        window.add(vbox)
        lbl ="Passphrase"
        if not self.hint is None:
            lbl += " " + self.hint
        vbox.pack_start(Gtk.Label(label=lbl), True, True, 0)
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=3)
        vbox.pack_start(hbox, True, True, 0)
        self.password = Gtk.Entry()
        hbox.pack_start(self.password, True, True, 0)
        self.password.connect('activate', self.on_ok)
        self.visible = Gtk.CheckButton.new_with_label('Visible')
        hbox.pack_start(self.visible, True, True, 0)
        self.visible.set_active(False)
        self.visible.connect("toggled", self.on_visible_toggled)
        self.on_visible_toggled(self.visible)   # sync state
        button = Gtk.Button.new_with_label("Ok")
        vbox.pack_start(button, True, True, 0)
        button.connect('clicked', self.on_ok)
        return window

    @override
    def do_activate(self):
        # We only allow a single window and raise any existing ones
        if not self.window:
            # Windows are associated with the application
            # when the last one is closed the application shuts down
            self.window = self.createWindow()
            #builder = Gtk.Builder()
            #builder.add_from_file("BuildWin.ui")
            #self.window = builder.get_object("buildWin")
            #builder.connect_signals(self.window)
            self.window.show_all()
        self.window.present()

    @override
    def do_command_line(self, command_line) -> int:
        options = command_line.get_options_dict()
        # convert GVariantDict -> GVariant -> dict
        options = options.end().unpack()
        if "hint" in options:
            self.hint = options["hint"]
        self.activate()
        return 0

    def on_visible_toggled(self, checkbutton):
        self.password.set_visibility(self.visible.get_active())

    def on_ok(self,button):
        print(self.password.get_text())
        self.quit()

    def on_quit(self, action, param):
        self.quit()

if __name__ == "__main__":
    app = AskPassApp()
    app.run(sys.argv)