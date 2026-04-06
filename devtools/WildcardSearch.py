# I genuinely have no idea if this fixes shit
import os
import re
import stat


# This takes a DOS filename wildcard like *abc.t?t and returns a regex string that will match it.
def GetRegExForDOSWildcard( wildcard ):
	# First find the base directory name.
	iLast = wildcard.rfind( "/" )
	if iLast == -1:
		iLast = wildcard.rfind( "\\" )

	if iLast == -1:
		dirName = "."
		dosStyleWildcard = wildcard
	else:
		dirName = wildcard[0:iLast]
		dosStyleWildcard = wildcard[iLast+1:]

	# Now generate a regular expression for the search.
	# DOS     -> RE
	# *       -> .*
	# .       -> \.
	# ?       -> .
	# Escape regex special characters first, then replace escaped * and ? with wildcards
	reString = re.escape( dosStyleWildcard )
	reString = reString.replace( r"\*", ".*" ).replace( r"\?", "." )
	return reString, dirName


#
# Useful function to return a list of files in a directory based on a dos-style wildcard like "*.txt"
#
# for name in WildcardSearch( "d:/hl2/src4/dt*.cpp", 1 ):
#	print name
#
def WildcardSearch( wildcard, bRecurse=0 ):
	reString, dirName = GetRegExForDOSWildcard( wildcard )
	# Anchor to full filename match
	matcher = re.compile( "^" + reString + "$", re.IGNORECASE )

	return __GetFiles_R( matcher, dirName, bRecurse )

def __GetFiles_R( matcher, dirName, bRecurse ):
	result = []
	try:
		files = os.listdir( dirName )
	except OSError:
		return result
	for baseName in files:
		filename = os.path.join( dirName, baseName )
		try:
			mode = os.stat( filename ).st_mode
		except OSError:
			continue
		if stat.S_ISREG( mode ):
			if matcher.match( baseName ):
				result.append( filename )
		elif bRecurse and stat.S_ISDIR( mode ):
			result.extend( __GetFiles_R( matcher, filename, bRecurse ) )
	return result
