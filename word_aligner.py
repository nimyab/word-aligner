from dataclasses import dataclass
from simalign import SentenceAligner
from typing import List, Dict, Any, Tuple
import re

all_matching_methods = {
    "a": "inter",
    "m": "mwmf",
    "i": "itermax",
    "f": "fwd",
    "r": "rev",
}


@dataclass
class AlignmentResult:
    src_word: str
    target_word: str
    src_indexes: Tuple[int, int]
    target_indexes: Tuple[int, int]


class WordAligner:
    def __init__(self, matching_method: str = "m"):
        """
        Initialize the WordAligner class.
        """
        self.__aligner = SentenceAligner(
            model="bert", token_type="bpe", matching_methods=matching_method
        )
        self.__method = all_matching_methods[matching_method]

    def __tokenize(self, text: str) -> List[Tuple[str, int, int]]:
        """
        Tokenize text and return a list of (word, start, end)
        """
        # return [
        #     (m.group(), m.start(), m.end())
        #     for m in re.finditer(r"\b\w+(?:[.'’]\w+)*\b([.,])*", text)
        # ]
        return [
            (m.group(), m.start(), m.end())
            for m in re.finditer(r'\S+', text)
        ]

    def get_word_alignment(
        self,
        src_text: str,
        target_text: str,
    ) -> List[Dict[str, Any]]:
        """
        Create an array of word alignments between source and target text.

        Args:
            src_text (str): Source text
            target_text (str): Target text

        Returns:
            List[Dict[str, Any]]: Array of objects with word alignments
        """

        src_text_tokenize = self.__tokenize(src_text)
        src_text_split = [word for word, _, _ in src_text_tokenize]
        target_text_tokenize = self.__tokenize(target_text)
        target_text_split = [word for word, _, _ in target_text_tokenize]
        if len(src_text_split) == 0 or len(target_text_split) == 0:
            raise ValueError("Source or target text is empty")
        alignments = self.__aligner.get_word_aligns(src_text_split, target_text_split)

        for method, pairs in alignments.items():
            if method != self.__method:
                continue
            method_alignments: List[AlignmentResult] = []
            for src_idx, target_idx in pairs:
                src_word = src_text_tokenize[src_idx]
                target_word = target_text_tokenize[target_idx]

                method_alignments.append(
                    AlignmentResult(
                        src_word=src_word[0],
                        target_word=target_word[0],
                        src_indexes=src_word[1:],
                        target_indexes=target_word[1:],
                    )
                )

            return method_alignments

        return []
