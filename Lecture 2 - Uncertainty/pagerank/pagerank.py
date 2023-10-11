import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(link for link in pages[filename] if link in pages)

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    # Initialise probability distribution dictionary:
    prob = {page: 0 for page in corpus}

    # If page has no links, return equal probability for the corpus:
    if len(corpus[page]) == 0:
        for page in prob:
            prob[page] = 1 / len(corpus)
        return prob

    # Probability of picking any page at random:
    random = (1 - damping_factor) / len(corpus)

    # Probability of picking a link from the page:
    link = damping_factor / len(corpus[page])

    # Add probabilities to the distribution:
    for page in prob:
        prob[page] += random

        if page in corpus[page]:
            prob[page] += link

    return prob


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    # first, not choose any page
    estimatedPageRank = {}
    pages = list(corpus.keys())

    firstChoose = random.choice(pages)
    for page in pages:
        estimatedPageRank[page] = 0

    estimatedPageRank[firstChoose] = 1 / n

    currentModel = transition_model(corpus, firstChoose, damping_factor)
    for i in range(1, n):
        # choose one page
        currentChoose = random.choices(
            list(currentModel.keys()), list(currentModel.values()), k=1
        )[0]

        estimatedPageRank[currentChoose] = estimatedPageRank[currentChoose] + 1 / n
        # next
        currentModel = transition_model(corpus, firstChoose, damping_factor)

    return estimatedPageRank


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    currentRanks = {}
    for page in corpus:
        currentRanks[page] = 1 / len(corpus)
    while True:
        newRanks = {}
        for page in currentRanks:
            newRanks[page] = (1 - damping_factor) / len(currentRanks)
            # links of page
            sigma = 0
            for link in list(corpus[page]):
                # alway add to 1 because link could be empty
                sigma += currentRanks[link] / (len(corpus[link]) + 1)
            # include itself
            # alway add to 1 because page could be empty
            sigma += currentRanks[page] / (len(corpus[page]) + 1)

            newRanks[page] += damping_factor * sigma

        countChangesMore = 0
        for page in newRanks:
            if abs(newRanks[page] - currentRanks[page]) <= 0.001:
                countChangesMore += 1
        currentRanks = newRanks
        if countChangesMore == len(currentRanks):
            break
    return currentRanks


if __name__ == "__main__":
    main()
