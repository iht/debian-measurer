debian-measurer
===============


Grab all Debian packages and measure them. You will need a Sources.gz
file with the directory of packages to be measured. See below for a
script to gather that file from a Debian mirror.

After that, install the tool with

```
python setup.py install
```

You will need the /lockfile/ module and the SLOCCount tool.

After that, pass the following command line arguments to
/debian-measurer/:
* Location of the sources file
* Output dir for the results
* Base URL of the Debian mirror from where the packages will be
gathered (from Spain, I recommend ftp://ftp.rediris.es/mirror/debian/)
* Path to SLOCCount if it is not in the default path


## Grab all the Sources.gz for Debian

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
done
```
