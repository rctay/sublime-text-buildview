import sublime, sublime_plugin

from pipe_views import PipeViews

class BuildListener(sublime_plugin.EventListener, PipeViews):
    dest_view_name = "Build output"

    on_modified = PipeViews.pipe_text

    def on_close(self, view):
        if self.dest_view and self.dest_view.id() == view.id():
            self.dest_view = None

    # source: https://github.com/kemayo/sublime-text-2-clipboard-history/blob/ed5cac2a50189f2399e928b4142b19506af5cc6f#clipboard.py
    #
    # Here we see a cunning plan. We listen for a key, but never say we
    # support it. This lets us respond to ctrl-c and ctrl-x, without having
    # to re-implement the copy and cut commands. (Important, since
    # run_command("copy") doesn't do anything.)
    def on_query_context(self, view, key, *args):
        if key != "build_fake":
            return None

        window = sublime.active_window()
        self.prepare_copy(window.get_output_panel("exec"))

        def hide_panel():
            window.run_command("hide_panel")
        sublime.set_timeout(hide_panel, 500)

        return None

