import sys

from crossword import *
from copy import deepcopy


class CrosswordCreator:
    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy() for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont

        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size, self.crossword.height * cell_size),
            "black",
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                rect = [
                    (j * cell_size + cell_border, i * cell_size + cell_border),
                    (
                        (j + 1) * cell_size - cell_border,
                        (i + 1) * cell_size - cell_border,
                    ),
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (
                                rect[0][0] + ((interior_size - w) / 2),
                                rect[0][1] + ((interior_size - h) / 2) - 10,
                            ),
                            letters[i][j],
                            fill="black",
                            font=font,
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for var in self.domains:
            len_consisten_var = var.length
            for word in self.domains[var].copy():
                if len(word) != len_consisten_var:
                    self.domains[var].remove(word)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        made_revision = False
        for var_x in self.domains[x].copy():
            is_consistent = False
            for var_y in self.domains[y]:
                #  consistent
                if self.crossword.overlaps[x, y] == None:
                    is_consistent = True
                else:
                    x_i, y_i = self.crossword.overlaps[x, y]
                    # word index same value
                    if var_x[x_i] == var_y[y_i]:
                        is_consistent = True
            # remove if not consistent
            if is_consistent == False:
                self.domains[x].remove(var_x)
                # revision
                made_revision = True

        return made_revision

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if arcs == None:
            arcs = []
            for var_1 in self.domains:
                for var_2 in self.domains:
                    if var_1 != var_2:
                        arcs.append((var_1, var_2))
        while len(arcs) > 0:
            # variables x, y
            x, y = arcs.pop()
            if self.revise(x, y):
                # words in var x
                if len(self.domains[x]) == 0:
                    return False
                # neighbors_var_x - var_y
                for z in self.crossword.neighbors(x) - {y}:
                    arcs.append((z, x))
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        return len(self.crossword.variables) == len(assignment)

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        for x, y in self.crossword.overlaps:
            # x, y in assignment and check not same value
            if x in assignment and y in assignment and assignment[x] == assignment[y]:
                return False
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        # default not remove any word for neighbor unassigned variables.
        words = {}
        for word in self.domains[var]:
            ruled_out = 0
            for neighbor in self.crossword.neighbors(var):
                # unassigned variables
                # check in words for neighbor
                if neighbor not in assignment and word in self.domains[neighbor]:
                    ruled_out += 1
            words[word] = ruled_out
        # sort to ruled_out
        dict(sorted(words.items(), key=lambda item: item[1]))
        return words.keys()

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        vars = []
        fewest_remain = float("inf")
        # add all vars have fewest remain
        for var in self.crossword.variables:
            #  not yet assigned
            if var not in assignment:
                len_words = len(self.domains[var])
                if len_words == fewest_remain:
                    # add to vars
                    vars.append(var)
                elif len_words < fewest_remain:
                    # if values < femest_remain
                    # update new selects
                    fewest_remain = len_words
                    vars = [var]
        # if have only one value -> select
        if len(vars) == 1:
            return vars[0]
        # if have many vars -> choose among has the most neighbors
        most_neighbors = 0
        vars_most_neighbors = []
        for var in vars:
            len_neighbors = len(self.crossword.neighbors(var))
            if len_neighbors == most_neighbors:
                vars_most_neighbors.append(var)
            elif len_neighbors > most_neighbors:
                most_neighbors = len_neighbors
                vars_most_neighbors = [var]
        # select one
        return vars_most_neighbors[0]

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment
        var = self.select_unassigned_variable(assignment)
        # domains backup if fail
        backup_assignment_domains = deepcopy(self.domains)
        for value in self.order_domain_values(var, assignment):
            assignment[var] = value
            if self.consistent(assignment):
                # set value to domains
                self.domains[var] = {value}
                # update all domains[var] -> remove word
                self.ac3(
                    [
                        (other_var, var)
                        for other_var in self.crossword.variables
                        if other_var != var
                    ]
                )

                result = self.backtrack(assignment)
                if result != False:
                    return result
            assignment.pop(var)
            # back up now domains before
            self.domains = backup_assignment_domains
        return None


def main():
    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()
    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
