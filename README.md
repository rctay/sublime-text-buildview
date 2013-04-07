# A Sublime Text 2 plugin to show build output in a view.

In Sublime Text 2, build results are shown in a fixed horizontal panel; you
can't drag it to put it vertically next to your code, like in Eclipse, VS.

With this plugin, like any other view, you can put your build results where
you want:

![buildview vertical](https://github.com/rctay/sublime-text-2-buildview/raw/master/buildview.png)

The core functionality is done in `pipe_views.PipeViews`, an abstraction
allowing Unix-like "pipes" to be created between Views in Sublime.

# Usage

The plugin hooks on to the keyboard shortcuts for launching builds; if you
have different shortcuts for them, change the `.sublime-keymap` files
accordingly, as well as adding the context key with value

	"context": [{"key": "build_fake", "operator":"equal", "operand":true}]


# Issues/TODO

 - build view does not gain focus if it is in the same tab group as the view
   that launched the build
 - pin/unpin location, so that subsequent builds scrolls to the same location
 - build view is "forgotten" after restarting Sublime

Pull requests welcome!

# Hacking notes

 - after editing `pipe_views.py`, restart Sublime or re-save `commands.py` 
   for the changes to take effect.
