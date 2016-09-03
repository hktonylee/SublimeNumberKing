
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
    def mode_select_on_done(self, selected_index):
        type = None
        name = None
        if selected_index == 0:
            type = SELECT_TYPE_AUTO
            name = "Auto"
        elif selected_index == 1:
            type = SELECT_TYPE_INT
            name = "Integer"
        elif selected_index == 2:
            type = SELECT_TYPE_FLOAT
            name = "Float"

        if type:
            settings.set_select_type(type)
            sublime.status_message('Number type is switched to: ' + name)

    def run(self, edit):
        sublime.active_window().show_quick_panel(
            ["Auto (base on first selection)", "Integer", "Float"],
            self.mode_select_on_done
        )





