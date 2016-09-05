
import sublime
import sublime_plugin


SELECT_TYPE_AUTO = 'auto'
SELECT_TYPE_INT = 'integer'
SELECT_TYPE_INT_NEAREST = 'integer_round_nearest'
SELECT_TYPE_FLOAT = 'float'
SELECT_TYPES = {
    SELECT_TYPE_AUTO: 'Auto',
    SELECT_TYPE_INT: 'Integer (Round Down)',
    SELECT_TYPE_INT_NEAREST: 'Integer (Round Nearest)',
    SELECT_TYPE_FLOAT: 'Float',
}


class Settings:
    def __init__(self):
        self.__settings_name = 'SublimeNumberKing.sublime-settings'

    def __load_settings(self):
        self.__settings = sublime.load_settings(self.__settings_name)        

    def __save_settings(self):
        sublime.save_settings(self.__settings_name)

    def load_select_type(self):
        self.__load_settings()
        return self.__settings.get('SelectType') or SELECT_TYPE_AUTO

    def set_select_type(self, select_type):
        self.__load_settings()
        self.__settings.set('SelectType', select_type)
        self.__save_settings()

    def load_last_used_formula(self):
        self.__load_settings()
        return self.__settings.get('LastUsedFormula') or 'x'

    def set_last_used_formula(self, formula):
        self.__load_settings()
        self.__settings.set('LastUsedFormula', formula)
        self.__save_settings()

    def load_last_used_selection_predicate(self):
        self.__load_settings()
        return self.__settings.get('LastUsedSelectionPredicate') or 'x > 3'

    def set_last_used_selection_predicate(self, formula):
        self.__load_settings()
        self.__settings.set('LastUsedSelectionPredicate', formula)
        self.__save_settings()


settings = Settings()

