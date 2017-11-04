
import sublime
import sublime_plugin
import os
import sys


from .core import *
from .core.number import *
from .core.selection import *
from .core.settings import settings
from .core.settings import SELECT_TYPES
from .core.settings import SELECT_TYPE_AUTO


class KingNeedHelpCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        path = os.path.join(sublime.packages_path(), 'SublimeNumberKing', 'HELP.md')
        self.view.window().open_file(path)


class KingSwitchNumberTypeCommand(sublime_plugin.TextCommand):
    def run(self, edit, select_type=SELECT_TYPE_AUTO):
        settings.set_select_type(select_type)
        sublime.status_message('Switched to %s Type' % SELECT_TYPES[select_type])






