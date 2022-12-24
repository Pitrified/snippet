"""Match two sequences of words.

Some words might be different, and other might be missing.

We      We
have    have
a       a
list    lst
of      -
words   -
badly   badly
copied  -

We cheat with the alignment adding 
`perfectly` and `aligned`
at the beginning and end of the sequence.

Frankly there are a billion tools to do the diff of a document, so.
"""

from Levenshtein import ratio


def sample_Levenshtein() -> None:
    """Sample use of the Levenshtein library.

    https://maxbachmann.github.io/Levenshtein/levenshtein.html#ratio
    """
    print(f"{ratio('lewenstein', 'levenshtein')=}")
    # 0.85714285714285


def main() -> None:
    """Run the aligner."""


if __name__ == "__main__":
    sample_Levenshtein()
    main()
