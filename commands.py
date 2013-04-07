import sublime, sublime_plugin

from pipe_views import PipeViews


class Pipe(PipeViews):
    dest_view_name = "Build output"

    last_placed_group = (0, 0)
    group_to_avoid = None

    def group_other_than(self, window, group):
        groups = window.num_groups()
        group = next(i for i in range(groups) if i != group)
        return group, 0

    def choose_group(self, window, view):
        group = self.last_placed_group
        if self.group_to_avoid == group[0]:
            group = self.group_other_than(window, self.group_to_avoid)
        return group

    def on_view_created(self, window, view, pipe):
        window.set_view_index(view, *self.choose_group(window, view))

        window.focus_view(self.view_launched_build)


class BuildListener(sublime_plugin.EventListener):
    def __init__(self):
        self.pipes = {}

    def on_modified(self, view):
        pipe = self.pipes.get(view.id(), None)
        if pipe is None:
            return
        pipe.pipe_text(view)

    def on_close(self, view):
        for pipe in self.pipes.values():
            if pipe.dest_view and pipe.dest_view.id() == view.id():
                pipe.dest_view = None
                pipe.last_placed_group = sublime.active_window().get_view_index(view)

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

        window = view.window()

        source_view = window.get_output_panel("exec")
        pipe = self.pipes.setdefault(source_view.id(), Pipe())

        pipe.prepare_copy(window)
        pipe.view_launched_build = view
        pipe.group_to_avoid = window.get_view_index(view)[0]

        def hide_panel():
            window.run_command("hide_panel")
        sublime.set_timeout(hide_panel, 500)

        return None
