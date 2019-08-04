import sublime, sublime_plugin

if sublime.version().startswith('3'):
    from . import settings as settings_bv
else:
    import settings as settings_bv

def set_settings_listener(instance, settings):
    def callback(*args):
        val = instance.kls_get_value(settings)
        # print('set_settings_listener, namespace: %-15s key: %-15s value: %-10s' % (instance.namespace, instance.key, val))
        instance.set_value(val)
    settings.add_on_change(instance.namespace, callback)

def proxy_settings(pipe, settings):
    settings.clear_on_change(settings_bv.SettingsDeclaration.namespace)

    set_settings_listener(pipe.scroll_setting, settings)
    set_settings_listener(pipe.enabled_setting, settings)

def copy_view_settings(source_view, destine_view):
    source_settings = source_view.settings()
    destine_settings = destine_view.settings()

    # print('BuildView setting syntax', source_syntax)
    source_syntax = source_settings.get('syntax')
    if source_syntax: destine_view.set_syntax_file(source_syntax)

    settings_names = [
        'result_full_regex',
        'result_real_dir',
        'result_replaceby',

        'result_file_regex',
        'result_line_regex',
        'result_base_dir',
    ]

    for setting_name in settings_names:
        setting_value = source_settings.get(setting_name, None)
        if setting_value is not None: destine_settings.set(setting_name, setting_value)


class PipeViews(object):
    dest_view_name = "Dest"

    def __init__(self, source_view):
        self.source_last_pos = 0
        self.is_running = False
        self.prepare_create = False
        self.buffer = ''
        self.last_scroll_region = None

        self.enabled_setting = settings_bv.EnabledSetting()
        self.scroll_setting = settings_bv.ScrollSetting()

        self.dest_view = None
        self.source_view = source_view

    def close_old_build_view(self):
        views = self.window.views()

        # Do not search for it when there are too much views because this would probably hand Sublime Text
        if len(views) > 50:
            return

        for view in self.window.views():
            view_name = view.name()
            # print('view_name: `%s`, dest_view_name: `%s`', (view_name, self.dest_view_name))

            if view.is_scratch() and view_name == self.dest_view_name:
                self.window.focus_view(view)
                self.save_view_positions(view)
                self.window.run_command("close_file")

    def create_destination(self):
        dest_view = self.window.new_file()
        dest_view.is_build_view_enabled = self.enabled_setting.get_value()

        self.dest_view = dest_view
        self.close_old_build_view()
        copy_view_settings(self.source_view, dest_view)

        dest_view.set_name(self.dest_view_name)
        dest_view.set_scratch(settings_bv.SilenceModifiedWarningSetting.kls_get_value(dest_view.settings()))

        proxy_settings(self, dest_view.settings())
        self.on_view_created(self.window, dest_view, self)

        return dest_view

    def save_view_positions(self, dest_view):
        self.last_scroll_region = dest_view.viewport_position()
        self.last_caret_region = [(selection.begin(), selection.end()) for selection in dest_view.sel()]

    def prepare_copy(self, window):
        """
        'Lock' the source view, and clear the destination view, if it exists.
        """
        self.window = window
        self.source_last_pos = 0

        dest_view = self.dest_view
        # print('dest_view', dest_view)

        if dest_view is not None:
            copy_view_settings(self.source_view, dest_view)

            self.save_view_positions(dest_view)
            dest_view.run_command('content_clear')
        else:
            self.buffer = ''
            self.prepare_create = True

            # Creating the dest view breaks modify listening; do it outside of
            # the current call stack
            def fn():
                dest_view = self.create_destination()
                dest_view.run_command('content_prepend', {'text': self.buffer})
                self.prepare_create = False

            sublime.set_timeout(fn, 100)

    def pipe_text(self, view):
        """
        Incrementally update the destination view.
        """
        if self.is_running:
            return

        self.is_running = True
        try:
            prev_source_last_pos = self.source_last_pos

            dest_view = self.dest_view
            # We're paranoid. Check dest view availability on every run, not just
            # on first run, in case the user closed it.
            if dest_view is None:
                if self.prepare_create:
                    new_source_last_pos = view.size()
                    region = sublime.Region(prev_source_last_pos, new_source_last_pos)
                    self.buffer += view.substr(region)

                    self.source_last_pos = new_source_last_pos
                    return

                dest_view = self.create_destination()

                # Copy text before readhead
                dest_view.run_command('content_prepend', {'text': view.substr(sublime.Region(0, prev_source_last_pos))})

            new_source_last_pos = view.size()
            region = sublime.Region(prev_source_last_pos, new_source_last_pos)
            dest_view.run_command('content_replace', {'start': prev_source_last_pos, 'end': new_source_last_pos, 'text': view.substr(region)})

            self.source_last_pos = new_source_last_pos
        finally:
            self.is_running = False

    def on_view_created(self, window, view, pipe):
        "Hook called when the destination view is created."


class ContentClear(sublime_plugin.TextCommand):
    def run(self, edit):
        region = sublime.Region(0, self.view.size())
        self.view.erase(edit, region)


class ContentReplace(sublime_plugin.TextCommand):
    def run(self, edit, start, end, text):
        # On Sublime Text 2 32-bit (on 64-bit??),
        # - run_command() converts start/end to floats; and
        # - sublime.Region() does not accept floats
        # Together these causes Region() to fail; hence the cast.
        #
        # int() instead of long() since Python 3 does not have the latter
        start = int(start); end = int(end)
        region = sublime.Region(start, end)
        self.view.replace(edit, region, text)


class ContentPrepend(sublime_plugin.TextCommand):
    def run(self, edit, text):
        self.view.insert(edit, 0, text)
