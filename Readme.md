# pyBuild

Is a utility puts the steps to maintain my projects
into on place so it is based on meson/pacman. 
Don't expect this to work right out of the box.
As the integration of scripts like git/pacman into a
Gui is not trivial it might give some insight how it can be done (from my limited perspective).
It tries to offer the following options:

- control processes with os.subprocess
- to run the console version use <pre>./build.py</pre>
- the Gtk/Glib Gui version runs with <pre>python BuildApp.py</pre> allows overriding the project main dir with --dir=PATH
- requires gobject intergration use for windows e.g. pacman -S ${MINGW_PACKAGE_PREFIX}-python-gobject

So there is no nice configuration, 
the configuration values are build into Proj.py see:

- getMainBuildDir,  is the directory which contains subdirectory for each project, and the PKGBUILD templates for each project prefixed with the project name see genericImg for a example 
- isLinux, switches between two build types: for linux use pacman and a local repository, otherwise install with meson
- getPacmanRepo, the location of a custom pacman repo
- getPacmanRepoDb, the repository db file
- defTarget is the install prefix for linux it is <pre>/usr</pre> for windows <pre>/ucrt64</pre> 
- in case git is setup with ssh, the environment is prepared to use the AskPass.py as a GUI password helper (also used for sudo on installation)  