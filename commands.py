import sublime, sublime_plugin

from pipe_views import PipeViews


class ViewGroupDecider(object):
    last_placed_group = -1

    def group_other_than(self, window, view):
        groups = window.num_groups()
        group, _ = window.get_view_index(view)
        for i in range(groups):
            if i != group:
                group = i
        index = len(window.views_in_group(group))
        return group, index

    def choose_group(self, view):
        if self.last_placed_group == -1:
            return self.group_other_than(view.window(), view)
        return self.last_placed_group


class BuildListener(sublime_plugin.EventListener,
        ViewGroupDecider,
        PipeViews):
    dest_view_name = "Build output"

    on_modified = PipeViews.pipe_text

    def on_close(self, view):
        if self.dest_view and self.dest_view.id() == view.id():
            self.dest_view = None
            self.last_placed_group = sublime.active_window().get_view_index(view)

    # The technique used below of hooking on to an existing (possibly built-
    # in) command was based on kemayo's excellent work [1]. The comment
    # describing the technique is reproduced here.
    #
    # [1] https://github.com/kemayo/sublime-text-2-clipboard-history/blob/ed5cac2a50189f2399e928b4142b19506af5cc6f#clipboard.py
    #
    # Here we see a cunning plan. We listen for a key, but never say we
    # support it. This lets us respond to ctrl-c and ctrl-x, without having
    # to re-implement the copy and cut commands. (Important, since
    # run_command("copy") doesn't do anything.)
    def on_query_context(self, view, key, *args):
        if key != "build_fake":
            return None

        self.view_launched_build = view

        window = sublime.active_window()
        self.prepare_copy(window.get_output_panel("exec"))

        def hide_panel():
            window.run_command("hide_panel")
        sublime.set_timeout(hide_panel, 500)

        return None

    #
    # Non-sublime events
    #
    def on_view_created(self, view):
        view.window().set_view_index(view, *self.choose_group(view))

        sublime.active_window().focus_view(self.view_launched_build)
