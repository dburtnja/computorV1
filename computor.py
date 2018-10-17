from sys import argv
from re import findall, search
from pprint import pprint

MAX_POLYNOMIAL_DEGREE = 2

def usage(error=None):
    if error:
        print("Error: " + error)
    print('Usage:\npython computor.py "<equation>"')


class Term:

    _coefficient = 1

    def __init__(self, term_string):
        self._term_string = str(term_string)
        search_result = search(r"^([\-\+]?\d*\.?\d*)((\w)(\^(\d))?)?", self._term_string)
        if search_result.group(1):
            self._coefficient = float(search_result.group(1))
        if search_result.group(3):
            self._variable_name = search_result.group(3)
        if search_result.group(5):
            self._power = int(search_result.group(5))

    def is_like(self, term):
        return self._variable_name == term._variable_name \
               and self._power == term._power

    def get_coefficient(self):
        return self._coefficient

    def get_power(self):
        return self._power

    def merge(self, term):
        if self.is_like(term):
            self._coefficient = self.get_coefficient() + term.get_coefficient()
            return True
        return False

    def change_sign(self):
        self._coefficient = -self._coefficient
        return self

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return \
            f"{('%f' % self.get_coefficient()).rstrip('0').rstrip('.')}*{self._variable_name}^{self._power}"

    def __eq__(self, other):
        return self._power == other._power

    def __lt__(self, other):
        return self._power < other._power


class Polynomial:

    def __init__(self, equation):
        self._terms = []
        equation = str(equation)
        equation = equation.replace(" ", "").replace("*", "")
        self._split_terms(equation)
        self._degree = None

    def _split_terms(self, equation):
        self._terms = \
            [Term(term_str)
             for term_str in findall(r"[\-\+]?[\d\w\.\^]+", equation)]

    def simplify(self):
        terms_start = list(self._terms)
        temporary_terms = []
        self._terms = []

        while terms_start:
            term = terms_start.pop(0)
            for other_term in terms_start:
                successfully_merged = term.merge(other_term)
                if not successfully_merged:
                    temporary_terms.append(other_term)
            terms_start = temporary_terms
            temporary_terms = []
            self._terms.append(term)
        self._terms = sorted(self._terms)
        self._degree = self._terms[-1].get_power()

    def get_degree(self):
        return self._degree

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
        self._left_polynomial.simplify()

    def _move_all_terms_to_left(self):
        for term in self._right_polynomial._terms:
            self._left_polynomial._terms.append(term.change_sign())
        self._right_polynomial._terms = []

    def get_degree(self):
        return self._left_polynomial.get_degree()

    def __str__(self):
        return f"{self._left_polynomial} = {self._right_polynomial}"


if __name__ == '__main__':
    if len(argv) != 2:
        usage("Invalid number of arguments.")
    polynomial_equation = PolynomialEquation(argv[1])
    # print(polynomial_equation)
    polynomial_equation.simplify()
    print(f"Reduced form: {polynomial_equation}")
    print(f"Polynomial degree: {polynomial_equation.get_degree()}")
    if polynomial_equation.get_degree() > MAX_POLYNOMIAL_DEGREE:
        print(f"The polynomial degree is strictly grader then "
              f"{MAX_POLYNOMIAL_DEGREE}, I can't solve.")


