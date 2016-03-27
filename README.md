# A Sublime Text 2/3 plugin to show build output in a view.

[![Flattr this!](http://api.flattr.com/button/flattr-badge-large.png)](https://flattr.com/submit/auto?user_id=rctay&url=https://github.com/rctay/sublime-text-2-buildview&title=sublime-text-2-buildview&category=software) [![Gittip me!](https://www.gratipay.com/assets/-/logo.png)](https://www.gratipay.com/rctay/)

In Sublime Text, build results are shown in a fixed horizontal panel; you
can't drag it to put it vertically next to your code, like in Eclipse, VS.

With this plugin, like any other view, you can put your build results where
you want:

![buildview vertical](https://github.com/rctay/sublime-text-2-buildview/raw/master/buildview.png)

This is super useful if you are repeatedly running a program on your code/
script and want to have its output handy. (You probably already have a
`.sublime-build` or `build_systems` entry in your `.sublime-project`.)

The core functionality is done in `pipe_views.PipeViews`, an abstraction
allowing Unix-like "pipes" to be created between Views in Sublime.

# Usage

The plugin hooks on to the keyboard shortcuts for launching builds; if you
have different shortcuts for them, change the `.sublime-keymap` files
accordingly. These bindings **must** have the following context:

	"context": [{"key": "build_fake", "operator":"equal", "operand":true}]

## Output scrolling

The plugin can scroll the output to the top, bottom, or the position before
the current build was launched.
This can be specified by triggering the Command Palette in *any* view (view
with build output or with source code) in the window, and selecting one of

    Build output always at top
    Build output always at end
    Build output stays at same position

The default is to scroll to the bottom. You can change this by specifying
`buildview_scroll` in Sublime Text's Settings (ie. user/default
`Preferences.sublime-settings`). It should be one of these strings:

 - `top`
 - `bottom`
 - `last`

For example:

    {
    	...
    	"buildview_scroll": "top",
    	...
    }

## Suppress build results panel

The built-in build results view will display momentarily. To disable this, use the User preference setting:

    {
      ...
      "show_panel_on_build": false`.
      ...
    }

## "Save changes?" warning

Since version 90e2365182e9566b2fa79dd7dc79d6b0d7e433f6 (Package Control: 2014.01.27.15.16.48),
closing the build output view, directly, or indirectly, eg. by exiting
Sublime Text, no longer causes a "Save changes?" warning to be displayed.

If you wish to have the old behaviour (of having a warning displayed), set
`buildview_silence_modified_warning` in your user/default `Preferences.sublime-settings`
to `false` (literal, not a string wrapped in quotes); for example:

    {
    	...
    	"buildview_silence_modified_warning": false,
    	...
    }

## Disabling

The plugin can be disabled on a per-view basis by triggering the Command
Palette in either the view with build output or with source code and selecting

    Disable/Enable buildview for this window

# Known Issues/TODO

 - The built-in build view in Sublime Text 2 shows up momentarily before disappearing: wontfix, see #9
 - pin/unpin location, so that subsequent builds scrolls to the same location
 - build view is "forgotten" after restarting Sublime
 - improve disabling/enabling options (eg whitelists, blacklists)

Pull requests welcome!

# Hacking notes

 - after editing `pipe_views.py`, restart Sublime or re-save `commands.py`
   for the changes to take effect.
 - _who's view is it anyway?_ A variety of names are used for views in the
   source code, according to their different roles:
   - source view: the built-in view that shows up when you click Show Build
     Results
   - destination view: the view that mirrors the build output, the one with the
     title "Build Output"
   - otherwise, a view should generally refer to one holding the source for the
     build

# Donate

If you liked this plugin, you can donate here:
[![Flattr this!](http://api.flattr.com/button/flattr-badge-large.png)](https://flattr.com/submit/auto?user_id=rctay&url=https://github.com/rctay/sublime-text-2-buildview&title=sublime-text-2-buildview&category=software) [![Gittip me!](https://www.gratipay.com/assets/-/logo.png)](https://www.gratipay.com/rctay/)
