# Refactored code by removing the function and cleanup.
import dlexer
import sys
import WildcardSearch

# Setup the parser.
parser = dlexer.DLexer(0)

__TOKEN_NEWLINE = parser.AddToken('\n')
__TOKEN_WHITESPACE = parser.AddToken('[ \\t\\f\\v]+')
__TOKEN_OPENBRACE = parser.AddToken('{')
__TOKEN_CLOSEBRACE = parser.AddToken('}')
__TOKEN_OPENPAREN = parser.AddToken(r'\(')
__TOKEN_CLOSEPAREN = parser.AddToken(r'\)')
__TOKEN_COMMENT = parser.AddToken(r"\/\/.*")

__TOKEN_CONST = parser.AddToken("const")
__TOKEN_IF = parser.AddToken("if")
__TOKEN_WHILE = parser.AddToken("while")
__TOKEN_FOR = parser.AddToken("for")
__TOKEN_SWITCH = parser.AddToken("switch")
__TOKEN_CLASS = parser.AddToken("class")
__TOKEN_PUBLIC = parser.AddToken("public")
__TOKEN_TYPEDEF = parser.AddToken("typedef")
__TOKEN_BASECLASS = parser.AddToken("BaseClass")

# Valid characters for identifiers (escaped for regex)
validChars = r"~@#$%^&!\w\.\-/\[\]<>\""
__TOKEN_IDENT = parser.AddToken('[' + validChars + ']+')
__TOKEN_OPERATOR = parser.AddToken(r"=|\+")
__TOKEN_SCOPE_OPERATOR = parser.AddToken("::")
__TOKEN_COLON = parser.AddToken(":")
__TOKEN_IGNORE = parser.AddToken(r"#|;|:|\||\?|'|\\|\*|-|`|,")

for i in range(1, len(sys.argv)):
    for filename in WildcardSearch.WildcardSearch(sys.argv[i]):

        # First, read all the tokens into a list.
        tokenList = []
        parser.BeginReadFile(filename)
        while True:
            m = parser.GetToken()
            if m:
                tokenList.append(m)
            else:
                break

        # Make a list of all the non-whitespace ones.
        nw = []
        for token in tokenList:
            if token.id == __TOKEN_NEWLINE or token.id == __TOKEN_WHITESPACE:
                token.iNonWhitespace = -2222
            else:
                token.iNonWhitespace = len(nw)
                nw.append(token)

        # Search for 'class <ident> : public <ident> {'
        for token in tokenList:
            if token.id == __TOKEN_CLASS:
                idx = token.iNonWhitespace
                # Bounds check: need at least 4 more tokens ahead
                if idx + 4 < len(nw):
                    if (nw[idx+1].id == __TOKEN_IDENT and
                        nw[idx+2].id == __TOKEN_COLON and
                        nw[idx+3].id == __TOKEN_PUBLIC and
                        nw[idx+4].id == __TOKEN_IDENT):
                        print "class %s : public %s" % (nw[idx+1].val, nw[idx+4].val)
