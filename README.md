# 🎬 CineMind NLP: Movie Recommendation System using NLP & Python

An intelligent, full-stack Movie Recommendation System built with **Natural Language Processing (NLP)**, **Machine Learning**, and **Python (Flask)**.

---

## 🏛️ Academic Information
- **Institution:** Dr. D. Y. Patil College of Engineering and Innovation
- **Department:** Department of Engineering Science and Humanities
- **Project Type:** Engineering Mini Project (DSA / Natural Language Processing)
- **Academic Year:** 2026-27
- **Students / Developers:**
  - **Ingole Sushant Prakashrao**
  - **Bhalke Diksha Sangmeshwar**

---

## 🚀 Key Highlights & Features

1. **Movie-to-Movie Content Recommender:**
   - Select or type any movie (with interactive keyboard-navigable autocomplete).
   - Generates Top-N recommendations with exact Cosine Similarity Match %, genre tags, IMDb rating, release year, director, and plot overview.
   - Highlights **Shared NLP Concepts** (e.g. `Space`, `Wormhole`, `Astronaut`, `Christopher Nolan`).

2. **Natural Language Mood & Plot Query Search:**
   - Describe what you want to watch in freeform English (e.g., *"Deep space voyage through wormholes to save mankind"* or *"Mind bending psychological thriller with detectives"*).
   - Vectorizes your prompt in real-time and ranks films using high-dimensional Cosine Similarity.

3. **Interactive Vectorizer Switch (TF-IDF vs. Bag of Words):**
   - Toggle between **TF-IDF** (Term Frequency - Inverse Document Frequency) and **CountVectorizer** (Bag of Words) to compare algorithmic behavior live in the browser.

4. **Interactive NLP Pipeline Visualizer:**
   - Step 1: Metadata Soup Ingestion (Title + Genre + Director + Plot)
   - Step 2: Text Normalization & Lowercasing
   - Step 3: Tokenization & Stopword Elimination (visual breakdown of kept informative tokens vs. removed stopwords)
   - Step 4: Morphological Suffix Stemming (e.g. `explorers` &rarr; `explor`)
   - Step 5: TF-IDF Feature Weights (animated bar chart of term weights)
   - Step 6: Mathematical Cosine Similarity derivation

5. **Movie Catalog & Explorer:**
   - Filter by genre, director, minimum IMDb rating slider, and search keywords.
   - 1-Click "Find Similar" button on any movie card.

6. **Cinematic Dark Glassmorphism UI:**
   - Obsidian & neon cyan/purple theme, responsive CSS Grid, modal popups, and offline-safe fallback posters.

---

## 📐 Mathematical Formulation

### 1. TF-IDF (Term Frequency - Inverse Document Frequency)
$$\text{TF-IDF}(t, d, D) = \text{TF}(t, d) \times \log\left(\frac{N}{\text{DF}(t)}\right)$$

- $\text{TF}(t, d)$: Number of times term $t$ appears in movie document $d$.
- $N$: Total number of movies in the catalog.
- $\text{DF}(t)$: Number of movie documents containing term $t$.

### 2. Cosine Similarity
$$\text{Cosine Similarity}(\vec{A}, \vec{B}) = \cos(\theta) = \frac{\vec{A} \cdot \vec{B}}{\|\vec{A}\| \|\vec{B}\|} = \frac{\sum_{i=1}^{n} A_i B_i}{\sqrt{\sum_{i=1}^{n} A_i^2} \sqrt{\sum_{i=1}^{n} B_i^2}}$$

Cosine similarity measures the cosine of the angle between two non-zero vectors in multi-dimensional space, making it length-invariant and ideal for plot text comparisons.

---

## 🛠️ Project Structure

```
MOVIE RECOMMENDATION/
├── app.py                   # Flask Web Server & REST API endpoints
├── main.py                  # Interactive CLI version of the recommender
├── simple_recommender.py    # Lightweight baseline CLI recommender
├── run_website.sh           # 1-Click shell script to launch web server
├── requirements.txt         # Project dependencies
├── movies_dataset.csv       # 52 curated movies with rich metadata & posters
├── src/
│   ├── __init__.py
│   ├── preprocessor.py      # NLP tokenization, stopword filtering, stemming & soup
│   └── recommender.py       # Recommender engine (TF-IDF, Count, query matching)
├── templates/
│   └── index.html           # Modern single-page web dashboard
└── static/
    ├── css/
    │   └── style.css        # Cinematic glassmorphism dark stylesheet
    └── js/
        └── app.js           # Client-side reactivity, search, autocomplete, modal
```

---

## 💻 How to Run the Project

### 1. Launch the Website (Recommended)

Run the convenient launch script:
```bash
./run_website.sh
```

Or run directly with Python:
```bash
./venv/bin/python app.py
```
*(Or `python3 app.py` if using system Python)*

Then open your browser and navigate to:
```
http://127.0.0.1:5001
```

---

### 2. Run the Terminal / CLI Recommender

```bash
./venv/bin/python main.py
```
Follow the interactive prompt:
- Option 1: Recommend by Movie Name
- Option 2: Search by Natural Language Query
- Option 3: List all available movies
- Option 4: Exit

---

## 🧪 Tech Stack
- **Backend:** Python 3.14, Flask 3.1
- **Machine Learning & NLP:** scikit-learn (TfidfVectorizer, CountVectorizer, cosine_similarity), pandas, numpy
- **Frontend:** Semantic HTML5, CSS3 Glassmorphism, Vanilla ES6+ JavaScript
- **Dataset:** 52 curated top-rated international movies across 10 film genres
