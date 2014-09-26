import sublime, sublime_plugin


class PipeViews(object):
    dest_view_name = "Dest"

    def __setattr__(self, name, value):
        if name is "enabled_setting":
            value = value is None or value
        elif name is "scroll_setting":
            value = value if value in set(["bottom", "top", "last"]) else "bottom"

        object.__setattr__(self, name, value)

    def __init__(self):
        self.source_last_pos = 0
        self.is_running = False
        self.prepare_create = False
        self.buffer = ''
        self.last_scroll_region = None

        # just use None, our internal cleanup ensures sane values anyway
        self.enabled_setting = None
        self.scroll_setting = None

        self.dest_view = None

    def create_destination(self):
        dest_view = self.window.new_file()

        settings = sublime.load_settings("Preferences.sublime-settings")
        key = settings.get("buildview_scroll", None)
        self.scroll_setting = key

        dest_view.set_name(self.dest_view_name)

        self.dest_view = dest_view

        self.on_view_created(self.window, dest_view, self)

        dest_view.set_scratch(True)

        return dest_view

    def prepare_copy(self, window):
        """
        'Lock' the source view, and clear the destination view, if it exists.
        """
        self.window = window
        self.source_last_pos = 0

        dest_view = self.dest_view
        if dest_view is not None:
            self.last_scroll_region = dest_view.viewport_position()

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
