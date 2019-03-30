"""
Source: https://gist.github.com/guyskk/6f3522e3d17135b470bf3d982c80cc01

Add command history and tab completion to python shell.
1. Save this file in ~/.pythonrc.py
2. Add the following line to your ~/.bashrc:
   export PYTHONSTARTUP="$HOME/.pythonrc.py"
"""


def _enable_history_and_completer():
    import atexit
    import os.path

    try:
        import readline
    except ImportError:
        return
    try:
        import rlcompleter
    except ImportError:
        return

    HISTORY_PATH = os.path.expanduser('~/.python_history')

    def _save_history():
        readline.write_history_file(HISTORY_PATH)

    readline.set_completer(rlcompleter.Completer().complete)
    if 'libedit' in readline.__doc__:
        readline.parse_and_bind("bind ^I rl_complete")
    else:
        readline.parse_and_bind("tab: complete")
    if os.path.exists(HISTORY_PATH):
        readline.read_history_file(HISTORY_PATH)
    readline.set_history_length(10000)
    atexit.register(_save_history)


_enable_history_and_completer()
del _enable_history_and_completer
# In addition to os, import some useful things

import re                   ; print "import re";
import pydash as _          ; print "import pydash as _";
from collections import *   ; print "from collections import *";
from itertools import *     ; print "from itertools import *";

