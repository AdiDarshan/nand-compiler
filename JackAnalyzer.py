"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import os
import sys
import typing
from CompilationEngine import CompilationEngine
from JackTokenizer import JackTokenizer


def write_tokens(token_type, tokenizer, file):
    if token_type == "KEYWORD":
        file.write(f"<keyword> {tokenizer.keyword()} </keyword>\n")
    elif token_type == "SYMBOL":
        file.write(f"<symbol> {tokenizer.symbol()} </symbol>\n")
    elif token_type == "IDENTIFIER":
        file.write(f"<identifier> {tokenizer.identifier()} </identifier>\n")
    elif token_type == "INT_CONST":
        file.write(
            f"<integerConstant> {tokenizer.int_val()} </integerConstant>\n")
    elif token_type == "STRING_CONST":
        file.write(
            f"<stringConstant> {tokenizer.string_val()} </stringConstant>\n")
    else:
        raise ValueError(f"Unsupported token type: {token_type}")


def analyze_file(
        input_file: typing.TextIO, output_file: typing.TextIO) -> None:
    """Analyzes a single file.

    Args:
        input_file (typing.TextIO): the file to analyze.
        output_file (typing.TextIO): writes all output to this file.
    """
    tokenizer = JackTokenizer(input_file)
    engine = CompilationEngine(tokenizer, output_file)
    engine.compile_class()
    # output_file.write('<tokens>\n')
    # while tokenizer.has_more_tokens():
    #     tokenizer.advance()
    #     token_type = tokenizer.token_type()
    #     write_tokens(token_type, tokenizer, output_file)
    # output_file.write('</tokens>\n')




if "__main__" == __name__:
    # Parses the input path and calls analyze_file on each input file.
    # This opens both the input and the output files!
    # Both are closed automatically when the code finishes running.
    # If the output file does not exist, it is created automatically in the
    # correct path, using the correct filename.
    if not len(sys.argv) == 2:
        sys.exit("Invalid usage, please use: JackAnalyzer <input path>")
    argument_path = os.path.abspath(sys.argv[1])
    if os.path.isdir(argument_path):
        files_to_assemble = [
            os.path.join(argument_path, filename)
            for filename in os.listdir(argument_path)]
    else:
        files_to_assemble = [argument_path]
    for input_path in files_to_assemble:
        filename, extension = os.path.splitext(input_path)
        if extension.lower() != ".jack":
            continue
        output_path = filename + "Q.xml"
        with open(input_path, 'r') as input_file, \
                open(output_path, 'w') as output_file:
            analyze_file(input_file, output_file)
