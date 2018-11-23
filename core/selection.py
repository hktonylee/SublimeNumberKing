
import sublime
import sublime_plugin
from . import settings
from . import utils


def get_select_pattern(select_type=None):
    if select_type is None:
        select_type = settings.settings.load_select_type()
    return utils.get_select_regex(select_type)


class KingSelectNumberCommand(sublime_plugin.TextCommand):
    def run(self, edit, select_type=settings.SELECT_TYPE_AUTO):
        pattern = get_select_pattern(select_type)

        current_sel = self.view.sel()
        all_regions = []
        for sel in current_sel:
            region = self.view.find(pattern, sel.begin())
            all_regions.append(region)

        current_sel.clear()
        current_sel.add_all(all_regions)


class KingSelectAllNumbersCommand(sublime_plugin.TextCommand):
    def run(self, edit, select_type=settings.SELECT_TYPE_AUTO):
        pattern = get_select_pattern(select_type)

        current_sel = self.view.sel()
        all_regions = self.view.find_all(pattern)
        if len(current_sel) > 1 or not current_sel[0].empty():
            all_regions = tuple(filter(lambda r: current_sel.contains(r), all_regions))

        if len(all_regions) > 0:
            current_sel.clear()
            current_sel.add_all(all_regions)


class KingSelectCsvFieldCommand(sublime_plugin.TextCommand):
    def on_done(self, text):
        index = {utils.to_non_negative_int(text)}
        current_sel = self.view.sel()
        all_regions = []
        for region in utils.get_current_sel(current_sel, self.view):
            if not region.empty():
                region_line = self.view.line(region)
                for line_region in self.view.split_by_newlines(region_line):
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
        self.view.window().show_input_panel('Select i-th column (start from 0): ', '', self.on_done, None, None)


class KingInterlacedSelectCommand(sublime_plugin.TextCommand):
    def onDone(self, text):
        count = utils.to_positive_int(text)

        current_sel = self.view.sel()
        all_regions = []
        i = 0
        count += 1
        for region in current_sel:
            if i % count == 0:
                all_regions.append(region)
            i += 1

        current_sel.clear()
        current_sel.add_all(all_regions)

    def askInterlacedCount(self):
        self.view.window().show_input_panel('Please the interlaced count', '', self.onDone, None, None)

    def run(self, edit):
        self.askInterlacedCount()

