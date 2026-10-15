"""Flask Web Application for Movie Recommendation System using NLP and Python.

Engineering Mini Project:
- Students: Ingole Sushant Prakashrao & Bhalke Diksha Sangmeshwar
- College: Dr. D. Y. Patil College of Engineering and Innovation
- Department: Engineering Science and Humanities
- Academic Year: 2026-27
"""

import os
from flask import Flask, jsonify, render_template, request
from src.recommender import MovieRecommender

app = Flask(__name__)

# Initialize the NLP Recommendation Engine
DATASET_PATH = os.path.join(os.path.dirname(__file__), "movies_dataset.csv")
recommender = MovieRecommender(dataset_path=DATASET_PATH)


@app.route("/")
def index():
    """Render the main single-page application dashboard."""
    stats = recommender.get_statistics()
    all_movies = recommender.get_all_movies(sort_by="rating")
    return render_template(
        "index.html",
        stats=stats,
        initial_movies=all_movies[:12],
        all_movies=all_movies,
        genres=stats["genres"],
        directors=stats["directors"],
    )


@app.route("/api/movies", methods=["GET"])
def get_movies():
    """Retrieve movies with optional search and filters."""
    search = request.args.get("search", "")
    genre = request.args.get("genre", "")
    director = request.args.get("director", "")
    min_rating = float(request.args.get("min_rating", 0.0))
    sort_by = request.args.get("sort_by", "rating")

    movies = recommender.get_all_movies(
        search=search,
        genre=genre,
        director=director,
        min_rating=min_rating,
        sort_by=sort_by,
    )
    return jsonify({"success": True, "count": len(movies), "movies": movies})


@app.route("/api/movie/<int:movie_id>", methods=["GET"])
def get_movie_detail(movie_id):
    """Retrieve details for a specific movie by index."""
    if movie_id < 0 or movie_id >= len(recommender.df):
        return jsonify({"success": False, "error": "Movie index out of range"}), 404
    movie = recommender._get_movie_dict(movie_id)
    return jsonify({"success": True, "movie": movie})


@app.route("/api/recommend", methods=["POST"])
def recommend_movies():
    """Endpoint to recommend movies similar to a given title."""
    data = request.get_json(silent=True) or {}
    movie_title = data.get("movie", "").strip()
    top_n = int(data.get("top_n", 6))
    method = data.get("method", "tfidf").strip().lower()

    if not movie_title:
        return jsonify({"success": False, "error": "Movie title is required."}), 400

    result = recommender.recommend(movie_name=movie_title, top_n=top_n, method=method)
    if not result.get("success"):
        return jsonify(result), 404

    return jsonify(result)


@app.route("/api/search", methods=["POST"])
def search_movies():
    """Endpoint for natural language / mood / plot query matching."""
    data = request.get_json(silent=True) or {}
    query = data.get("query", "").strip()
    top_n = int(data.get("top_n", 6))
    method = data.get("method", "tfidf").strip().lower()

    if not query:
        return jsonify({"success": False, "error": "Query cannot be empty."}), 400

    result = recommender.search_by_query(query=query, top_n=top_n, method=method)
    return jsonify(result)


@app.route("/api/explain", methods=["POST"])
def explain_nlp():
    """Endpoint for interactive NLP pipeline breakdown."""
    data = request.get_json(silent=True) or {}
    text = data.get("text", "").strip()

    if not text:
        return jsonify({"success": False, "error": "Text or movie title is required."}), 400

    explanation = recommender.explain_nlp_pipeline(text)
    return jsonify({"success": True, "data": explanation})


@app.route("/api/stats", methods=["GET"])
def get_stats():
    """Endpoint to retrieve system and model statistics."""
    return jsonify({"success": True, "stats": recommender.get_statistics()})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    print(f"\n========================================================")
    print(f"  🎬 CineMind NLP Movie Recommendation Server Running!")
    print(f"  URL: http://127.0.0.1:{port}")
    print(f"========================================================\n")
    app.run(host="0.0.0.0", port=port, debug=True)
