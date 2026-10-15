# ==============================================================================
# MINI PROJECT: Movie Recommendation System using NLP and Python
# Students: INGOLE SUSHANT PRAKASHRAO & BHALKE DIKSHA SANGMESHWAR
# College: Dr. D. Y. Patil College of Engineering and Innovation
# Department: Engineering Science and Humanities (A.Y. 2026-27)
# ==============================================================================

import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

print("Loading Movie Recommendation System...\n")

# Step 1: Load the dataset
df = pd.read_csv('movies_dataset.csv')

# Step 2: Data Preprocessing (Combine genre and description into tags)
df['tags'] = df['genre'] + " " + df['description']
df['tags'] = df['tags'].str.lower()

# Step 3: Text Vectorization using Bag of Words (CountVectorizer)
cv = CountVectorizer(max_features=5000, stop_words='english')
vectors = cv.fit_transform(df['tags']).toarray()

# Step 4: Calculate Cosine Similarity between all movie vectors
similarity = cosine_similarity(vectors)

# Step 5: Recommendation Function
def recommend_movie(movie_name):
    # Case-insensitive check
    movie_name_clean = movie_name.strip().lower()
    matches = df[df['title'].str.lower() == movie_name_clean]
    
    if matches.empty:
        print(f"\n[!] Sorry, '{movie_name}' is not in our database.")
        print("Tip: Check spelling or pick from the list of available movies.\n")
        return

    # Find the row index of the matched movie
    movie_index = matches.index[0]
    matched_title = df.iloc[movie_index]['title']
    
    # Get similarity vector for this movie
    distances = similarity[movie_index]
    
    # Sort movies by similarity score in descending order
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])
    
    print(f"\nBecause you watched '{matched_title}', we recommend:")
    print("-" * 45)
    # movies_list[0] is the movie itself, so we take [1:4] for top 3 recommendations
    for i in movies_list[1:4]:
        rec_index = i[0]
        rec_title = df.iloc[rec_index]['title']
        score = i[1] * 100
        print(f" -> {rec_title} (Match: {score:.1f}%)")
    print("-" * 45 + "\n")

# Step 6: User Interaction Loop
if __name__ == '__main__':
    print("Available Movies: Interstellar, Inception, The Dark Knight, The Matrix, Toy Story, Finding Nemo, The Avengers, Iron Man, etc.")
    while True:
        user_input = input("Enter a movie name (or type 'exit' to quit): ").strip()
        
        if user_input.lower() == 'exit':
            print("Exiting recommendation system. Thank you!")
            break
        if not user_input:
            continue
            
        recommend_movie(user_input)
