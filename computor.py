from sys import argv
from re import findall, search
from pprint import pprint

ADDITION = "+"
SUBTRACTION = "-"


def usage(error=None):
    if error:
        print("Error: " + error)
    print('Usage:\npython computor.py "<equation>"')


class Term:

    _coefficient = 1

    def __init__(self, term_string):
        if term_string.startswith("-"):
            self._term_string = term_string.replace(SUBTRACTION, "")
            self._positive = False
        else:
            self._positive = True
            self._term_string = term_string.replace(ADDITION, "")
        search_result = search(r"^\-?(\d*\.?\d*)((\w)(\^(\d))?)?", self._term_string)
        if search_result.group(1):
            self._coefficient = search_result.group(1)
        if search_result.group(3):
            self._variable_name = search_result.group(3)
        if search_result.group(5):
            self._power = search_result.group(5)
        print(self)
        pprint(self.__dict__)

    def change_sign(self):
        self._positive = not self._positive
        return self

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return ("+" if self._positive else "-") + self._term_string


class Polynomial:

    def __init__(self, equation):
        equation = str(equation)
        equation = equation.replace(" ", "").replace("*", "")
        self._split_terms(equation)

    # def __split_get_negative_terms(self):

    def _split_terms(self, equation):
        self._terms = \
            [Term(term_str)
             for term_str in findall(r"[\-\+]?[\d\w\.\^]+", equation)]

    def __str__(self):
        if self._terms:
            return " ".join([str(term) for term in self._terms])
        else:
            return "0"


class PolynomialEquation:

    def __init__(self, equation_string):
        self._equation_string = str(equation_string)
        equations = self._equation_string.split("=")
        if len(equations) != 2:
            raise ValueError
        self._left_polynomial = Polynomial(equations[0])
        self._right_polynomial = Polynomial(equations[1])

    def simplify(self):
        self._move_all_terms_to_left()

    def _move_all_terms_to_left(self):
        for term in self._right_polynomial._terms:
            self._left_polynomial._terms.append(term.change_sign())
        self._right_polynomial._terms = []

    def __str__(self):
        return f"{self._left_polynomial} = {self._right_polynomial}"


if __name__ == '__main__':
    if len(argv) != 2:
        usage("Invalid number of arguments.")
    polynomial_equation = PolynomialEquation(argv[1])
    polynomial_equation.simplify()
    print(polynomial_equation)


