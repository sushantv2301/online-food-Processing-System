"""Movie Recommendation System using Natural Language Processing (NLP) and Python.

Developed for Engineering Mini Project (DSA / NLP)
Students: Ingole Sushant Prakashrao & Bhalke Diksha Sangmeshwar
College: Dr. D. Y. Patil College of Engineering and Innovation
Department: Engineering Science and Humanities
Academic Year: 2026-27
"""

import os
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def load_and_preprocess_data(dataset_path="movies_dataset.csv"):
    """Load the dataset and construct NLP tags from genre and description."""
    if not os.path.exists(dataset_path):
        raise FileNotFoundError(
            f"Dataset '{dataset_path}' not found! Please ensure '{dataset_path}' is in the project folder."
        )

    # Step 1: Load dataset into a pandas DataFrame
    df = pd.read_csv(dataset_path)

    # Fill any missing values with empty strings
    df["genre"] = df["genre"].fillna("")
    df["description"] = df["description"].fillna("")
    if "director" in df.columns:
        df["director"] = df["director"].fillna("")

    # Step 2: NLP Feature Engineering - Create combined tags
    # We combine genre and description (and director if available)
    if "director" in df.columns:
        df["tags"] = df["genre"] + " " + df["description"] + " " + df["director"]
    else:
        df["tags"] = df["genre"] + " " + df["description"]

    # Step 3: Text Normalization (convert to lowercase)
    df["tags"] = df["tags"].str.lower()

    return df


def build_similarity_model(df, use_tfidf=True):
    """Convert text tags into vectors and calculate Cosine Similarity.
    
    Parameters:
        df (pd.DataFrame): Preprocessed movie DataFrame.
        use_tfidf (bool): If True, uses TfidfVectorizer (weighted NLP).
                          If False, uses CountVectorizer (Bag of Words).
    """
    if use_tfidf:
        # TF-IDF gives higher weight to unique, informative words
        vectorizer = TfidfVectorizer(max_features=5000, stop_words="english")
    else:
        # CountVectorizer calculates raw word frequency
        vectorizer = CountVectorizer(max_features=5000, stop_words="english")

    # Fit and transform the movie tags into numerical vectors
    vectors = vectorizer.fit_transform(df["tags"]).toarray()

    # Calculate pairwise Cosine Similarity matrix between all movies
    similarity_matrix = cosine_similarity(vectors)

    return similarity_matrix, vectorizer


def recommend_movie(movie_name, df, similarity_matrix, top_n=5):
    """Find and display the top N most similar movies for a given movie title."""
    # Create a case-insensitive lookup dictionary: {lowercase_title: original_title}
    title_lookup = {title.strip().lower(): title for title in df["title"].values}
    clean_input = movie_name.strip().lower()

    if clean_input not in title_lookup:
        print(f"\n[!] Sorry, '{movie_name}' is not found in our database.")
        print("Tip: Check spelling or choose one from the available list below.\n")
        return

    # Retrieve exact matching title and its index
    exact_title = title_lookup[clean_input]
    movie_index = df[df["title"] == exact_title].index[0]

    # Get similarity scores for this movie with all other movies
    similarity_scores = similarity_matrix[movie_index]

    # Enumerate scores with their index, and sort in descending order
    # x[1] is the similarity score
    ranked_movies = sorted(
        list(enumerate(similarity_scores)),
        reverse=True,
        key=lambda x: x[1]
    )

    print("\n" + "=" * 65)
    print(f"  RECOMMENDATIONS FOR: '{exact_title}'")
    print(f"  Genre: {df.iloc[movie_index]['genre']}")
    print("=" * 65)

    # Skip index 0 because that is the input movie itself (similarity = 1.0)
    count = 0
    for idx, score in ranked_movies[1:]:
        if count >= top_n:
            break
        rec_title = df.iloc[idx]["title"]
        rec_genre = df.iloc[idx]["genre"]
        rec_rating = df.iloc[idx].get("rating", "N/A")
        match_percentage = score * 100

        print(f"  {count + 1}. {rec_title} ({rec_genre})")
        print(f"     Match Score: {match_percentage:.1f}%  |  IMDb: {rec_rating}/10")
        count += 1

    print("=" * 65 + "\n")


def search_by_natural_language(query, df, vectorizer, top_n=3):
    """NLP Feature: Recommend movies based on a user's free-text natural language query.
    
    Example: 'space exploration with black holes and time travel'
    """
    clean_query = query.strip().lower()
    if not clean_query:
        print("[!] Please enter a valid description.")
        return

    # Transform the user's query into the same vector space
    query_vector = vectorizer.transform([clean_query]).toarray()

    # Compute cosine similarity between the query vector and all movie vectors
    # Note: We re-vectorize movie tags to compute similarity with query
    movie_vectors = vectorizer.transform(df["tags"]).toarray()
    scores = cosine_similarity(query_vector, movie_vectors)[0]

    # Sort descending
    ranked = sorted(list(enumerate(scores)), reverse=True, key=lambda x: x[1])

    print("\n" + "=" * 65)
    print(f"  NLP SEMANTIC MATCHES FOR QUERY: '{query}'")
    print("=" * 65)

    count = 0
    for idx, score in ranked:
        if score <= 0.0 or count >= top_n:
            break
        rec_title = df.iloc[idx]["title"]
        rec_genre = df.iloc[idx]["genre"]
        rec_rating = df.iloc[idx].get("rating", "N/A")
        print(f"  {count + 1}. {rec_title} ({rec_genre})")
        print(f"     Relevance Score: {score * 100:.1f}%  |  IMDb: {rec_rating}/10")
        count += 1

    if count == 0:
        print("  No strong semantic matches found. Try different descriptive keywords!")
    print("=" * 65 + "\n")


def main():
    """Main execution loop for user interaction."""
    print("\n" + "#" * 65)
    print("  MOVIE RECOMMENDATION SYSTEM USING NLP & PYTHON")
    print("  Dr. D. Y. Patil College of Engineering and Innovation")
    print("  Students: Sushant Ingole & Diksha Bhalke (A.Y. 2026-27)")
    print("#" * 65 + "\n")

    print("[*] Loading dataset...")
    df = load_and_preprocess_data("movies_dataset.csv")
    print(f"    Loaded {len(df)} movies successfully.")

    print("[*] Building NLP Vectorizer and Cosine Similarity Matrix...")
    similarity_matrix, vectorizer = build_similarity_model(df, use_tfidf=True)
    print("    Model training completed!\n")

    while True:
        print("-" * 65)
        print("OPTIONS:")
        print("  1. Recommend by Movie Name")
        print("  2. Recommend by Natural Language Query (e.g. 'space time travel')")
        print("  3. List All Available Movies in Database")
        print("  4. Exit")
        print("-" * 65)

        choice = input("Enter your choice (1-4): ").strip()

        if choice == "1":
            movie_name = input("Enter movie name: ").strip()
            if movie_name:
                recommend_movie(movie_name, df, similarity_matrix, top_n=4)

        elif choice == "2":
            query = input("Describe what kind of movie you want to watch: ").strip()
            if query:
                search_by_natural_language(query, df, vectorizer, top_n=4)

        elif choice == "3":
            print("\nAvailable Movies in Database:")
            for i, title in enumerate(sorted(df["title"].values), 1):
                print(f"  {i:2d}. {title}")
            print()

        elif choice == "4" or choice.lower() == "exit":
            print("\nThank you for using the Movie Recommendation System. Goodbye!\n")
            break

        else:
            print("\n[!] Invalid choice. Please enter 1, 2, 3, or 4.\n")


if __name__ == "__main__":
    main()
