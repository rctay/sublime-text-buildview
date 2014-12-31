import sublime


class SettingsDeclaration(object):
    settings_file = "Preferences.sublime-settings"

    def __init__(self):
        self.dirty = False
        self.value = None

    def set_value(self, value):
        self.dirty = True
        self.value = value

    def set_opposite(self):
        if self.dirty:
            self.value = not self.value
        else:
            self.value = not self.get_value()
            self.dirty = True

        return self.value

    def get_value(self):
        return self.value if self.dirty \
                else sublime.load_settings(self.settings_file).get(self.settings_key, self.default)


class SilenceModifiedWarningSetting(SettingsDeclaration):
    """
    This setting determines if a "Save changes?" dialog is to be launched.

    The default is to not show a "Save changes?" dialog.
    """

    settings_key = "buildview_silence_modified_warning"

    default = True


# a hack to allow us to set attributes with less keystrokes - via http://stackoverflow.com/a/2283725
class _Struct(object):
    pass


available = _Struct()
available.SilenceModifiedWarning = SilenceModifiedWarningSetting()
