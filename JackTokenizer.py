"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing
import re


class JackTokenizer:
    """Removes all comments from the input stream and breaks it
    into Jack language tokens, as specified by the Jack grammar.
    
    # Jack Language Grammar

    A Jack file is a stream of characters. If the file represents a
    valid program, it can be tokenized into a stream of valid tokens. The
    tokens may be separated by an arbitrary number of whitespace characters, 
    and comments, which are ignored. There are three possible comment formats: 
    /* comment until closing */ , /** API comment until closing */ , and 
    // comment until the line’s end.

    - ‘xxx’: quotes are used for tokens that appear verbatim (‘terminals’).
    - xxx: regular typeface is used for names of language constructs 
           (‘non-terminals’).
    - (): parentheses are used for grouping of language constructs.
    - x | y: indicates that either x or y can appear.
    - x?: indicates that x appears 0 or 1 times.
    - x*: indicates that x appears 0 or more times.

    ## Lexical Elements

    The Jack language includes five types of terminal elements (tokens).

    - keyword: 'class' | 'constructor' | 'function' | 'method' | 'field' | 
               'static' | 'var' | 'int' | 'char' | 'boolean' | 'void' | 'true' |
               'false' | 'null' | 'this' | 'let' | 'do' | 'if' | 'else' | 
               'while' | 'return'
    - symbol: '{' | '}' | '(' | ')' | '[' | ']' | '.' | ',' | ';' | '+' | 
              '-' | '*' | '/' | '&' | '|' | '<' | '>' | '=' | '~' | '^' | '#'
    - integerConstant: A decimal number in the range 0-32767.
    - StringConstant: '"' A sequence of Unicode characters not including 
                      double quote or newline '"'
    - identifier: A sequence of letters, digits, and underscore ('_') not 
                  starting with a digit. You can assume keywords cannot be
                  identifiers, so 'self' cannot be an identifier, etc'.

    ## Program Structure

    A Jack program is a collection of classes, each appearing in a separate 
    file. A compilation unit is a single class. A class is a sequence of tokens 
    structured according to the following context free syntax:
    
    - class: 'class' className '{' classVarDec* subroutineDec* '}'
    - classVarDec: ('static' | 'field') type varName (',' varName)* ';'
    - type: 'int' | 'char' | 'boolean' | className
    - subroutineDec: ('constructor' | 'function' | 'method') ('void' | type) 
    - subroutineName '(' parameterList ')' subroutineBody
    - parameterList: ((type varName) (',' type varName)*)?
    - subroutineBody: '{' varDec* statements '}'
    - varDec: 'var' type varName (',' varName)* ';'
    - className: identifier
    - subroutineName: identifier
    - varName: identifier

    ## Statements

    - statements: statement*
    - statement: letStatement | ifStatement | whileStatement | doStatement | 
                 returnStatement
    - letStatement: 'let' varName ('[' expression ']')? '=' expression ';'
    - ifStatement: 'if' '(' expression ')' '{' statements '}' ('else' '{' 
                   statements '}')?
    - whileStatement: 'while' '(' 'expression' ')' '{' statements '}'
    - doStatement: 'do' subroutineCall ';'
    - returnStatement: 'return' expression? ';'

    ## Expressions
    
    - expression: term (op term)*
    - term: integerConstant | stringConstant | keywordConstant | varName | 
            varName '['expression']' | subroutineCall | '(' expression ')' | 
            unaryOp term
    - subroutineCall: subroutineName '(' expressionList ')' | (className | 
                      varName) '.' subroutineName '(' expressionList ')'
    - expressionList: (expression (',' expression)* )?
    - op: '+' | '-' | '*' | '/' | '&' | '|' | '<' | '>' | '='
    - unaryOp: '-' | '~' | '^' | '#'
    - keywordConstant: 'true' | 'false' | 'null' | 'this'
    
    Note that ^, # correspond to shiftleft and shiftright, respectively.
    """

    KEYWORDS = {
        'class': 'CLASS',
        'method': 'METHOD',
        'function': 'FUNCTION',
        'constructor': 'CONSTRUCTOR',
        'int': 'INT',
        'boolean': 'BOOLEAN',
        'char': 'CHAR',
        'void': 'VOID',
        'var': 'VAR',
        'static': 'STATIC',
        'field': 'FIELD',
        'let': 'LET',
        'do': 'DO',
        'if': 'IF',
        'else': 'ELSE',
        'while': 'WHILE',
        'return': 'RETURN',
        'true': 'TRUE',
        'false': 'FALSE',
        'null': 'NULL',
        'this': 'THIS'
    }

    def __init__(self, input_stream: typing.TextIO) -> None:
        """Opens the input stream and gets ready to tokenize it.

        Args:
            input_stream (typing.TextIO): input stream.
        """

        # Define regex patterns for each token type
        keyword_pattern = r'\b(class|constructor|function|method|field|static|var|int|char|boolean|void|true|false|null|this|let|do|if|else|while|return)\b'
        symbol_pattern = r'[{}()\[\].,;+\-*/&|<>=~^#]'
        integer_pattern = r'\b\d{1,5}\b'  # Matches integers from 0 to 32767
        string_pattern = r'"([^"\n]*)"'  # Matches string literals
        identifier_pattern = r'\b[a-zA-Z_]\w*\b'  # Matches valid identifiers

        # Combine all patterns into one pattern for matching
        self.elements_pattern = f"({keyword_pattern}|{symbol_pattern}|{integer_pattern}|{string_pattern}|{identifier_pattern})"

        self.elements_pattern1 = r"""
                \b(class|constructor|function|method|field|static|var|
                int|char|boolean|void|true|false|null|this|let|do|if|
                else|while|return)\b|\{|\}|\(|\)|\[|\]|\.|,|;|\+|\-|\*|\/|&|\||<|>|=|~|\^|# |
                "[^"\n]*" |
                \b\d+\b |
                \b[A-Za-z_]\w*\b
            """


        input_text = input_stream.read()

        # remove multi-line comments (/* ... */ and /** ... */)
        input_text = re.sub(r"/\*.*?\*/", "", input_text, flags=re.DOTALL)

        input_lines = input_text.splitlines()

        lines = list()  # orders in file
        # remove inline remarks and strip
        for line in input_lines:
            line = line.strip().split("//", 1)[0].strip()
            if is_valid_line(line):
                lines.append(line)

        input_stream.close()

        # Tokenize lines into tokens
        self.tokens = self.tokenize_lines(lines)
        self.token_index = -1  # no token is currently chosen


    def tokenize_lines(self, lines: list) -> list:
        """Tokenizes all lines and returns a list of tokens.

        Returns:
            list: List of tokens extracted from the lines.
        """
        token_regex = re.compile(self.elements_pattern, re.VERBOSE)

        tokens = []
        for line in lines:
            tokens.extend(self.process_line(line))
        return tokens

    def has_more_tokens(self) -> bool:
        """Do we have more tokens in the input?

        Returns:
            bool: True if there are more tokens, False otherwise.
        """
        return self.token_index + 1 < len(self.tokens)

    def advance(self) -> None:
        """Gets the next token from the input and makes it the current token. 
        This method should be called if has_more_tokens() is true. 
        Initially there is no current token.
        """
        self.token_index += 1

    def token_type(self) -> str:
        """
        Returns:
            str: the type of the current token, can be
            "KEYWORD", "SYMBOL", "IDENTIFIER", "INT_CONST", "STRING_CONST"
        """
        token = self.tokens[self.token_index]

        if token in JackTokenizer.KEYWORDS:
            return "KEYWORD"

        symbols = {'{', '}', '(', ')', '[', ']', '.', ',', ';', '+', '-', '*',
                   '/', '&', '|', '<', '>', '=', '~', '^', '#'}
        if token in symbols:
            return "SYMBOL"

        if token.isdigit():
            return "INT_CONST"

        if token.startswith('"') and token.endswith('"'):
            return "STRING_CONST"

        identifier_pattern = r'^[A-Za-z_]\w*$'
        if re.match(identifier_pattern, token):
            return "IDENTIFIER"

        raise ValueError(f"Unknown token type for token: {token}")

    def keyword(self) -> str:
        """
        Returns:
            str: the keyword which is the current token.
            Should be called only when token_type() is "KEYWORD".
            Can return "CLASS", "METHOD", "FUNCTION", "CONSTRUCTOR", "INT", 
            "BOOLEAN", "CHAR", "VOID", "VAR", "STATIC", "FIELD", "LET", "DO", 
            "IF", "ELSE", "WHILE", "RETURN", "TRUE", "FALSE", "NULL", "THIS"
        """
        return self.KEYWORDS[self.tokens[self.token_index]]

    def symbol(self) -> str:
        """
        Returns:
            str: the character which is the current token.
            Should be called only when token_type() is "SYMBOL".
            Recall that symbol was defined in the grammar like so:
            symbol: '{' | '}' | '(' | ')' | '[' | ']' | '.' | ',' | ';' | '+' | 
              '-' | '*' | '/' | '&' | '|' | '<' | '>' | '=' | '~' | '^' | '#'
        """
        return self.tokens[self.token_index]

    def identifier(self) -> str:
        """
        Returns:
            str: the identifier which is the current token.
            Should be called only when token_type() is "IDENTIFIER".
            Recall that identifiers were defined in the grammar like so:
            identifier: A sequence of letters, digits, and underscore ('_') not 
                  starting with a digit. You can assume keywords cannot be
                  identifiers, so 'self' cannot be an identifier, etc'.
        """
        return self.tokens[self.token_index]

    def int_val(self) -> int:
        """
        Returns:
            str: the integer value of the current token.
            Should be called only when token_type() is "INT_CONST".
            Recall that integerConstant was defined in the grammar like so:
            integerConstant: A decimal number in the range 0-32767.
        """
        return int(self.tokens[self.token_index])

    def string_val(self) -> str:
        """
        Returns:
            str: the string value of the current token, without the double 
            quotes. Should be called only when token_type() is "STRING_CONST".
            Recall that StringConstant was defined in the grammar like so:
            StringConstant: '"' A sequence of Unicode characters not including 
                      double quote or newline '"'
        """
        return self.tokens[self.token_index].strip('"')


    def process_line(self, line):
        """Splits a line into words, then tokenizes each word."""

        # Use re.finditer to match all tokens
        tokens = []
        for match in re.finditer(self.elements_pattern, line):
            token = match.group(0)
            tokens.append(token)
        return tokens


def is_valid_line(line):
    """
    Check if line contains content
    """
    return line != ""