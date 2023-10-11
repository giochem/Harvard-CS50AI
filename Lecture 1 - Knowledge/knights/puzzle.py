from logic import *

AKnight = Symbol("A is a Knight")
AKnave = Symbol("A is a Knave")

BKnight = Symbol("B is a Knight")
BKnave = Symbol("B is a Knave")

CKnight = Symbol("C is a Knight")
CKnave = Symbol("C is a Knave")

knowledgeGeneral = And(
    Or(AKnight, AKnave),
    Not(And(AKnave, AKnight)),
    Or(BKnight, BKnave),
    Not(And(BKnave, BKnight)),
    Or(CKnight, CKnave),
    Not(And(CKnave, CKnight)),
)
# Puzzle 0
# A says "I am both a knight and a knave."
knowledge0 = And(
    knowledgeGeneral,
    # A is Knight -> true
    Implication(AKnight, And(AKnight, AKnave)),
    # A is Knave -> false
    Implication(AKnave, Not(And(AKnight, AKnave))),
)

# Puzzle 1
# A says "We are both knaves."
# B says nothing.
knowledge1 = And(
    knowledgeGeneral,
    # A is Knight -> true
    Implication(AKnight, And(AKnave, BKnave)),
    # A is Knave -> false
    Implication(AKnave, Not(And(AKnave, BKnave))),
)

# Puzzle 2
# A says "We are the same kind."
# B says "We are of different kinds."
knowledge2 = And(
    knowledgeGeneral,
    # A is Knight -> true
    Implication(
        AKnight,
        And(
            Or(And(AKnight, BKnight), And(AKnave, BKnave)),
            Not(And(And(AKnight, BKnight), And(AKnave, BKnave))),
        ),
    ),
    # A is Knave -> false
    Implication(
        AKnave,
        Not(
            And(
                Or(And(AKnight, BKnight), And(AKnave, BKnave)),
                Not(And(And(AKnight, BKnight), And(AKnave, BKnave))),
            )
        ),
    ),
    # B is Knight -> True
    Implication(
        BKnight,
        And(
            Or(And(AKnight, BKnave), And(AKnave, BKnight)),
            Not(And(And(AKnight, BKnave), And(AKnave, BKnight))),
        ),
    ),
    # B is Knave -> False
    Implication(
        BKnave,
        Not(
            And(
                Or(And(AKnight, BKnave), And(AKnave, BKnight)),
                Not(And(And(AKnight, BKnave), And(AKnave, BKnight))),
            )
        ),
    ),
)

# Puzzle 3
# A says either "I am a knight." or "I am a knave.", but you don't know which.
# B says "A said 'I am a knave'."
# B says "C is a knave."
# C says "A is a knight."
knowledge3 = And(
    knowledgeGeneral,
    # A is Knight -> True
    Implication(AKnight, Or(AKnight, AKnave)),
    # A is Knave -> False
    Implication(AKnave, Not(Or(AKnight, AKnave))),
    # B is Knight -> True
    Implication(
        BKnight, And(Implication(AKnight, AKnave), Implication(AKnave, Not(AKnave)))
    ),
    Implication(BKnight, CKnave),
    # B is Knave -> False
    Implication(
        BKnave, Not(And(Implication(AKnight, AKnave), Implication(AKnave, Not(AKnave))))
    ),
    Implication(BKnave, Not(CKnave)),
    # C is Knight -> True
    Implication(
        CKnight, And(Implication(AKnight, AKnight), Implication(AKnave, Not(AKnight)))
    ),
    # C is Knave -> False
    Implication(
        CKnave,
        Not(And(Implication(AKnight, AKnight), Implication(AKnave, Not(AKnight)))),
    ),
)
"""
ANSWER
Puzzle 0
A is a Knave
Puzzle 1
A is a Knave
B is a Knight
Puzzle 2
A is a Knave
B is a Knight
Puzzle 3
A is a Knight
B is a Knave
C is a Knight
"""

def main():
    symbols = [AKnight, AKnave, BKnight, BKnave, CKnight, CKnave]
    puzzles = [
        ("Puzzle 0", knowledge0),
        ("Puzzle 1", knowledge1),
        ("Puzzle 2", knowledge2),
        ("Puzzle 3", knowledge3),
    ]
    for puzzle, knowledge in puzzles:
        print(puzzle)
        if len(knowledge.conjuncts) == 0:
            print("    Not yet implemented.")
        else:
            for symbol in symbols:
                if model_check(knowledge, symbol):
                    print(f"    {symbol}")


if __name__ == "__main__":
    main()
