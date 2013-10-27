#!/usr/bin/env python

# Copyright (C) 2012 Israel Herraiz Tabernero

# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# Authors : Israel Herraiz <israel.herraiz@upm.es>


"""
Main Sources parser

@author:       Israel Herraiz
@organization: Universidad Politecnica de Madrid
@copyright:    Universidad Politecnica de Madrid
@license:      
@contact:      israel.herraiz@upm.es
"""

import gzip
import os
#import urllib
#import urlparse
import ftplib
import hashlib
import tarfile
import shutil
import tempfile
from lockfile import FileLock, AlreadyLocked, LockFailed

class SourcesFile:

    def __init__ (self, sourcesFilePath = ''):

        self._sourcesFilePath = sourcesFilePath
        self._contents = []
        self.pkgs = []

    def parseAll(self):
        self._readFile()
        self._parseFile()

    def _readFile(self):

        f = gzip.open(self._sourcesFilePath,'r')
        self._contents = f.readlines()
        f.close()
    
    def _parseFile(self):

        currentPkg = None
        hasValue = True

        print 'Parsing sources file %s' % self._sourcesFilePath
        
        for l in self._contents:
            if l.strip():
                if ':' in l:
                    try:
                        field, value = l.strip().split(': ')
                        hasValue = True
                    except ValueError:
                        field = l.strip().rstrip(':')
                        hasValue = False

                   
                        
                    if field.lower() == 'package':
                        if currentPkg:
                            self.pkgs.append(currentPkg)
                        currentPkg = Package()
                        print '*** Parsing package %s' % value

                        currentPkg[field] = value

                    elif field.lower() == 'build-depends' or field.lower() == 'binary' or field.lower() == 'uploaders' :
                        buildDepends = value.split(', ')
                        currentPkg[field] = buildDepends
                    else:
                        if hasValue:
                            currentPkg[field] = value
                elif ',' in l:
                    try:
                        currentPkg[field] = currentPkg[field] + l.strip().split(', ')
                    except TypeError:
                        print "########"
                        print 
                        print currentPkg
                        print field
                        print l
                        print 
                        print "########"
                        continue
                elif 'checksum' in field.lower() or 'files' == field.lower():
                    hashvalue, size, filename = l.strip().split(' ')                  
                    if field in currentPkg.keys():
                        currentPkg[field].append((hashvalue,size,filename))
                    else:
                        currentPkg[field] = [(hashvalue,size,filename),]
                elif 'package-list' == field.lower():
                    s1, s2, s3, s4 = l.strip().split(' ')
                    if field in currentPkg.keys():
                        currentPkg[field].append((s1,s2,s3,s4))
                    else:
                        currentPkg[field] = [(s1,s2,s3,s4)]
                else:
                    currentPkg[field].append(l.strip())

                            
class Package (dict):

    def __init__(self):
        pass

        # if featDict:
        #     self.featDict = featDict
        # else:
        #     self.featDict = {'Package':'',
        #                       'Binary':'',
        #                       'Version':'',
        #                       'Priority':'',
        #                       'Section':'',
        #                       'Maintainer':'',
        #                       'Build-Depends':[],
        #                       'Architecture':'',
        #                       'Standards-Version':'',
        #                       'Format':'',
        #                       'Directory':'',
        #                       'Files':[],
        #                       'Uploaders':'',
        #                       'Checksums-sha1':[],
        #                       'Checksums-sha256':[]}

        
        
def start(sourcesFilePath, outputDir, baseURL, uccPath):

    s = SourcesFile(sourcesFilePath)
    s.parseAll()

    print "All packages parsed"
    
    retrievePackages(s, outputDir, baseURL)
    #measurePackages(s, outputDir, uccPath)

def measurePackages(sourcesFile, outputDir, uccPath):

    DEBIAN_LOCKS = '/gpfs/scratch/A20802011/a75877868/debian_locks_ucc/'
    DEBIAN_RESULTS = '/gpfs/projects/A20802011/sources/debian/results_ucc/'
    BASE_PATH = '/gpfs/projects/A20802011/sources/debian/'
    
    #DEBIAN_LOCKS = '/tmp/deblocks'
    #DEBIAN_RESULTS = '/tmp/debresults'
    #BASE_PATH = '/home/herraiz/research/debian/all_pkgs/'

    if not os.path.exists(DEBIAN_LOCKS):
        os.makedirs(DEBIAN_LOCKS)

    if not os.path.exists(DEBIAN_RESULTS):
        os.makedirs(DEBIAN_RESULTS)
        

    for pkg in sourcesFile.pkgs:

        name = pkg['Package']
        version = pkg['Version']

        #writeDirectory = os.path.join(outputDir, name)
        #writeDirectory = os.path.join(outputDir, version)

        origFiles = []
        diffFile = ''
        dscFile = ''

        for hashvalue, size, f in pkg['Files']:

            if 'diff.gz' == f[-7:].lower():
                # It is a diff file
                diffFile = f
            elif 'dsc' == f[-3:].lower():
                dscFile = f
            elif 'orig' in f:
                origFiles.append(f)

        # Measure orig files

        # Check if already measured
        resultsDir = os.path.join(DEBIAN_RESULTS,name)
        resultsDir = os.path.join(resultsDir,version)

        if os.path.exists(resultsDir):
            continue

                
        # Lock pkg + version
        lockFile = FileLock(os.path.join(DEBIAN_LOCKS,name+"."+version))
        try:
            lockFile.acquire()
        except AlreadyLocked:
            continue
        except LockFailed:
            print "ERROR Acquiring lock for %s @ %s" % (name, version)
            continue

        extractSourcesDir = os.path.join(DEBIAN_LOCKS,name+"_"+version)
        
        if not os.path.exists(extractSourcesDir):
            os.makedirs(extractSourcesDir)

        if not os.path.exists(resultsDir):
            os.makedirs(resultsDir)
            
        # Uncompress
        ftpdir = pkg['Directory']+'/'
        for o in origFiles:
            readDirectory = os.path.join(outputDir, ftpdir)
            oExtract = os.path.join(extractSourcesDir, o)
            oResult = os.path.join(resultsDir, o)
            if not os.path.exists(oResult):
                os.makedirs(oResult)
            try:
                tarf = tarfile.open(os.path.join(readDirectory,o))
                tarf.extractall(oExtract)
                tarf.close()
            except tarfile.ReadError:
                print " *** ERROR reading file %s from pkg %s %s at %s" % (o, name, version, os.path.join(readDirectory, o))
                continue
                                                                           
            # Create filelist.txt
            # Measure
            os.system('cd "%s" && find . > filelist.txt && %s -i1 filelist.txt' % (oExtract, uccPath))

            # Get CSV files
            os.system('cp "%s"/*.csv "%s"' % (oExtract, oResult))
            os.system('cp "%s"/error_log* "%s"' % (oExtract, oResult))
        # Apply diff patch
        
        
        # Look for Debian patches
        # Apply with patch -t -l -p1 -i
        # Measure again
        # Get new CSV files
        # Unlock package + version
        shutil.rmtree(extractSourcesDir)
        lockFile.release()

def measurePackagesSLOCCOUNT(sourcesFile, outputDir, uccPath):

    DEBIAN_LOCKS = '/gpfs/scratch/A20802011/a75877868/debian_locks_sloc/'
    DEBIAN_RESULTS = '/gpfs/projects/A20802011/sources/debian/results_sloccount/'
    BASE_PATH = '/gpfs/projects/A20802011/sources/debian/'
    
    #DEBIAN_LOCKS = '/tmp/deblocks'
    #DEBIAN_RESULTS = '/tmp/debresults'
    #BASE_PATH = '/home/herraiz/research/debian/all_pkgs/'

    if not os.path.exists(DEBIAN_LOCKS):
        os.makedirs(DEBIAN_LOCKS)

    if not os.path.exists(DEBIAN_RESULTS):
        os.makedirs(DEBIAN_RESULTS)
        

    for pkg in sourcesFile.pkgs:

        name = pkg['Package']
        version = pkg['Version']

        print "Measuring %s @ %s" % (name, version)

        origFiles = []
        diffFile = ''
        dscFile = ''

        for hashvalue, size, f in pkg['Files']:

            if 'diff.gz' == f[-7:].lower():
                # It is a diff file
                diffFile = f
            elif 'dsc' == f[-3:].lower():
                dscFile = f
            elif 'orig' in f or not ('debian' in f):
                origFiles.append(f)

        # Measure orig files

        # Lock pkg + version
        lockFile = FileLock(os.path.join(DEBIAN_LOCKS,name+"."+version))
        try:
            lockFile.acquire()
        except AlreadyLocked:
            continue
        except LockFailed:
            print "ERROR Acquiring lock for %s @ %s" % (name, version)
            continue
                    


        # Package not measured before

        extractSourcesDir = os.path.join(DEBIAN_LOCKS,name+"_"+version)
        
        if not os.path.exists(extractSourcesDir):
            os.makedirs(extractSourcesDir)

        resultsDir = os.path.join(DEBIAN_RESULTS,name)
        resultsDir = os.path.join(resultsDir,version)


        if not os.path.exists(resultsDir):
            os.makedirs(resultsDir)
            
        # Uncompress
        ftpdir = pkg['Directory']+'/'
        for o in origFiles:
            readDirectory = os.path.join(outputDir, ftpdir)
            oExtract = os.path.join(extractSourcesDir, o)
            oResult = os.path.join(resultsDir, o)
            if not os.path.exists(oResult):
                os.makedirs(oResult)


            # Check if already measured
            if os.path.exists(os.path.join(oResult,'results_sloccount.txt')):
                continue

            try:
                tarf = tarfile.open(os.path.join(readDirectory,o))
                tarf.extractall(oExtract)
                tarf.close()
            except tarfile.ReadError:
                print " *** ERROR reading file %s from pkg %s %s at %s" % (o, name, version, os.path.join(readDirectory, o))
                continue

            # Measure
            print "    File %s" % os.path.join(ftpdir,o)
            cacheDir = tempfile.mktemp(dir='/gpfs/scratch/A20802011/a75877868/tmp')
            if not os.path.exists(cacheDir):
                os.makedirs(cacheDir)
            os.system('cd "%s" && %s --wide --details --datadir "%s" . > results_sloccount.txt' % (oExtract, uccPath, cacheDir))
            os.system('cp "%s/results_sloccount.txt" "%s"' % (oExtract, oResult))
            if os.path.exists(cacheDir):
                shutil.rmtree(cacheDir)

        # Unlock package + version
        shutil.rmtree(extractSourcesDir)
        lockFile.release()

def retrievePackages(sourcesFile, outputDir, baseURL):

    ftp = ftplib.FTP ('ftp.rediris.es')

    ftp.login ()

    for pkg in sourcesFile.pkgs:

        name = pkg['Package']
        version = pkg['Version']
        ftpdir = pkg['Directory']+'/'
        writeDirectory = os.path.join(outputDir, ftpdir)

        try:
            os.makedirs(writeDirectory)
        except OSError:
            pass

        for hashvalue, size, f in pkg['Files']:
            #ftpURL = urlparse.urljoin(baseURL, ftpdir)
            #ftpURL = urlparse.urljoin(ftpURL, f)
            localPath = os.path.join(writeDirectory, f)

            if os.path.exists(localPath) and checkMD5File(hashvalue, localPath):
                print ">>> Avoiding good file from package %s @ %s" % (name, version)
                continue
            
            print ">>> Downloading file from package %s @ %s" % (name, version)
            #print ftpURL
            print localPath
            print writeDirectory
            #urllib.urlretrieve(ftpURL, localPath)
            ftpPath = 'mirror/debian/';
            ftpPath += os.path.join(ftpdir, f)
            print ftpPath
            try:
                ftp.retrbinary('RETR %s' % ftpPath, open(localPath, 'wb').write)
            except ftplib.all_errors:
                ftp.connect('ftp.rediris.es')
                ftp.login ()
                ftp.retrbinary('RETR %s' % ftpPath, open(localPath, 'wb').write)

            if checkMD5File(hashvalue, localPath):
                print "    OK"
            else:
                print "    ERROR"


def checkMD5File(h, f):


    
    f = open(f, 'rb')

    data = f.read(128)
    md5 = hashlib.md5(data)
    
    while data:
        data = f.read(128)
        md5.update(data)

    
    f.close()

    return h.lower() == md5.hexdigest().lower()
