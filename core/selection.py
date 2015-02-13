
import sublime
import sublime_plugin
from settings import *
import utils


class KingSelectNumberCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        select_type = settings.load_select_type()
        pattern = utils.get_select_regex(select_type)

        current_sel = self.view.sel()
        all_regions = []
        for sel in current_sel:
            region = self.view.find(pattern, sel.begin())
            all_regions.append(region)

        current_sel.clear()
        current_sel.add_all(all_regions)


class KingSelectAllNumbersCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        select_type = settings.load_select_type()
        pattern = utils.get_select_regex(select_type)

        current_sel = self.view.sel()
        all_regions = self.view.find_all(pattern)
        if len(current_sel) > 1 or not current_sel[0].empty():
            all_regions = tuple(filter(lambda r: current_sel.contains(r), all_regions))

        if len(all_regions) > 0:
            current_sel.clear()
            current_sel.add_all(all_regions)


class KingSelectCsvFieldCommand(sublime_plugin.TextCommand):
    def onDone(self, text):
        index = {utils.to_non_negative_int(text)}
        current_sel = self.view.sel()
        condition_regions = utils.get_current_sel(current_sel, self.view)
        all_regions = []
        for region in condition_regions:
            region = self.view.line(region)
            for line_region in self.view.split_by_newlines(region):
                line = self.view.substr(line_region)
                parser = utils.parse_csv_line(line)
                try:
                    i = 0
                    for item in parser:
                        if i in index:
                            sel_start, sel_end = item[1], item[2]
                            line_start = line_region.begin()
                            all_regions.append(sublime.Region(line_start + sel_start, line_start + sel_end))
                        i += 1
                except StopIteration:
                    pass    # ignore

        current_sel.clear()
        current_sel.add_all(all_regions)

    def run(self, edit):
        self.view.window().show_input_panel('Select i-th column (start from 0): ', '', self.onDone, None, None)        

        # select_type = settings.load_select_type()
        # pattern = get_select_regex(select_type)

        # current_sel = self.view.sel()
        # all_regions = self.view.find_all(pattern)
        # if len(current_sel) > 1 or not current_sel[0].empty():
        #     all_regions = tuple(filter(lambda r: current_sel.contains(r), all_regions))

        # if len(all_regions) > 0:
        #     current_sel.clear()
        #     for region in all_regions:
        #         current_sel.add(region)


