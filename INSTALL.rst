Installation instructions for pijnu

Dowload
=======

Download the latest 'pijnu' version::

  git clone git@github.com:peter17/pijnu.git

Install
=======
On Unix, you’d run this command from a shell prompt; on Windows, you have to open a command prompt window (“DOS box”) and do it there; on Mac OS X, you open a Terminal window to get a shell prompt. So, open a console box and Move to pijnu's temporary directory, for instance::

  cd /home/me/install/pijnu-version

or::

  cd c:\install\pijnu-version

Then run the command::

  python setup.py install

Note: on some systems, you may need administrator rights to do that. On many Linux boxes, just use "sudo" to be asked for administrator password::

  sudo python setup.py install

This will simply copy pijnu into a place where python will be able to find it for import. You can then delete both the archive and the temp directory if you like.

Note: You can also choose not to install pijnu: if you rename 'pijnu-version' to 'pijnu' and place it in a folder, the Python files in this folder will be able to import the pijnu modules as well.
