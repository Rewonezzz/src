# Dead code everywhere, what the hell...
# Assuming all functions begin with ')' followed by '{', just find the matching brace and
# add a line with 'g_pVCR->SyncToken("<random string here>");'

import dlexer
import sys


def MatchParensBack(token_list, iStart):
    parenCount = -1
    for i in range(0, iStart):
        if token_list[iStart - i].id == __TOKEN_OPENPAREN:
            parenCount += 1
        elif token_list[iStart - i].id == __TOKEN_CLOSEPAREN:
            parenCount -= 1

        if parenCount == 0:
            return iStart - i
    return -1


if len(sys.argv) >= 2:

    # Setup the parser.
    parser = dlexer.DLexer(0)
# Regex cleaned
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

    validChars = r"~@#$%^&!,\w\.\-/\[\]<>\""
    __TOKEN_IDENT = parser.AddToken('[' + validChars + ']+')
    __TOKEN_OPERATOR = parser.AddToken(r"=|\+")
    __TOKEN_SCOPE_OPERATOR = parser.AddToken("::")
    __TOKEN_IGNORE = parser.AddToken(r"#|;|:|\||\?|'|\\|\*|-|`")

    # First, read all the tokens into a list.
    tokens = []
    parser.BeginReadFile(sys.argv[1])
    while True:
        m = parser.GetToken()
        if m:
            tokens.append(m)
        else:
            break

    # Make a list of all the non-whitespace ones.
    non_whitespace = []
    for token in tokens:
        if token.id in (__TOKEN_NEWLINE, __TOKEN_WHITESPACE):
            token.iNonWhitespace = -2222
        else:
            token.iNonWhitespace = len(non_whitespace)
            non_whitespace.append(token)

    # Write directly to the original file (but with 'with' to ensure closure! Makes it automatic)
    with open(sys.argv[1], 'w') as out_file:
        curLine = 1
        iCur = 0

        # Now, search for the patterns
        # Look for <ident>::<ident> '(' <idents...> ')' followed by a '{'. This would be a function.
        for token in tokens:
            out_file.write(token.val)
            if token.id == __TOKEN_NEWLINE:
                curLine += 1

            if token.id == __TOKEN_OPENBRACE:
                idx = token.iNonWhitespace
                # Bounds checking (needed): need at least 6 non-whitespace tokens before this brace,
                # and the previous token must be a closing parenthesis.
                if idx >= 6 and non_whitespace[idx - 1].id == __TOKEN_CLOSEPAREN:
                    pos = MatchParensBack(non_whitespace, idx - 2)
                    # Ensure pos is valid and there's an identifier before it.
                    if pos != -1 and pos - 1 >= 0:
                        if non_whitespace[pos - 1].id == __TOKEN_IDENT:
                            # ADD PROLOGUE CODE HERE!!
                            # out_file.write("\n\tg_pVCR->SyncToken( \"%d_%s\" ); // AUTO-GENERATED SYNC TOKEN\n" % (iCur, non_whitespace[pos - 1].val))
                            iCur += 1

                            # Test code to print function names or something.
                            # if pos - 2 >= 0 and non_whitespace[pos - 2].id == __TOKEN_SCOPE_OPERATOR:
                            #     print "%d: %s::%s" % (curLine, non_whitespace[pos - 3].val, non_whitespace[pos - 1].val)
                            # else:
                            #     print "%d: %s" % (curLine, non_whitespace[pos - 1].val)

else:
    print "VCRMode_AddSyncTokens <filename>"
# Python 2!
