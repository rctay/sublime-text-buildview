import sublime


class SettingsDeclaration(object):
    """
    SettingsDeclarations are actually like Kmett lenses allowing
    implementations to specify their own respective value validation,
    keys, etc.

    They can get/set on sublime's settings (as static - oops, not Java - class
    methods) or hold distinct values (when instantiated).
    """
    namespace = "buildview"

    def __init__(self):
        self.dirty = False
        self.value = None

    def get_value(self, settings=None):
        if self.dirty:
            return self.value
        return self.kls_get_value(settings)

    def set_value(self, value):
        self.dirty = True
        self.value = value

    @classmethod
    def kls_get_value(kls, settings=None):
        if not settings:
            settings = sublime.active_window().active_view().settings()
        value = settings.get("%s.%s" % (kls.namespace, kls.key), kls.default))
        return value

    @classmethod
    def kls_set_value(kls, settings, value):
        settings.set("%s.%s" % (kls.namespace, kls.key), value)


class EnumSettingsDeclaration(SettingsDeclaration):
    @classmethod
    def kls_get_value(kls, settings=None):
        value = super(EnumSettingsDeclaration, kls).kls_get_value(settings)
        value = value if value in kls.enum else kls.default
        return value

    @classmethod
    def kls_set_value(kls, settings, value):
        value = value if value in kls.enum else kls.default
        super(EnumSettingsDeclaration, kls).kls_set_value(settings, value)

    def get_value(self, settings=None):
        value = super(EnumSettingsDeclaration, self).get_value(settings)
        value = value if value in self.enum else self.default
        return value

    def set_value(self, value):
        value = value if value in self.enum else self.default
        super(EnumSettingsDeclaration, self).set_value(value)


class ScrollSetting(EnumSettingsDeclaration):
    key = "scroll"

    enum = ["bottom", "top", "last"]
    default = "bottom"


class BoolSettingsDeclaration(SettingsDeclaration):
    @classmethod
    def kls_set_opposite(kls, settings):
        value = not kls.kls_get_value(settings)
        kls.kls_set_value(settings, value)
        return value

    def set_opposite(self, settings=None):
        value = not super(BoolSettingsDeclaration, self).get_value(settings)
        super(BoolSettingsDeclaration, self).set_value(value)
        return value


class EnabledSetting(BoolSettingsDeclaration):
    key = "enabled"

    default = True


class SilenceModifiedWarningSetting(BoolSettingsDeclaration):
    """
    This setting determines if a "Save changes?" dialog is to be launched.

    The default is to not show a "Save changes?" dialog.
    """

    key = "silence_modified_warning"

    default = True

