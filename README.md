# pathfix

Change the #! line (shebang) occurring in Python scripts.  The new interpreter
pathname must be given with a -i option.

Command line arguments are files or directories to be processed.
Directories are searched recursively for files whose name looks
like a python module. Symbolic links are always ignored
(except as explicit directory arguments).

The original file is kept as a back-up (with a "~" attached to its name),
-n flag can be used to disable this.

Sometimes you may find shebangs with flags such as `#! /usr/bin/env python -si`.
Normally, pathfix overwrites the entire line, including the flags.
To change interpreter and keep flags from the original shebang line, use -k.
If you want to keep flags and add to them one single literal flag, use option -a.

Undoubtedly you can do this using find and sed or perl, but this is
a nice example of Python code that recurses down a directory tree
and uses regular expressions.  Also note several subtleties like
preserving the file's mode and avoiding to even write a temp file
when no changes are needed for a file.

# Distribution

In Fedora Linux, this tools is a part of python-rpm-macros RPM package in /usr/lib/rpm directory.

# History

This tool has been in CPython since version [2.0 (August 1994)](https://github.com/python/cpython/commit/9af22a037fc961b51651324bdd17a43567a688fd)
until [October 2022 and version 3.12](https://github.com/python/cpython/commit/e0ae9ddffe0a708d0d3f5b8cc10488d466fc43c4).

Because we (Python maintenance team in Red Hat) use this tool in Fedora Linux to [fix shebangs in RPM packages](https://src.fedoraproject.org/rpms/python-rpm-macros/blob/rawhide/f/macros.python#_21)
we decided to create a new upstream for it and allow other users to use it and contribute to it.

# License

[Python-2.0.1](https://spdx.org/licenses/Python-2.0.1.html)
