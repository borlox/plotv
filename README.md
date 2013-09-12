The plotv module/command for saving multiple versions of ROOT plots.


Module
======
Use the `plot_version` class from this module to save versioned plots.

```
from plotv import plot_version
pv = plot_version()
```

to use the default file name or use

```pv = plot_version("filename.root")```

to specify a file name.

Then you create your ROOT plots and save them using

```
pv.save(canvas)
pv.save(canv2, "NewName")
```

You should add an comment using

```pv.comment("Fixed plot style issues")```

If your version is special, you can tag it with a message

```pv.tag("This seems to be good!")```

At the end, close the root file using

```
pv.close()
```

Tool
====
You can use plotv as a tool to list plots in a versioned file and to get plots
of a specific version.

Use

```$ plotv.py --help```

to display the help message.
