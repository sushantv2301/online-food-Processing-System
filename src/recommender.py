"""Movie Recommendation Engine using NLP and Cosine Similarity.

Provides Content-Based Recommendation, Natural Language Mood/Query Search,
and NLP Explainability (Tokenization, Stopword Filtering, TF-IDF analysis).
"""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.preprocessor import (
    STOPWORDS,
    clean_text,
    create_metadata_soup,
    normalize_entity_name,
    preprocess_nlp,
    simple_stem,
    tokenize,
)


class MovieRecommender:
    """Core recommendation engine combining NLP preprocessing and vector space similarity."""

    def __init__(self, dataset_path: str = "movies_dataset.csv"):
        self.dataset_path = dataset_path
        self.df: pd.DataFrame = pd.DataFrame()
        self.tfidf_vectorizer: Optional[TfidfVectorizer] = None
        self.count_vectorizer: Optional[CountVectorizer] = None
        self.tfidf_matrix: Optional[np.ndarray] = None
        self.count_matrix: Optional[np.ndarray] = None
        self.tfidf_similarity: Optional[np.ndarray] = None
        self.count_similarity: Optional[np.ndarray] = None
        self.title_lookup: Dict[str, int] = {}
        self.genres_list: List[str] = []
        self.directors_list: List[str] = []
        self.vocab_size: int = 0
        self.load_and_train()

    def load_and_train(self) -> None:
        """Load dataset, build NLP metadata tags, and compute similarity matrices."""
        if not os.path.exists(self.dataset_path):
            raise FileNotFoundError(f"Dataset not found at {self.dataset_path}")

        df = pd.read_csv(self.dataset_path)

        # Standardize expected columns
        df["title"] = df["title"].fillna("").astype(str).str.strip()
        df["genre"] = df["genre"].fillna("").astype(str)
        df["description"] = df["description"].fillna("").astype(str)
        df["director"] = df["director"].fillna("Unknown").astype(str)
        df["rating"] = pd.to_numeric(df.get("rating", 7.5), errors="coerce").fillna(7.5)

        if "year" not in df.columns:
            df["year"] = 2020
        else:
            df["year"] = pd.to_numeric(df["year"], errors="coerce").fillna(2020).astype(int)

        if "poster_url" not in df.columns:
            df["poster_url"] = ""
        else:
            df["poster_url"] = df["poster_url"].fillna("").astype(str)

        # Build Enriched NLP Metadata Soup
        # Combines description, genres, and director (with entity normalization)
        soups: List[str] = []
        processed_tags: List[str] = []

        for _, row in df.iterrows():
            soup = create_metadata_soup(
                overview=row["description"],
                genres=row["genre"],
                director=row["director"],
                weight_director=2,
                weight_genres=2,
            )
            soups.append(soup)
            # Apply NLP pipeline (tokenization, stopword removal, stemming)
            processed_tags.append(preprocess_nlp(soup, stem=True))

        df["metadata_soup"] = soups
        df["nlp_tags"] = processed_tags

        self.df = df

        # Quick lookup map: lowercase title -> row index
        self.title_lookup = {
            str(title).strip().lower(): idx for idx, title in enumerate(self.df["title"].values)
        }

        # Train TF-IDF Vectorizer
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words="english",
            ngram_range=(1, 2),  # capture single words & bigrams
        )
        self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(self.df["nlp_tags"]).toarray()
        self.tfidf_similarity = cosine_similarity(self.tfidf_matrix)

        # Train CountVectorizer (Bag of Words)
        self.count_vectorizer = CountVectorizer(
            max_features=5000,
            stop_words="english",
            ngram_range=(1, 1),
        )
        self.count_matrix = self.count_vectorizer.fit_transform(self.df["nlp_tags"]).toarray()
        self.count_similarity = cosine_similarity(self.count_matrix)

        self.vocab_size = len(self.tfidf_vectorizer.get_feature_names_out())

        # Collect unique genres and directors
        all_genres = set()
        for g_str in self.df["genre"]:
            for g in str(g_str).replace("|", ",").split(","):
                g_clean = g.strip()
                if g_clean:
                    all_genres.add(g_clean)
        self.genres_list = sorted(list(all_genres))
        self.directors_list = sorted([d for d in self.df["director"].unique() if d and d != "Unknown"])

    def _get_movie_dict(self, idx: int) -> Dict[str, Any]:
        """Convert a row of DataFrame to a dictionary."""
        row = self.df.iloc[idx]
        return {
            "id": int(idx),
            "title": str(row["title"]),
            "genre": str(row["genre"]),
            "description": str(row["description"]),
            "director": str(row["director"]),
            "rating": float(row["rating"]),
            "year": int(row["year"]),
            "poster_url": str(row["poster_url"]),
            "nlp_tags": str(row["nlp_tags"]),
        }

    def get_shared_keywords(self, idx1: int, idx2: int, top_k: int = 5) -> List[str]:
        """Find the top overlapping NLP tokens between two movies based on TF-IDF weights."""
        if self.tfidf_matrix is None or self.tfidf_vectorizer is None:
            return []

        feature_names = self.tfidf_vectorizer.get_feature_names_out()
        v1 = self.tfidf_matrix[idx1]
        v2 = self.tfidf_matrix[idx2]

        # Element-wise product identifies joint importance
        joint_weight = v1 * v2
        non_zero_indices = np.where(joint_weight > 0)[0]
        if len(non_zero_indices) == 0:
            return []

        sorted_indices = non_zero_indices[np.argsort(-joint_weight[non_zero_indices])]
        top_terms = [feature_names[i] for i in sorted_indices[:top_k]]
        return [t.replace("_", " ").title() for t in top_terms]

    def recommend(
        self, movie_name: str, top_n: int = 6, method: str = "tfidf"
    ) -> Dict[str, Any]:
        """Recommend similar movies for a given movie title."""
        clean_input = movie_name.strip().lower()

        if clean_input not in self.title_lookup:
            # Fuzzy fallback: check if input is substring of any title
            partial_matches = [
                idx for title, idx in self.title_lookup.items() if clean_input in title
            ]
            if not partial_matches:
                return {
                    "success": False,
                    "error": f"Movie '{movie_name}' not found in database.",
                    "available_movies": list(self.df["title"].values[:10]),
                }
            movie_index = partial_matches[0]
        else:
            movie_index = self.title_lookup[clean_input]

        target_movie = self._get_movie_dict(movie_index)

        # Select similarity matrix
        sim_matrix = (
            self.tfidf_similarity if method.lower() == "tfidf" else self.count_similarity
        )
        if sim_matrix is None:
            sim_matrix = self.tfidf_similarity

        scores = sim_matrix[movie_index]

        # Sort indices by similarity descending
        ranked_indices = np.argsort(-scores)

        recommendations = []
        count = 0
        for idx in ranked_indices:
            # Skip the query movie itself
            if idx == movie_index:
                continue
            score = float(scores[idx])
            if score <= 0.001:
                continue

            rec_movie = self._get_movie_dict(idx)
            rec_movie["similarity_score"] = round(score * 100, 1)
            rec_movie["shared_keywords"] = self.get_shared_keywords(movie_index, idx)
            recommendations.append(rec_movie)
            count += 1
            if count >= top_n:
                break

        return {
            "success": True,
            "target_movie": target_movie,
            "method": "TF-IDF (Term Frequency - Inverse Document Frequency)"
            if method.lower() == "tfidf"
            else "CountVectorizer (Bag of Words)",
            "count": len(recommendations),
            "recommendations": recommendations,
        }

    def search_by_query(
        self, query: str, top_n: int = 6, method: str = "tfidf"
    ) -> Dict[str, Any]:
        """Find movies matching a free-text natural language query or description."""
        clean_q = query.strip()
        if not clean_q:
            return {"success": False, "error": "Query cannot be empty."}

        # Apply NLP preprocessing to query
        processed_q = preprocess_nlp(clean_q, stem=True)
        if not processed_q.strip():
            # In case all words were stopwords, fallback to tokenized
            processed_q = " ".join(tokenize(clean_q))

        vectorizer = (
            self.tfidf_vectorizer if method.lower() == "tfidf" else self.count_vectorizer
        )
        matrix = self.tfidf_matrix if method.lower() == "tfidf" else self.count_matrix

        if vectorizer is None or matrix is None:
            return {"success": False, "error": "Model not trained."}

        # Vectorize user query
        query_vector = vectorizer.transform([processed_q]).toarray()
        scores = cosine_similarity(query_vector, matrix)[0]

        ranked_indices = np.argsort(-scores)
        feature_names = vectorizer.get_feature_names_out()
        query_words = set(processed_q.split())

        results = []
        count = 0
        for idx in ranked_indices:
            score = float(scores[idx])
            if score <= 0.001 or count >= top_n:
                break

            movie = self._get_movie_dict(idx)
            movie["relevance_score"] = round(score * 100, 1)

            # Find matching terms between query and movie
            movie_tags = set(self.df.iloc[idx]["nlp_tags"].split())
            matching_terms = [
                w.replace("_", " ").title()
                for w in query_words.intersection(movie_tags)
                if len(w) > 2
            ]
            movie["matched_terms"] = matching_terms[:5]

            results.append(movie)
            count += 1

        return {
            "success": True,
            "raw_query": clean_q,
            "processed_query": processed_q,
            "method": "TF-IDF" if method.lower() == "tfidf" else "CountVectorizer",
            "count": len(results),
            "results": results,
        }

    def explain_nlp_pipeline(self, text_or_title: str) -> Dict[str, Any]:
        """Provides step-by-step NLP breakdown of text or a movie's description."""
        raw_text = text_or_title.strip()
        movie_title = None

        # Check if it's a known movie title
        clean_input = raw_text.lower()
        if clean_input in self.title_lookup:
            idx = self.title_lookup[clean_input]
            row = self.df.iloc[idx]
            movie_title = row["title"]
            raw_text = (
                f"{row['title']} | Genre: {row['genre']} | Director: {row['director']} | "
                f"Plot: {row['description']}"
            )

        # Step 1: Lowercase & Clean
        cleaned = clean_text(raw_text)

        # Step 2: Tokenize
        raw_tokens = tokenize(raw_text)

        # Step 3: Stopword Analysis
        removed_stopwords = [t for t in raw_tokens if t in STOPWORDS]
        filtered_tokens = [t for t in raw_tokens if t not in STOPWORDS]

        # Step 4: Stemming
        stemmed_tokens = [simple_stem(t) for t in filtered_tokens]
        stem_map = [
            {"original": orig, "stemmed": stem}
            for orig, stem in zip(filtered_tokens, stemmed_tokens)
            if orig != stem
        ]

        # Step 5: TF-IDF feature weights
        processed_str = " ".join(stemmed_tokens)
        top_features = []
        if self.tfidf_vectorizer:
            vec = self.tfidf_vectorizer.transform([processed_str]).toarray()[0]
            feature_names = self.tfidf_vectorizer.get_feature_names_out()
            nonzero = np.where(vec > 0)[0]
            if len(nonzero) > 0:
                sorted_nonzero = nonzero[np.argsort(-vec[nonzero])]
                for i in sorted_nonzero[:10]:
                    top_features.append(
                        {
                            "term": feature_names[i].replace("_", " "),
                            "weight": round(float(vec[i]), 4),
                        }
                    )

        return {
            "movie_title": movie_title,
            "raw_text": raw_text,
            "cleaned_text": cleaned,
            "raw_tokens_count": len(raw_tokens),
            "raw_tokens": raw_tokens[:30],
            "removed_stopwords_count": len(removed_stopwords),
            "removed_stopwords": list(set(removed_stopwords))[:20],
            "filtered_tokens_count": len(filtered_tokens),
            "filtered_tokens": filtered_tokens[:30],
            "stemmed_tokens": stemmed_tokens[:30],
            "stem_transformations": stem_map[:10],
            "top_tfidf_features": top_features,
        }

    def get_all_movies(
        self,
        search: str = "",
        genre: str = "",
        director: str = "",
        min_rating: float = 0.0,
        sort_by: str = "rating",
    ) -> List[Dict[str, Any]]:
        """Filter and return movie records."""
        sub_df = self.df.copy()

        if search:
            s = search.strip().lower()
            sub_df = sub_df[
                sub_df["title"].str.lower().str.contains(s)
                | sub_df["description"].str.lower().str.contains(s)
                | sub_df["director"].str.lower().str.contains(s)
            ]

        if genre and genre != "all":
            sub_df = sub_df[sub_df["genre"].str.contains(genre, case=False, na=False)]

        if director and director != "all":
            sub_df = sub_df[sub_df["director"] == director]

        if min_rating > 0.0:
            sub_df = sub_df[sub_df["rating"] >= min_rating]

        if sort_by == "rating":
            sub_df = sub_df.sort_values(by="rating", ascending=False)
        elif sort_by == "year":
            sub_df = sub_df.sort_values(by="year", ascending=False)
        elif sort_by == "title":
            sub_df = sub_df.sort_values(by="title", ascending=True)

        return [self._get_movie_dict(idx) for idx in sub_df.index]

    def get_statistics(self) -> Dict[str, Any]:
        """Return dataset & model summary metrics."""
        return {
            "total_movies": len(self.df),
            "vocabulary_size": self.vocab_size,
            "unique_genres": len(self.genres_list),
            "unique_directors": len(self.directors_list),
            "average_rating": round(float(self.df["rating"].mean()), 2),
            "genres": self.genres_list,
            "directors": self.directors_list,
        }
