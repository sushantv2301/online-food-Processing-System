"""Natural Language Processing (NLP) text preprocessing module.

This module provides text normalization, tokenization, stopword removal,
stemming, and feature soup construction for the movie recommendation system.
"""

from __future__ import annotations

import re
from typing import Iterable, List, Set


# Standard English stopwords commonly removed in Information Retrieval (IR) and NLP
STOPWORDS: Set[str] = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
    "below", "between", "both", "but", "by", "can", "can't", "cannot", "could",
    "couldn't", "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down",
    "during", "each", "few", "for", "from", "further", "had", "hadn't", "has",
    "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her",
    "here", "here's", "hers", "herself", "him", "himself", "his", "how", "how's",
    "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it",
    "it's", "its", "itself", "let's", "me", "more", "most", "mustn't", "my",
    "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or",
    "other", "ought", "our", "ours", "ourselves", "out", "over", "own", "same",
    "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't", "so",
    "some", "such", "than", "that", "that's", "the", "their", "theirs", "them",
    "themselves", "then", "there", "there's", "these", "they", "they'd", "they'll",
    "they're", "they've", "this", "those", "through", "to", "too", "under",
    "until", "up", "very", "was", "wasn't", "we", "we'd", "we'll", "we're",
    "we've", "were", "weren't", "what", "what's", "when", "when's", "where",
    "where's", "which", "while", "who", "who's", "whom", "why", "why's", "with",
    "won't", "would", "wouldn't", "you", "you'd", "you'll", "you're", "you've",
    "your", "yours", "yourself", "yourselves"
}


def clean_text(text: str) -> str:
    """Lowercase text, remove URLs, special characters, and normalize spaces."""
    if not isinstance(text, str):
        return ""
    text = text.lower()
    # Remove URLs
    text = re.sub(r"https?://\S+|www\.\S+", " ", text)
    # Remove HTML tags
    text = re.sub(r"<.*?>", " ", text)
    # Replace non-alphanumeric (except underscores for merged entities) with spaces
    text = re.sub(r"[^a-zA-Z0-9_\s]", " ", text)
    # Collapse multiple whitespaces
    text = re.sub(r"\s+", " ", text).strip()
    return text


def tokenize(text: str) -> List[str]:
    """Split text into individual word tokens."""
    cleaned = clean_text(text)
    return [token for token in cleaned.split() if len(token) > 1]


def remove_stopwords(tokens: Iterable[str], extra_stopwords: Set[str] | None = None) -> List[str]:
    """Filter out stopwords from a list of tokens."""
    stop_set = STOPWORDS if extra_stopwords is None else STOPWORDS.union(extra_stopwords)
    return [t for t in tokens if t not in stop_set]


def simple_stem(word: str) -> str:
    """Lightweight rule-based stemmer for common English suffixes.

    Reduces inflected words (e.g., 'mysteries' -> 'mysteri', 'exploring' -> 'explor').
    """
    if len(word) <= 3:
        return word

    # Common suffix replacements
    if word.endswith("ies") and len(word) > 4:
        return word[:-3] + "i"
    if word.endswith("sses"):
        return word[:-2]
    if word.endswith("ing") and len(word) > 5:
        return word[:-3]
    if word.endswith("ed") and len(word) > 4:
        return word[:-2]
    if word.endswith("ly") and len(word) > 4:
        return word[:-2]
    if word.endswith("ment") and len(word) > 6:
        return word[:-4]
    if word.endswith("ness") and len(word) > 6:
        return word[:-4]
    if word.endswith("s") and not word.endswith("ss") and len(word) > 3:
        return word[:-1]

    return word


def preprocess_nlp(text: str, stem: bool = True) -> str:
    """Full NLP pipeline: clean -> tokenize -> remove stopwords -> stem -> join."""
    tokens = tokenize(text)
    filtered = remove_stopwords(tokens)
    if stem:
        filtered = [simple_stem(w) for w in filtered]
    return " ".join(filtered)


def normalize_entity_name(name: str) -> str:
    """Collapse names into single connected tokens.

    Example:
        'Christopher Nolan' -> 'christopher_nolan'
        'Leonardo DiCaprio' -> 'leonardo_dicaprio'
    This prevents 'Christopher' from matching unrelated 'Christopher' entries.
    """
    if not isinstance(name, str):
        return ""
    cleaned = re.sub(r"[^a-zA-Z0-9\s]", "", name).strip().lower()
    return "_".join(cleaned.split())


def create_metadata_soup(
    overview: str,
    genres: str | list,
    keywords: str | list = "",
    director: str = "",
    cast: str | list = "",
    weight_director: int = 2,
    weight_genres: int = 2,
    weight_keywords: int = 2,
) -> str:
    """Construct an enriched 'metadata soup' document for NLP vectorization.

    Combines textual plot overview with normalized genres, keywords, director,
    and cast to maximize semantic relevance.
    """
    parts: List[str] = []

    # 1. Overview (clean text)
    if overview:
        cleaned_overview = clean_text(str(overview))
        parts.append(cleaned_overview)

    # 2. Genres (boosted)
    if genres:
        if isinstance(genres, str):
            # Split commas or spaces
            genre_list = [g.strip() for g in genres.replace("|", ",").split(",") if g.strip()]
        else:
            genre_list = list(genres)
        normalized_genres = [normalize_entity_name(g) for g in genre_list]
        for _ in range(weight_genres):
            parts.extend(normalized_genres)

    # 3. Keywords (boosted)
    if keywords:
        if isinstance(keywords, str):
            kw_list = [k.strip() for k in keywords.replace("|", ",").split(",") if k.strip()]
        else:
            kw_list = list(keywords)
        normalized_keywords = [normalize_entity_name(k) for k in kw_list]
        for _ in range(weight_keywords):
            parts.extend(normalized_keywords)

    # 4. Director (boosted)
    if director:
        norm_director = normalize_entity_name(str(director))
        if norm_director:
            for _ in range(weight_director):
                parts.append(norm_director)

    # 5. Top Cast
    if cast:
        if isinstance(cast, str):
            cast_list = [c.strip() for c in cast.replace("|", ",").split(",") if c.strip()]
        else:
            cast_list = list(cast)
        normalized_cast = [normalize_entity_name(c) for c in cast_list[:4]]
        parts.extend(normalized_cast)

    # Return consolidated string for vectorizer
    return " ".join(parts)
