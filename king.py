
import sublime
import sublime_plugin
import os
import sys


BASE_DIR = os.path.dirname(__file__)
sys.path.append(BASE_DIR)
sys.path.extend(map(lambda x: os.path.join(BASE_DIR, x), ['core']))

from core import *


class KingNeedHelpCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        path = os.path.join(sublime.packages_path(), 'SublimeNumberKing', 'HELP.md')
        self.view.window().open_file(path)


class KingSwitchNumberTypeCommand(sublime_plugin.TextCommand):
    def run(self, edit, select_type=SELECT_TYPE_AUTO):
        settings.set_select_type(select_type)
        sublime.status_message('Switched to %s Type' % SELECT_TYPES[select_type])






