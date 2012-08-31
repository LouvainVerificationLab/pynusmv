"""
Provide functions to parse strings and return corresponding ASTs.
"""

from ..utils.exception import NuSMVParsingError, Error

from ..nusmv.parser import parser as nsparser
from ..nusmv.node import node as nsnode

def parse_simple_expression(expression):
    """
    Parse a simple expression.
    
    Throw a NuSMVParsingException if a parsing error occurs.
    """
    node, err = nsparser.ReadSimpExprFromString(expression)
    if err:
        errlist = []
        errors = nsparser.Parser_get_syntax_errors_list()
        while errors is not None:
            error = nsnode.car(errors)
            err = nsparser.Parser_get_syntax_error(error)
            errlist.append(Error(*err[1:]))
            errors = nsnode.cdr(errors)
        raise NuSMVParsingError(tuple(errlist))
    else:
        return nsnode.car(node) # Get rid of the top SIMPWFF node
        
        
def parse_next_expression(expression):
    """
    Parse a next expression.
    
    Throw a NUSMVParsingException if a parsing error occurs.
    """
    node, err = nsparser.ReadNextExprFromString(expression)
    if err:
        errlist = []
        errors = nsparser.Parser_get_syntax_errors_list()
        while errors is not None:
            error = nsnode.car(errors)
            err = nsparser.Parser_get_syntax_error(error)
            errlist.append(Error(*err[1:]))
            errors = nsnode.cdr(errors)
        raise NuSMVParsingError(tuple(errlist))
    else:
        return nsnode.car(node) # Get rid of the top NEXTWFF node
        
        
def parse_identifier(expression):
    """
    Parse an identifier.
    
    Throw a NUSMVParsingException if a parsing error occurs.
    """
    node, err = nsparser.ReadIdentifierExprFromString(expression)
    if err:
        errlist = []
        errors = nsparser.Parser_get_syntax_errors_list()
        while errors is not None:
            error = nsnode.car(errors)
            err = nsparser.Parser_get_syntax_error(error)
            errlist.append(Error(*err[1:]))
            errors = nsnode.cdr(errors)
        raise NuSMVParsingError(tuple(errlist))
    else:
        return nsnode.car(node) # Get rid of the top COMPID node