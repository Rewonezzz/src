# Refactored so it's clean I guess...
# Valve Pls Fix TwT
import WildcardSearch
import sys
import re
import os
import subprocess

curProps = {}

modelsContentFallbackDir = "c:\\hl2\\hl2\\models"
modelsContentDir = "c:\\hl2\\cstrike\\models"

materialsFallbackDir = "c:\\hl2\\hl2\\materials"
materialsDir = "c:\\hl2\\cstrike\\materials"
mapsDir = "c:\\hl2\\cstrike\\maps"
exeDir = "c:\\hl2\\bin"

# RE to look for '$surfaceProp blah'
surfacePropRE = re.compile(r'\"?\$surfaceprop\"?\s+\"?(?P<propname>[^\"]+)\"?', re.IGNORECASE)


# ------------------------------------------------------------------------------------------- #
# Helper functions.
# ------------------------------------------------------------------------------------------- #

def FileExists(path):
    return os.path.exists(path)
# FileExists? Nah, os.path.exists.

def SearchFile(filename):
    with open(filename, "rt") as f:
        PrintFilename(filename)
        fileData = f.read()
        match = surfacePropRE.search(fileData)
        if match:
            propName = match.group(1).upper()
            curProps[propName] = 1


def PrintFilename(filename):
    print filename


# ------------------------------------------------------------------------------------------- #
# Search all the map files for texture names and model files.
# ------------------------------------------------------------------------------------------- #
# Set, changed this to set. Don't know if it works though, this used to be empty.
usedVMTFiles = set()
modelFiles = set()

# RE to look for 'material blah'  (fixed: removed stray backslash before 'material')
materialRE = re.compile(r'\"?material\"?\s+\"?(?P<matname>[^\"]+)\"?', re.IGNORECASE)

# Look for a model name referenced in the VMF file.
modelRE = re.compile(r'\"models\/(?P<modelname>.+)\.mdl\"', re.IGNORECASE)

mapsPattern = os.path.join(mapsDir, "*.vmf")
files = WildcardSearch.WildcardSearch(mapsPattern, 1)
for filename in files:
    with open(filename, "rt") as f:
        fileData = f.read()

    PrintFilename(filename)

    # Get all the model names.
    allMatches = modelRE.findall(fileData)
    for match in allMatches:
        modelFiles.add(match.upper())

    # Get all the texture names.
    allMatches = materialRE.findall(fileData)
    for match in allMatches:
        usedVMTFiles.add(match)


# ------------------------------------------------------------------------------------------- #
# Search all the model files for surface props.
# ------------------------------------------------------------------------------------------- #

# Make sure we look at ALL models in the CStrike folder.
modelsPattern = os.path.join(modelsContentDir, "*.mdl")
for filename in WildcardSearch.WildcardSearch(modelsPattern, 1):
    modelFiles.add(filename.upper())

for iModel in modelFiles:
    iModel = iModel.replace("/", "\\")
    filename = os.path.join(modelsContentDir, iModel + ".mdl")
    if not FileExists(filename):
        filename = os.path.join(modelsContentFallbackDir, iModel + ".mdl")
# here lies what used to be deprecated code
    if FileExists(filename):
        PrintFilename(filename)

        # I changed something here, it might break.
        cmd = '"%s\\studiomdl.exe" -PrintSurfaceProps "%s"' % (exeDir, filename)
        try:
            output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
            for line in output.splitlines():
                curProps[line.upper().strip()] = 1
        except subprocess.CalledProcessError as e:
            print >>sys.stderr, "Error running studiomdl on %s: %s" % (filename, e)
        except OSError as e:
            print >>sys.stderr, "studiomdl.exe not found: %s" % e

# Tried error handling here for missing studiomdl.exe

# ------------------------------------------------------------------------------------------- #
# Search all the texture files for surface props.
# ------------------------------------------------------------------------------------------- #

for vmtName in usedVMTFiles:
    filename = os.path.join(materialsDir, vmtName + ".vmt")
    if not FileExists(filename):
        filename = os.path.join(materialsFallbackDir, vmtName + ".vmt")

    if FileExists(filename):
        SearchFile(filename)


# ------------------------------------------------------------------------------------------- #
# Output the results.
# ------------------------------------------------------------------------------------------- #

print "\n"
print "---------------------------------"
print "- Surface types found"
print "---------------------------------\n"

sortedList = sorted(curProps.keys())
for x in sortedList:
    print x
