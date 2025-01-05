"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing

import JackTokenizer


class CompilationEngine:
    """Gets input from a JackTokenizer and emits its parsed structure into an
    output stream.
    """

    UNARY_OP = {'-', '~', '^', '#'}
    KEYWORD_CONSTANTS = {'true', 'false', 'null', 'this'}
    STATEMENT_PREFIX = {"while", "do", "return", "let", "if"}
    OP = {'+', '-', '*', '/', '&', '|', '<', '>', '='}

    def __init__(self, input_stream: JackTokenizer,
                 output_stream: typing.TextIO) -> None:
        """
        Creates a new compilation engine with the given input and output. The
        next routine called must be compileClass()
        :param input_stream: The input stream.
        :param output_stream: The output stream.
        """
        # Your code goes here!
        # Note that you can write to output_stream like so:
        # output_stream.write("Hello world! \n")
        self.tokenizer = input_stream
        self.tokenizer.advance()  # now tokenizer set to first token
        self.output_stream = output_stream

    def writeTag(self, tag: str, content: str):
        self.output_stream.write(f"<{tag}> {content} </{tag}>\n")

    def writeKeyword(self, content: str):
        self.writeTag("keyword", content)

    def writeSymbol(self, content: str):
        self.writeTag("symbol", content)

    def writeIdentifier(self, content: str):
        self.writeTag("identifier", content)

    def writeIntConst(self, content: str):
        self.writeTag("integerConstant", content)

    def writeStrConst(self, content: str):
        self.writeTag("stringConstant", content)

    def compile_class(self) -> None:
        """Compiles a complete class."""
        self.output_stream.write("<class>\n")

        self.writeKeyword(self.tokenizer.keyword())  # 'class'
        self.tokenizer.advance()
        self.writeIdentifier(self.tokenizer.identifier())  # class name
        self.tokenizer.advance()
        self.writeSymbol(self.tokenizer.symbol())  # {
        self.tokenizer.advance()

        while (self.tokenizer.token_type() == "KEYWORD" and
               self.tokenizer.keyword() in {"static", "field"}):
            self.compile_class_var_dec()

        while (self.tokenizer.token_type() == "KEYWORD" and
               self.tokenizer.keyword() in {"constructor", "function",
                                            "method"}):
            self.compile_subroutine()

        self.writeSymbol(self.tokenizer.symbol())  # }
        self.output_stream.write("</class>")

    def compile_class_var_dec(self) -> None:
        """Compiles a static declaration or a field declaration."""
        self.output_stream.write("<classVarDec>\n")
        self.writeKeyword(self.tokenizer.keyword())  # 'field/static'
        self.tokenizer.advance()
        self.compile_type()  # type
        self.tokenizer.advance()
        self.writeIdentifier(self.tokenizer.identifier())  # varName
        self.tokenizer.advance()

        # handle additional variable names separated by commas
        while (self.tokenizer.token_type() == "SYMBOL" and
               self.tokenizer.symbol() == ','):
            self.writeSymbol(self.tokenizer.symbol())  # ,
            self.tokenizer.advance()
            self.writeIdentifier(self.tokenizer.identifier())  # varName
            self.tokenizer.advance()

        self.writeSymbol(self.tokenizer.symbol())  # ;
        self.tokenizer.advance()
        self.output_stream.write("</classVarDec>\n")

    def compile_subroutine(self) -> None:
        """
        Compiles a complete method, function, or constructor.
        You can assume that classes with constructors have at least one field,
        you will understand why this is necessary in project 11.
        """
        self.output_stream.write("<subroutineDec>\n")
        self.writeKeyword(
            self.tokenizer.keyword())  # 'constractor/function/method'
        self.tokenizer.advance()
        if self.tokenizer.token_type() == "KEYWORD" and self.tokenizer.keyword() == 'void':
            self.writeKeyword(self.tokenizer.keyword())  # 'void'
        else:
            self.compile_type()  # type
        self.tokenizer.advance()
        self.writeIdentifier(self.tokenizer.identifier())  # subRoutineName
        self.tokenizer.advance()
        self.writeSymbol(self.tokenizer.symbol())  # (
        self.tokenizer.advance()
        self.compile_parameter_list()  # parameter list
        self.writeSymbol(self.tokenizer.symbol())  # )
        self.tokenizer.advance()
        self.output_stream.write("<subroutineBody>\n")
        self.writeSymbol(self.tokenizer.symbol())  # {
        self.tokenizer.advance()

        # compile variable declarations
        while self.tokenizer.token_type() == "KEYWORD" and self.tokenizer.keyword() == "var":
            self.compile_var_dec()

        self.compile_statements()  # routine body - dec
        self.writeSymbol(self.tokenizer.symbol())  # }
        self.tokenizer.advance()
        self.output_stream.write("</subroutineBody>\n")

        self.output_stream.write("</subroutineDec>\n")

    def compile_parameter_list(self) -> None:
        """Compiles a (possibly empty) parameter list, not including the
        enclosing "()".
        """
        self.output_stream.write("<parameterList>\n")
        if not (
                self.tokenizer.token_type() == "SYMBOL" and self.tokenizer.symbol() == ")"):
            self.compile_type()  # type
            self.tokenizer.advance()
            self.writeIdentifier(self.tokenizer.identifier())  # var name
            self.tokenizer.advance()

            # handle additional variable names separated by commas
            while (self.tokenizer.token_type() == "SYMBOL" and
                   self.tokenizer.symbol() == ','):
                self.writeSymbol(self.tokenizer.symbol())  # ,
                self.tokenizer.advance()
                self.compile_type()  # type
                self.tokenizer.advance()
                self.writeIdentifier(self.tokenizer.identifier())  # var name
                self.tokenizer.advance()

        self.output_stream.write("</parameterList>\n")

    def compile_var_dec(self) -> None:
        """Compiles a var declaration."""
        self.output_stream.write("<varDec>\n")
        self.writeKeyword(self.tokenizer.keyword())  # 'var'
        self.tokenizer.advance()
        self.compile_type()  # type
        self.tokenizer.advance()
        self.writeIdentifier(self.tokenizer.identifier())  # varName
        self.tokenizer.advance()

        # handle additional variable names separated by commas
        while (self.tokenizer.token_type() == "SYMBOL" and
               self.tokenizer.symbol() == ','):
            self.writeSymbol(self.tokenizer.symbol())  # ,
            self.tokenizer.advance()
            self.writeIdentifier(self.tokenizer.identifier())  # varName
            self.tokenizer.advance()

        self.writeSymbol(self.tokenizer.symbol())  # ;
        self.tokenizer.advance()

        self.output_stream.write("</varDec>\n")

    def compile_statements(self) -> None:
        """Compiles a sequence of statements, not including the enclosing
        "{}".
        """
        self.output_stream.write("<statements>\n")
        while (self.tokenizer.token_type() == "KEYWORD" and
               self.tokenizer.keyword() in CompilationEngine.STATEMENT_PREFIX):
            if self.tokenizer.keyword() == "do":
                self.compile_do()
            elif self.tokenizer.keyword() == "let":
                self.compile_let()
            elif self.tokenizer.keyword() == "while":
                self.compile_while()
            elif self.tokenizer.keyword() == "return":
                self.compile_return()
            elif self.tokenizer.keyword() == "if":
                self.compile_if()
            else:
                raise ValueError(
                    f"Unsupported token type: {self.tokenizer.keyword()}")
        self.output_stream.write("</statements>\n")

    def compile_do(self) -> None:
        """Compiles a do statement."""
        self.output_stream.write("<doStatement>\n")
        self.writeKeyword(self.tokenizer.keyword())  # do
        self.tokenizer.advance()
        var_name = self.tokenizer.identifier()
        self.tokenizer.advance()
        self.compile_subroutine_call(var_name)  # subroutineCall
        self.writeSymbol(self.tokenizer.symbol())  # ;
        self.tokenizer.advance()
        self.output_stream.write("</doStatement>\n")

    def compile_let(self) -> None:
        """Compiles a let statement."""
        self.output_stream.write("<letStatement>\n")
        self.writeKeyword(self.tokenizer.keyword())  # let
        self.tokenizer.advance()
        self.writeIdentifier(self.tokenizer.identifier())  # varName
        self.tokenizer.advance()
        if self.tokenizer.token_type() == "SYMBOL" and self.tokenizer.symbol() == "[":
            self.writeSymbol(self.tokenizer.symbol())  # [
            self.tokenizer.advance()
            self.compile_expression()  # expression
            self.writeSymbol(self.tokenizer.symbol())  # ]
            self.tokenizer.advance()
        self.writeSymbol(self.tokenizer.symbol())  # =
        self.tokenizer.advance()
        self.compile_expression()  # expression
        self.writeSymbol(self.tokenizer.symbol())  # ;
        self.tokenizer.advance()
        self.output_stream.write("</letStatement>\n")

    def compile_while(self) -> None:
        """Compiles a while statement."""
        self.output_stream.write("<whileStatement>\n")
        self.writeKeyword(self.tokenizer.keyword())  # while
        self.tokenizer.advance()
        self.writeSymbol(self.tokenizer.symbol())  # (
        self.tokenizer.advance()
        self.compile_expression()  # expression
        self.writeSymbol(self.tokenizer.symbol())  # )
        self.tokenizer.advance()
        self.writeSymbol(self.tokenizer.symbol())  # {
        self.tokenizer.advance()
        self.compile_statements()  # statements
        self.writeSymbol(self.tokenizer.symbol())  # }
        self.tokenizer.advance()
        self.output_stream.write("</whileStatement>\n")

    def compile_return(self) -> None:
        """Compiles a return statement."""
        self.output_stream.write("<returnStatement>\n")
        self.writeKeyword(self.tokenizer.keyword())  # return
        self.tokenizer.advance()
        if not (self.tokenizer.token_type() == "SYMBOL" and
                self.tokenizer.symbol() == ";"):
            self.compile_expression()
        self.writeSymbol(self.tokenizer.symbol())  # ;
        self.tokenizer.advance()
        self.output_stream.write("</returnStatement>\n")

    def compile_if(self) -> None:
        """Compiles a if statement, possibly with a trailing else clause."""
        # - ifStatement: 'if' '(' expression ')' '{' statements '}' ('else' '{'
        #                    statements '}')?
        self.output_stream.write("<ifStatement>\n")
        self.writeKeyword(self.tokenizer.keyword())  # if
        self.tokenizer.advance()
        self.writeSymbol(self.tokenizer.symbol())  # (
        self.tokenizer.advance()
        self.compile_expression()
        self.writeSymbol(self.tokenizer.symbol())  # )
        self.tokenizer.advance()
        self.writeSymbol(self.tokenizer.symbol())  # {
        self.tokenizer.advance()
        self.compile_statements()
        self.writeSymbol(self.tokenizer.symbol())  # }
        self.tokenizer.advance()
        if self.tokenizer.token_type() == "KEYWORD" and self.tokenizer.keyword() == "else":
            self.writeKeyword(self.tokenizer.keyword())  # else
            self.tokenizer.advance()
            self.writeSymbol(self.tokenizer.symbol())  # {
            self.tokenizer.advance()
            self.compile_statements()
            self.writeSymbol(self.tokenizer.symbol())  # }
            self.tokenizer.advance()
        self.output_stream.write("</ifStatement>\n")

    def compile_expression(self) -> None:
        """Compiles an expression."""
        self.compile_term()
        while (self.tokenizer.token_type() == "SYMBOL" and
               self.tokenizer.symbol() in CompilationEngine.OP):
            self.writeSymbol(self.tokenizer.symbol())  # op
            self.tokenizer.advance()
            self.compile_term()

    def compile_term(self) -> None:
        """Compiles a term.
        This routine is faced with a slight difficulty when
        trying to decide between some of the alternative parsing rules.
        Specifically, if the current token is an identifier, the routing must
        distinguish between a variable, an array entry, and a subroutine call.
        A single look-ahead token, which may be one of "[", "(", or "." suffices
        to distinguish between the three possibilities. Any other token is not
        part of this term and should not be advanced over.
        """
        if self.tokenizer.token_type() == "INT_CONST":
            self.writeIntConst(self.tokenizer.int_val())
            self.tokenizer.advance()
        elif self.tokenizer.token_type() == "STRING_CONST":
            self.writeStrConst(self.tokenizer.string_val())
            self.tokenizer.advance()
        elif (self.tokenizer.token_type() == "KEYWORD" and
              self.tokenizer.keyword() in CompilationEngine.KEYWORD_CONSTANTS):
            self.writeKeyword(self.tokenizer.keyword())
            self.tokenizer.advance()
        elif self.tokenizer.token_type() == "IDENTIFIER":
            var_name = self.tokenizer.identifier()
            self.tokenizer.advance()
            if self.tokenizer.token_type() == "SYMBOL" and self.tokenizer.symbol() == "[":
                # array
                self.writeIdentifier(var_name)
                self.writeSymbol(self.tokenizer.symbol())  # [
                self.tokenizer.advance()
                self.compile_expression()
                self.writeSymbol(self.tokenizer.symbol())  # ]
                self.tokenizer.advance()
            elif (self.tokenizer.token_type() == "SYMBOL" and
                  self.tokenizer.symbol() in ("(", ".")):
                # subroutineCall:
                self.compile_subroutine_call(var_name)
            else:
                # Simple variable
                self.writeIdentifier(var_name)
        elif self.tokenizer.token_type() == "SYMBOL" and self.tokenizer.symbol() == "(":
            # ( expression )
            self.writeSymbol(self.tokenizer.symbol())  # (
            self.tokenizer.advance()
            self.compile_expression()
            self.writeSymbol(self.tokenizer.symbol())  # )
            self.tokenizer.advance()
        elif self.tokenizer.token_type() == "SYMBOL" and self.tokenizer.symbol() in CompilationEngine.UNARY_OP:
            # Handle unaryOp term
            self.writeSymbol(self.tokenizer.symbol())
            self.tokenizer.advance()
            self.compile_term()
        else:
            raise ValueError(
                f"Unexpected token: {self.tokenizer.token_type()}")

    def compile_expression_list(self) -> None:
        """Compiles a (possibly empty) comma-separated list of expressions."""
        #     - expressionList: (expression (',' expression)* )? todo
        #  check if empty
        if (not self.tokenizer.token_type() == "SYMBOL" and
                self.tokenizer.symbol() == ")"):
            self.compile_expression()
            while (self.tokenizer.token_type() == "SYMBOL" and
                   self.tokenizer.symbol() == ","):
                self.writeSymbol(self.tokenizer.symbol())  # ,
                self.tokenizer.advance()
                self.compile_expression()

    def compile_type(self):
        if self.tokenizer.token_type() == "KEYWORD":
            self.writeKeyword(self.tokenizer.keyword())  # 'int/char/boolean'
        elif self.tokenizer.token_type() == "IDENTIFIER":
            self.writeIdentifier(self.tokenizer.identifier())  # className

    def compile_subroutine_call(self, identifier):
        self.writeIdentifier(identifier)
        if self.tokenizer.symbol() == "(":
            self.writeSymbol(self.tokenizer.symbol())  # (
            self.tokenizer.advance()
            self.compile_expression_list()
            self.writeSymbol(self.tokenizer.symbol())  # )
            self.tokenizer.advance()
        elif self.tokenizer.symbol() == ".":
            self.writeSymbol(self.tokenizer.symbol())  # .
            self.tokenizer.advance()
            self.writeIdentifier(self.tokenizer.identifier())  # subroutineName
            self.tokenizer.advance()
            self.writeSymbol(self.tokenizer.symbol())  # (
            self.tokenizer.advance()
            self.compile_expression_list()
            self.writeSymbol(self.tokenizer.symbol())  # )
            self.tokenizer.advance()
        else:
            raise ValueError(
                f"Unexpected token: {self.tokenizer.symbol()}")


