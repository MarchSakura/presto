$ PGDISP == "$PERKIN2:[TJP.PGPLOT]PGDISP"
$ SPAWN/NOWAIT/INPUT=NL: PGDISP -line 64
$ DEFINE PGPLOT_DEV "/XDISP"
