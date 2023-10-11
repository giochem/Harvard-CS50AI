import csv
import itertools
import sys

PROBS = {
    # Unconditional probabilities for having gene
    "gene": {2: 0.01, 1: 0.03, 0: 0.96},
    "trait": {
        # Probability of trait given two copies of gene
        2: {True: 0.65, False: 0.35},
        # Probability of trait given one copy of gene
        1: {True: 0.56, False: 0.44},
        # Probability of trait given no gene
        0: {True: 0.01, False: 0.99},
    },
    # Mutation probability
    "mutation": 0.01,
}


def main():
    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {"gene": {2: 0, 1: 0, 0: 0}, "trait": {True: 0, False: 0}}
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):
        # Check if current set of people violates known information
        fails_evidence = any(
            (
                people[person]["trait"] is not None
                and people[person]["trait"] != (person in have_trait)
            )
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):
                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (
                    True
                    if row["trait"] == "1"
                    else False
                    if row["trait"] == "0"
                    else None
                ),
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s)
        for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """
    entire_joint_probability = 1
    for person in people:
        name_mother = people[person]["mother"]
        name_father = people[person]["father"]
        # calculator probability each person
        gene = 0
        trait = 0

        # index gene
        # default is 0 copies
        index_gene = 1 if person in one_gene else 2 if person in two_genes else 0
        # parent
        if name_mother == name_father == None:
            # result each person
            gene = PROBS["gene"][index_gene]
        else:
            # gene mother, father
            gene_mother = (
                1 if name_mother in one_gene else 2 if name_mother in two_genes else 0
            )
            gene_father = (
                1 if name_father in one_gene else 2 if name_father in two_genes else 0
            )

            # probability mutation of mother, father
            mother = (
                PROBS["mutation"]
                if gene_mother == 0
                else 0.5
                if gene_mother == 1
                else (1 - PROBS["mutation"])
            )
            father = (
                PROBS["mutation"]
                if gene_father == 0
                else 0.5
                if gene_father == 1
                else (1 - PROBS["mutation"])
            )

            if index_gene == 2:
                # 2 copies
                gene = mother * father
            elif index_gene == 1:
                # 1 copies
                gene = mother * (1 - father) + father * (1 - mother)
            else:
                # 0 copy
                gene = (1 - mother) * (1 - father)

        # trait
        is_trait = (
            True if people[person]["trait"] == True or person in have_trait else False
        )
        trait = PROBS["trait"][index_gene][is_trait]

        entire_joint_probability *= gene * trait

    return entire_joint_probability


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    # for each person
    for person in probabilities:
        # find number copies and check trait
        index_gene = 1 if person in one_gene else 2 if person in two_genes else 0
        is_trait = True if person in have_trait else False

        # add p to each atribution
        probabilities[person]["gene"][index_gene] += p
        probabilities[person]["trait"][is_trait] += p


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    # for each person
    for person in probabilities:
        gene_0 = probabilities[person]["gene"][0]
        gene_1 = probabilities[person]["gene"][1]
        gene_2 = probabilities[person]["gene"][2]

        trait_true = probabilities[person]["trait"][True]
        trait_false = probabilities[person]["trait"][False]
        # sum distribution
        sum_distribution_gene = gene_0 + gene_1 + gene_2

        sum_distribution_trait = trait_true + trait_false
        # -> divide
        update_gene_0 = gene_0 / sum_distribution_gene
        update_gene_1 = gene_1 / sum_distribution_gene
        update_gene_2 = gene_2 / sum_distribution_gene

        update_trait_true = trait_true / sum_distribution_trait
        update_trait_false = trait_false / sum_distribution_trait

        # update gene
        probabilities[person]["gene"][0] = update_gene_0
        probabilities[person]["gene"][1] = update_gene_1
        probabilities[person]["gene"][2] = update_gene_2
        # update trait
        probabilities[person]["trait"][True] = update_trait_true
        probabilities[person]["trait"][False] = update_trait_false


if __name__ == "__main__":
    main()
