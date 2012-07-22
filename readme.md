# GDB Flee

## A simple web service for helping your data flee File Geodatabaes.

### Example
If you just want to help your data flee, give [this app][app] a try. The app's [about][about] page gives some more details about the how and why of this.

### Deployment
This repo is built to work with [Red Hat Open Shift][openshift]. The libs directory contains pre-built copies of [gdal][gdal], [geos][geos], and [proj][proj]. You will need to download the [File Geodatabase SDK][fgdb] for and copy the .so files into `$HOME/app-root/data/gdb/lib`.

In other environments, as long as python can see the above libraries, it should work.

### Todo

- Better error handling
- API

[openshift]: http://openshift.com
[gdal]: http://www.gdal.org
[geos]: http://trac.osgeo.org/geos/
[proj]: http://trac.osgeo.org/proj/
[fgdb]: http://resources.arcgis.com/content/geodatabases/10.0/file-gdb-download
[app]: http://gdbflee-mweisman.rhcloud.com
[about]: http://gdbflee-mweisman.rhcloud.com/about