from sys import argv
from re import findall, search, match
import argparse

MAX_POLYNOMIAL_DEGREE = 2
A = 0
B = 1
C = 2

DEBUG = False
TERM_VALIDATION_REGEX = r"\d*\.?\d*\s*\*?\s*(\w\s*(\^\s*\d+)?)?"


class Term:

    _coefficient = 1
    _variable_name = ""
    _power = 0

    def __init__(self, term_string, default=False):
        self._default = default
        self._term_string = str(term_string)
        search_result = search(r"^([\-\+]?)(\d*\.?\d*)((\w)(\^(\d+))?)?", self._term_string)
        if search_result.group(2) or search_result.group(1):
            self._coefficient = float(search_result.group(2) or 1) * float(search_result.group(1) + "1")
        if search_result.group(4):
            self._variable_name = search_result.group(4)
            self._power = 1
        if search_result.group(6):
            self._power = int(search_result.group(6))

    def is_like(self, term):
        return self._variable_name == term._variable_name \
               and self._power == term._power

    def get_coefficient(self):
        return self._coefficient

    def get_power(self):
        return self._power

    def get_variable_name(self):
        return self._variable_name

    def merge(self, term):
        if self.is_like(term):
            self._coefficient = self.get_coefficient() + term.get_coefficient()
            return True
        return False

    def change_sign(self):
        self._coefficient = -self._coefficient
        return self

    def __str__(self):
        if self._default:
            return ""
        result = ""
        if self._variable_name and self._power >= 2:
            result = f"{self._variable_name}^{self._power}"
        if self._variable_name and self._power == 1:
            result = str(self._variable_name)
        if not result or self._coefficient != 1:
            result = f"{str(abs(self._coefficient)).rstrip('0').rstrip('.')}" + result
        if result:
            result = ("+ " if self._coefficient > 0 else "- ") + result
        return result

    def __repr__(self):
        return "{}*{}^{}".format(
            ('%f' % self.get_coefficient()).rstrip('0').rstrip('.'),
            self._variable_name,
            self._power
        )

    def __eq__(self, other):
        return self._power == other._power

    def __lt__(self, other):
        return self._power < other._power


class Polynomial:

    def __init__(self, equation):
        self._terms = []
        equation = str(equation)
        self._check_equation(equation)
        equation = equation.replace(" ", "").replace("*", "")
        self._split_terms(equation)
        self._degree = None

    @staticmethod
    def _check_equation(equation):
        for expretion in equation.split("+"):
            for term_str in expretion.split("-"):
                term_str = term_str.strip()
                re_obj = match(TERM_VALIDATION_REGEX, term_str)
                if re_obj.group(0) != term_str:
                    raise ValueError(f"Not valid term: {term_str}")

    def _split_terms(self, equation):
        if DEBUG:
            print("Available string terms:")
            print("\t", findall(r"[\-\+]?[\d\w\.\^]+", equation))
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
            if term.get_coefficient():
                self._terms.append(term)
        if len(self._terms) < 1:
            raise ValueError("It's not a equation!")
        self._terms = sorted(self._terms)
        self._degree = self._terms[-1].get_power()

    def get_degree(self):
        return self._degree

    def __str__(self):
        if self._terms:
            return " ".join([str(term) for term in self._terms]).lstrip("+ ")
        else:
            return "0"

    def get_term_coeff(self, index):
        if len(self._terms) > index:
            return self._terms[::-1][index].get_coefficient()
        return 0

    def find_discriminant(self):
        return self.get_term_coeff(B) ** 2 - 4 * self.get_term_coeff(A) * self.get_term_coeff(C)

    def _run_formula(self, sign):
        a = self.get_term_coeff(A)
        b = self.get_term_coeff(B)
        c = self.get_term_coeff(C)
        if DEBUG:
            print(f"a = {a}")
            print(f"b = {b}")
            print(f"c = {c}")
        sqrt = lambda x: x**(1 / 2.0)

        if DEBUG:
            print("Running formula:")
            print("\t(-b + sqrt(b**2 - 4 * a * c)) / (2 * a)")
            print("\t(-{1} + sqrt({1}**2 - 4 * {0} * {2})) / (2 * {0})".format(a, b, c))
        if sign == "+":
            return (-b + sqrt(b**2 - 4 * a * c)) / (2 * a)
        else:
            return (-b - sqrt(b**2 - 4 * a * c)) / (2 * a)

    def _check_zero_degree(self):
        if self.get_term_coeff(0) == 0:
            print("Many solutions available.")
        else:
            print("No solution available.")
        return None

    def _check_one_degree(self):
        a = self.get_term_coeff(A)
        b = self.get_term_coeff(B) or 0
        if DEBUG:
            print(f"a = {a}")
            print(f"b = {b}")
            print("Run formula:")
            print("-b / a")
            print(f"-{b} / {a}")
        return -b / a

    def find_solution(self):
        degree = self.get_degree()
        print(f"Polynomial degree: {self.get_degree()}")
        if degree > MAX_POLYNOMIAL_DEGREE:
            print(f"The polynomial degree is strictly grader then "
                  f"{MAX_POLYNOMIAL_DEGREE}, I can't solve.")
        elif degree == 0:
            return self._check_zero_degree()
        elif degree == 1:
            return self._check_one_degree()
        elif degree == 2:
            discriminant = self.find_discriminant()
            print(f"Polynomial discriminant: {discriminant}")
            if discriminant > 0:
                return self._run_formula("-"), self._run_formula("+")
            elif discriminant == 0:
                return self._run_formula("+")
            else:
                return self._run_discriminant_formula(discriminant)
        return None

    def _run_discriminant_formula(self, discriminant):
        a = self.get_term_coeff(A)
        b = self.get_term_coeff(B)
        if DEBUG:
            print(f"a = {a}")
            print(f"b = {b}")

        (-b - (abs(discriminant) ** 0.5)) / (2 * a)
        if DEBUG:
            print("Running formula:")
            print("\t(-b +/- (abs(discriminant) ** 0.5)) / (2 * a)")
            print("\t(-{1} +/- (abs({2}) ** 0.5)) / (2 * {0})".format(a, b, discriminant))
        negative_result = (-b - (abs(discriminant) ** 0.5)) / (2 * a)
        positive_result = (-b + (abs(discriminant) ** 0.5)) / (2 * a)
        return f"{negative_result}i", f"{positive_result}i"


class PolynomialEquation:

    def __init__(self, equation_string):
        self._equation_string = str(equation_string)
        equations = self._equation_string.split("=")
        if len(equations) != 2:
            raise ValueError("It's not a equation!")
        self._left_polynomial = Polynomial(equations[0])
        self._right_polynomial = Polynomial(equations[1])

    def simplify(self):
        self._move_all_terms_to_left()
        self._left_polynomial.simplify()

    def _move_all_terms_to_left(self):
        if not self._right_polynomial._terms:
            raise ValueError("This expression isn't equation")
        for term in self._right_polynomial._terms:
            self._left_polynomial._terms.append(term.change_sign())
        self._right_polynomial._terms = []
        variables = {term.get_variable_name() for term in self._left_polynomial._terms if term.get_variable_name()}
        if len(variables) > 1:
            raise ValueError(f"Unexpected variables: {', '.join(list(variables)[1:])}")

    def get_degree(self):
        return self._left_polynomial.get_degree()

    def __str__(self):
        return f"{self._left_polynomial} = {self._right_polynomial}"

    def find_solution(self):
        return self._left_polynomial.find_solution()


def run_computor(input_equation):
    print("Input equation:", input_equation)
    try:
        polynomial_equation = PolynomialEquation(input_equation)
        polynomial_equation.simplify()
        print(f"Reduced form: {polynomial_equation}")
        solution = polynomial_equation.find_solution()
        if solution is not None:
            print("The solution is:")
            if isinstance(solution, float):
                print(solution)
            elif len(solution) == 2:
                print("Discriminant is strictly positive, the two solutions are:")
                print(solution[0])
                print(solution[1])
            return solution
    except ValueError as error:
        print(f"Error: {error}")


def test_computor():
    failed = 0

    test_input = {
        "5 * X^0 + 4 * X^1 = 4 * X^0": -0.25,
        "5 * X^0 + 4 * X^1 - 9.3 * X^2 = 1 * X^0": (0.9052389907905898, -0.47513146390886934),
        "2x - 4 = 0": 2,
        "2x^2 - 18 =0": (0.0, 9.0),
        "0 = 0": None,
        "x=0": 0,
        "5 + 3X + 3 * X^2 = X^2 + 0 * X": ("-2.1419410907075056i", "0.6419410907075054i"),
        "4 * X^0 + 4 * X^1 - 9.3 * X^2 = 0": (0.9052389907905898, -0.47513146390886934),
        "1 * X^0 + 4 * X^1 = 0": -0.25,
        "1 + 4 * X = 0": -0.25,
        "8 * X^0 - 6 * X^1 + 0 * X^2 - 5.6 * X^3 = 3 * X^0": None,
        "5 * X^0 - 6 * X^1 + 0 * X^2 - 5.6 * X^3 = 0": None,
        "5 + 4 * X + X^2= X^2": -1.25,
        "0": None,
        "=": None,
        "X + X + 1 + X^2 = 0": -1.0,
        "X + X *+ 1/X^2 = 0": None,
        "X + X + 1X^2 =": None,
        "X = X = X": None,
        "x = y": None,
        "1x = 0": 0,
        "x = y = z = ": None,
        "x - y = z": None,
        "2x^2 - 3x + 4  =   0": ("-0.4489578808281798i", "1.9489578808281798i"),
        "x^23 + 3 = 0": None,
    }
    for input_equation, expected_result in test_input.items():
        print("##############start test################")
        print(f"Input: {input_equation}")
        result = run_computor(input_equation)
        if result == expected_result:
            print("\033[32mOK\033[39m")
        else:
            failed += 1
            print("\033[31mKO\033[39m")
            print(f"\033[31mresult={result}, expected={expected_result}\033[39m")

        print("################end test################\n")
    print(f"Run {len(test_input)} tests {failed} failed.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="The program that solves a polynomial equation of degree less than or equal to 2"
    )
    parser.add_argument("equation", metavar="equation", type=str,
                        help="Polynomial equation that must be solved", nargs=1)
    parser.add_argument("-d", metavar="debug", action='store_const', const=True, default=False,
                        help="Turns on debug mode")
    args = parser.parse_args()
    if args.d:
        DEBUG = True
    if args.equation[0] == "RUN_TEST":
        test_computor()
    else:
        run_computor(args.equation[0])
