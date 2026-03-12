# pyBuild

Is a utility puts the steps to maintain my projects
into one place so it is based on meson/pacman. 
Don't expect this to work right out of the box.
As the integration of scripts like git/pacman into a
Gui is not trivial it might give some insight how it can be done (from my limited perspective).
It tries to offer the following options:

- to run the console version use <pre>./build.py</pre>
- the Gtk/Glib Gui version runs with <pre>python BuildApp.py</pre> allows overriding the project main dir with --dir=PATH 
- in case git is setup with ssh, the environment is prepared to use the AskPass.py as a GUI password helper (also used for sudo on installation with pacman)

On startup the setup options are saved into ~/.config/pyBuild.conf so they can be adjusted
for the next startup.
The default configuration values are build into ProjConfig.py.
Some explanation of the values:

- BuildDir, is the directory which contains subdirectory for each project, and the PKGBUILD templates for each project prefixed with the project name see genericImg for a example 
- Repo, the location of a custom pacman repo directory including the db file ending with .db.tar.gz (only used on linux)
- DefaultTarget is the install prefix for linux it is <pre>/usr</pre> for windows <pre>/ucrt64</pre> 

## Linux

- requires gobject integreation e.g. <pre>pacman -S python-gobject</pre>
- for installation of the packages uses pacman and a local repository (this is much effort see Arch-Linux wiki on creating a custom repository)
- depending on the situation meson install might be an option (with known limitations)
- or the use of the created packages with pacman -U pack_file ...

## Windows

- requires gobject integration use e.g. <pre>pacman -S ${MINGW_PACKAGE_PREFIX}-python-gobject</pre>
- the Gui depends on select.select for file-descriptors so it is not working on Windows
- for installation of the packages meson is used
