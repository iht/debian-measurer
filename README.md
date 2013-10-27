debian-measurer
===============

Grab all Debian packages and measure them.

You need to get the Sources.gz files for the release of Debian you
want to measure. Use this script to grab all the sources for all the releases:

```shell
#!/bin/bash

base_url="ftp://ftp.rediris.es/mirror/debian/"


echo 'stable\ntesting\nsid\nexperimental\nstable-updates\nstable-proposed-updates\ntesting-proposed-updates'| while read d
do

	echo 'main\ncontrib\nnon-free' | while read l
	do	
		echo Grabbing $d/$l...
		wget $base_url/dists/$d/$l/source/Sources.gz
		mv Sources.gz Sources-$d-$l.gz
	done
done```
