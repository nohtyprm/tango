'''
Test lexer
'''

import unittest

if __name__ == "__main__":
    import sys
    sys.path.append("../src")

import tangolib
from tangolib.lexer import Char, CharIn, Regexp, make_string_tokenizer
import tangolib.eregex as ere

class TestLexerString(unittest.TestCase):
    def test_emph(self):
        underscore = tangolib.lexer.Char("underscore", '_')
        space = tangolib.lexer.CharIn("space", ' ', '\t')
        word = tangolib.lexer.Regexp("word", ere.ERegex(r'([^_ \t\n\r\f\v]+)'))

        tokens = tangolib.lexer.make_string_tokenizer("_example in emphasis_")

        token = underscore.recognize(tokens)
        self.assertEqual(token.token_type,'underscore')
        self.assertEqual(token.value,'_')
        self.assertEqual(tokens.show_lines(1,cursor="<>") , "_<>example in emphasis_")
        self.assertEqual(tokens.pos.offset,1)

        token = underscore.recognize(tokens)
        self.assertEqual(token,None)
        self.assertEqual(tokens.pos.offset,1)

        token = word.recognize(tokens)
        self.assertEqual(token.token_type,'word')
        self.assertEqual(tokens.pos.offset,8)

        token = word.recognize(tokens)
        self.assertEqual(token,None)
        self.assertEqual(tokens.pos.offset,8)

        token = space.recognize(tokens)
        self.assertEqual(token.token_type,'space')
        self.assertEqual(tokens.pos.offset,9)

        tokens.reset()
        lexer = tangolib.lexer.Lexer(tokens, underscore, space, word)
        token = lexer.next_token()
        self.assertEqual(token.token_type, 'underscore')
        token = lexer.next_token()
        self.assertEqual(token.token_type, 'word')
        lexer.putback(token)
        token = lexer.next_token()
        self.assertEqual(token.token_type, 'word')

        tokens.reset()
        toks = [ tok for tok in lexer ]
        print("toks={}".format(toks))
        self.assertEqual([tok.token_type for tok in toks],['underscore', 'word', 'space', 'word', 'space', 'word', 'underscore'])
        

if __name__ == '__main__':
    unittest.main()
