"""Try this wonky inheritance."""

from loguru import logger as lg

from typing import Type


class SentenceBase:
    """Basic sentence."""

    def __init__(
        self,
        text: str,
    ) -> None:
        """Initialize a basic sentence."""
        lg.debug("Start init SentenceBase.  Actual class {}", self.__class__.__name__)
        self.text = text

    def __str__(self) -> str:
        """Str representation of the sentence."""
        return self.text

    def __repr__(self) -> str:
        """Detailed representation of the sentence."""
        return self.__str__()


class SentenceSpace(SentenceBase):
    """Fancier sentence, counts the space in the text."""

    def __init__(
        self,
        text: str,
    ) -> None:
        """Initialize a fancy sentence."""
        lg.debug("Start init SentenceSpace. Actual class {}", self.__class__.__name__)
        super().__init__(text)

        self.spaces = text.count(" ")

    def __repr__(self) -> str:
        """Detailed representation of the sentence."""
        return self.text + f" ({self.spaces})"


class ParagraphBase:
    """Basic paragraph."""

    def __init__(
        self,
        par_text: list[str],
        sentence_type: Type[SentenceBase] = SentenceBase,
    ) -> None:
        """Initialize a basic paragraph.

        Here we only allow ``SentenceBase`` as ``sentence_type``.
        Using ``self.sentence.spaces`` inside a ``ParagraphBase`` is an error.
        """
        lg.debug("Start init ParagraphBase.  Actual class {}", self.__class__.__name__)
        self.sentence_type = sentence_type
        self.sentence = [self.sentence_type(sen_text) for sen_text in par_text]


class ParagraphSpace(ParagraphBase):
    """Fancier paragraph."""

    def __init__(
        self,
        text: list[str],
    ) -> None:
        """Initialize a fancy paragraph.

        We create sentences of the right type when creating the ``ParagraphBase``,
        which is ok because ``SentenceSpace`` inherits from ``SentenceBase``.
        Then we override the type of ``self.sentence``,
        so that ``self.sentence.spaces`` type checks.
        """
        lg.debug("Start init ParagraphSpace. Actual class {}", self.__class__.__name__)
        super().__init__(
            text,
            SentenceSpace,
        )
        self.sentence: list[SentenceSpace]


def main():
    """Try this wonky inheritance."""
    par_text = [
        "this sentence has four spaces",
        "a longer sentences has more spaces",
    ]
    pb = ParagraphBase(par_text)
    lg.info(f"{pb.sentence}")
    lg.info(f"{type(pb.sentence[0])}")
    # lg.info("f{pb.sentence[0].spaces}") # fails, obviously

    pf = ParagraphSpace(par_text)
    lg.info(f"{pf.sentence!r}")
    lg.info(f"{type(pf.sentence[0])}")
    lg.info(f"{pf.sentence[0].spaces}")


if __name__ == "__main__":
    main()
