import sublime, sublime_plugin

if sublime.version().startswith('3'):
    from .pipe_views import PipeViews, proxy_settings
    from . import settings as settings_bv
else:
    from pipe_views import PipeViews, proxy_settings
    import settings as settings_bv


class PlacementPolicy1(object):
    """
    Use the (group, index) where the build view was last (closed) in;
    if we haven't had a build view yet,
      if the windows has more than one group,
        use the first group that doesn't hold the source view;
        otherwise, place the build view next to the source view (on the right)

    Note: re-placing the build view at last-closed position does not work on
    Sublime Text 3.
    """
    last_placed_group = None

    def choose_group(self, window, view):
        """
        Returns a tuple (group, index), corresponding to
        sublime.View.get_view_index()/set_view_index()
        """

        source_group_index, source_view_index = window.get_view_index(view)

        if self.last_placed_group is not None and self.last_placed_group != (-1, -1):
            group_index, view_index = self.last_placed_group
        else:
            num_groups = window.num_groups()
            if num_groups == 1:
                place_to_side = True
            else:
                group_index = next((i for i in range(num_groups) if i != source_group_index), None)
                if group_index is None:
                    place_to_side = True
                else:
                    active_view = window.active_view_in_group(group_index)
                    _, view_index = window.get_view_index(active_view)
                    view_index += 1
                    place_to_side = False

            if place_to_side:
                group_index = source_group_index
                view_index = source_view_index + 1

        # sublime refuses to place view into group_index if view_index exceeds
        # number of views in that group
        view_index = min(view_index, len(window.views_in_group(group_index)))

        return group_index, view_index


class Pipe(PlacementPolicy1, PipeViews):
    dest_view_name = "Build output"

    def __init__(self, source_view):
        super(Pipe, self).__init__(source_view)

    def on_view_created(self, window, view, pipe):
        group_index, view_index = self.choose_group(window, self.view_launched_build)
        window.set_view_index(view, group_index, view_index)

        source_group_index, _ = window.get_view_index(self.view_launched_build)
        if source_group_index != group_index:
            window.focus_view(self.view_launched_build)


class BuildListener(sublime_plugin.EventListener):
    def __init__(self):
        self.pipes = {}

    def on_modified(self, view):
        pipe = self.pipes.get(view.id(), None)
        if pipe is None or not pipe.enabled_setting.get_value():
            return

        pipe.pipe_text(view)

        # dest_view has not been created; don't continue on to setting scroll
        # position, etc.
        if pipe.prepare_create:
            return

        scroll_pos = pipe.scroll_setting.get_value()
        if scroll_pos == "top" and pipe.first_update:
            pipe.first_update = False
            pipe.dest_view.show(0)
        elif scroll_pos == "bottom" or pipe.last_scroll_region is None:
            pipe.dest_view.show(pipe.dest_view.size())
        elif scroll_pos == "last" and pipe.last_scroll_region is not None:
            def fn():
                pipe.dest_view.set_viewport_position(pipe.last_scroll_region)
                pipe.dest_view.sel().clear()
                for selection in pipe.last_caret_region:
                    pipe.dest_view.sel().add(sublime.Region(selection[0], selection[1]))
            sublime.set_timeout(fn, 500)

    def on_close(self, view):
        for pipe in self.pipes.values():
            if pipe.dest_view and pipe.dest_view.id() == view.id():
                pipe.dest_view = None
                # view.window() does not work; so we use
                # sublime.active_window(). But this again doesn't work on
                # Sublime Text 3; it returns (-1, -1). Assigning is safe
                # because (-1, -1) is treated as a null element.
                pipe.last_placed_group = sublime.active_window().get_view_index(view)

    # https://github.com/kemayo/sublime-text-2-clipboard-history/blob/6b07f38a8ab3d38921bccff68a15658f01c10207/clipboard.py#L75
    def on_window_command(self, window, command_name, args):

        if command_name != 'build':
            return None

        view = window.active_view()
        view_settings = view.settings()

        if not settings_bv.EnabledSetting.kls_get_value(view_settings):
            return None

        if args and 'select' in args and args['select']:
            return None

        print("Here 3")
        source_view = window.get_output_panel("exec")
        pipe = self.pipes.get(source_view.id())
        if not pipe:
            pipe = Pipe(source_view)
            proxy_settings(pipe, view.settings())

            self.pipes[source_view.id()] = pipe

        pipe.first_update = True
        pipe.view_launched_build = view
        pipe.prepare_copy(window)

        # We cannot call the `hide_panel` directly; it has no effect if we do
        # so, last I checked in Sublime 2221 and 3103. Not surprising,
        # considering how most event-loops work. So we employ the (usual) out-
        # of-band trick.
        #
        # It is interesting to note that while `show_panel` accepts the panel
        # argument, `hide_panel` doesn't. See [1]. Though, [2] gives a hint
        # that it might work if the panel is specified via contexts instead of
        # as an argument. But the API (`run_command`) doesn't allow contexts to
        # be specified, only key bindings in a .sublime-keymap. Hmph.
        #
        # [1] https://sublimetext.userecho.com/topics/1930-add-panel-param-to-hide_panel-command/
        # [2] https://forum.sublimetext.com/t/output-panel-hotkey/15628/2
        def show_panel_build_view():
            window.focus_view(pipe.dest_view)

        if view_settings.get('buildview.focus_build', False):
            sublime.set_timeout(show_panel_build_view, 100)


class ToggleScrollBottom(sublime_plugin.TextCommand):
    def run(self, edit):
        settings_bv.ScrollSetting.kls_set_value(self.view.settings(), "bottom")


class ToggleScrollTop(sublime_plugin.TextCommand):
    def run(self, edit):
        settings_bv.ScrollSetting.kls_set_value(self.view.settings(), "top")


class ToggleScrollUnchanged(sublime_plugin.TextCommand):
    def run(self, edit):
        settings_bv.ScrollSetting.kls_set_value(self.view.settings(), "last")


class ToggleEnabled(sublime_plugin.TextCommand):
    def run(self, edit):
        settings_bv.EnabledSetting.kls_set_opposite(self.view.settings())


class ToggleSilenceModifiedWarning(sublime_plugin.TextCommand):
    def run(self, edit):
        settings_bv.SilenceModifiedWarningSetting.kls_set_opposite(self.view.settings())
