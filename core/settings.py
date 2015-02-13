
import sublime
import sublime_plugin


class Settings:
    def __init__(self):
        self.__settings = sublime.load_settings('Number King.sublime-settings')

    def load_select_type(self):
        return self.__settings.get('SelectType') or 'float'

    def switch_select_type(self):
        current = self.load_select_type()
        current = 'int' if current == 'float' else 'float'
        self.__settings.set('SelectType', current)
        return current

    def load_last_used_formula(self):
        return self.__settings.get('LastUsedFormula') or 'x'

    def set_last_used_formula(self, formula):
        self.__settings.set('LastUsedFormula', formula)

    def load_last_used_selection_predicate(self):
        return self.__settings.get('LastUsedSelectionPredicate') or 'x > 3'

    def set_last_used_selection_predicate(self, formula):
        self.__settings.set('LastUsedSelectionPredicate', formula)


settings = Settings()

