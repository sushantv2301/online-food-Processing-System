/**
 * CineMind NLP - Client Application Logic
 * Engineering Mini Project (DSA / NLP)
 * Students: Sushant Ingole & Diksha Bhalke
 */

document.addEventListener("DOMContentLoaded", () => {
    // State management
    const state = {
        allMovies: window.INITIAL_MOVIES || [],
        selectedMethod: "tfidf",
        currentTab: "recommender",
        debounceTimer: null,
    };

    // DOM Elements
    const elements = {
        navTabs: document.querySelectorAll(".nav-tab"),
        tabContents: document.querySelectorAll(".tab-content"),
        
        // Recommender
        movieInput: document.getElementById("movieInput"),
        autocompleteDropdown: document.getElementById("autocompleteDropdown"),
        methodSelector: document.getElementById("methodSelector"),
        topNSelect: document.getElementById("topNSelect"),
        btnRecommend: document.getElementById("btnRecommend"),
        btnSurpriseMe: document.getElementById("btnSurpriseMe"),
        quickPicks: document.getElementById("quickPicks"),
        targetMovieSection: document.getElementById("targetMovieSection"),
        recsHeader: document.getElementById("recsHeader"),
        recsTitle: document.getElementById("recsTitle"),
        recsMethodBadge: document.getElementById("recsMethodBadge"),
        recommendationsGrid: document.getElementById("recommendationsGrid"),
        
        // Semantic Search
        nlQueryInput: document.getElementById("nlQueryInput"),
        btnNlSearch: document.getElementById("btnNlSearch"),
        btnClearNl: document.getElementById("btnClearNl"),
        sampleChips: document.querySelectorAll(".sample-chip"),
        nlResultsHeader: document.getElementById("nlResultsHeader"),
        nlResultsTitle: document.getElementById("nlResultsTitle"),
        nlQueryTokensBadge: document.getElementById("nlQueryTokensBadge"),
        nlResultsGrid: document.getElementById("nlResultsGrid"),
        
        // Catalog
        catalogSearch: document.getElementById("catalogSearch"),
        genreFilter: document.getElementById("genreFilter"),
        directorFilter: document.getElementById("directorFilter"),
        minRatingRange: document.getElementById("minRatingRange"),
        ratingValue: document.getElementById("ratingValue"),
        sortBySelect: document.getElementById("sortBySelect"),
        catalogGrid: document.getElementById("catalogGrid"),
        catalogCount: document.getElementById("catalogCount"),
        
        // Visualizer
        visualizerInput: document.getElementById("visualizerInput"),
        btnInspectNlp: document.getElementById("btnInspectNlp"),
        step1Output: document.getElementById("step1Output"),
        step2Output: document.getElementById("step2Output"),
        keptTokens: document.getElementById("keptTokens"),
        removedTokens: document.getElementById("removedTokens"),
        keptTokensCount: document.getElementById("keptTokensCount"),
        removedTokensCount: document.getElementById("removedTokensCount"),
        stemTransformations: document.getElementById("stemTransformations"),
        tfidfBars: document.getElementById("tfidfBars"),
        
        // Modal & Toast
        movieModal: document.getElementById("movieModal"),
        modalContent: document.getElementById("modalContent"),
        toast: document.getElementById("toast"),
    };

    // =========================================================================
    // 1. Navigation & Tab Switching
    // =========================================================================
    window.switchTab = (tabId) => {
        state.currentTab = tabId;
        elements.navTabs.forEach(btn => {
            btn.classList.toggle("active", btn.dataset.tab === tabId);
        });

        const tabMap = {
            "recommender": "recommenderTab",
            "semantic-search": "semanticSearchTab",
            "catalog": "catalogTab",
            "nlp-visualizer": "nlpVisualizerTab",
            "about": "aboutTab",
        };

        elements.tabContents.forEach(content => {
            content.classList.toggle("active", content.id === tabMap[tabId]);
        });

        // If switching to visualizer with empty inspect, trigger inspection of current input
        if (tabId === "nlp-visualizer" && elements.visualizerInput.value.trim()) {
            inspectNlp(elements.visualizerInput.value.trim());
        }
    };

    elements.navTabs.forEach(tab => {
        tab.addEventListener("click", () => {
            switchTab(tab.dataset.tab);
        });
    });

    // =========================================================================
    // 2. Poster Fallback Image Handler
    // =========================================================================
    window.handlePosterError = (imgEl, title, genre) => {
        const parent = imgEl.parentElement;
        if (!parent) return;

        const genreIconMap = {
            "Science Fiction": "🚀",
            "Action": "💥",
            "Animation": "🎨",
            "Drama": "🎭",
            "Crime": "🔍",
            "Mystery": "🕵️",
            "Adventure": "🗺️",
            "Comedy": "✨",
            "Romance": "❤️",
            "Thriller": "⚡"
        };

        const icon = genreIconMap[genre] || "🎬";
        const fallback = document.createElement("div");
        fallback.className = "fallback-poster";
        fallback.innerHTML = `
            <div class="fallback-poster-icon">${icon}</div>
            <div class="fallback-poster-title">${title}</div>
            <div class="fallback-poster-genre">${genre}</div>
        `;
        imgEl.style.display = "none";
        parent.appendChild(fallback);
    };

    // =========================================================================
    // 3. Autocomplete for Movie Recommender
    // =========================================================================
    let activeDropdownIndex = -1;

    function renderAutocomplete(filtered) {
        if (!filtered.length) {
            elements.autocompleteDropdown.innerHTML = `<div class="autocomplete-item" style="color: var(--text-muted);">No movies found</div>`;
            elements.autocompleteDropdown.classList.remove("hidden");
            return;
        }

        elements.autocompleteDropdown.innerHTML = filtered.map((m, idx) => `
            <div class="autocomplete-item" data-index="${idx}" data-title="${m.title}">
                <span><strong>${m.title}</strong> (${m.year})</span>
                <span class="autocomplete-item-genre">${m.genre} &bull; ${m.rating}★</span>
            </div>
        `).join("");
        elements.autocompleteDropdown.classList.remove("hidden");
        activeDropdownIndex = -1;
    }

    elements.movieInput.addEventListener("input", (e) => {
        const query = e.target.value.trim().toLowerCase();
        if (!query) {
            elements.autocompleteDropdown.classList.add("hidden");
            return;
        }

        const matches = state.allMovies
            .filter(m => m.title.toLowerCase().includes(query))
            .slice(0, 8);

        renderAutocomplete(matches);
    });

    elements.movieInput.addEventListener("keydown", (e) => {
        const items = elements.autocompleteDropdown.querySelectorAll(".autocomplete-item");
        if (elements.autocompleteDropdown.classList.contains("hidden") || !items.length) return;

        if (e.key === "ArrowDown") {
            e.preventDefault();
            activeDropdownIndex = (activeDropdownIndex + 1) % items.length;
            updateDropdownHighlight(items);
        } else if (e.key === "ArrowUp") {
            e.preventDefault();
            activeDropdownIndex = (activeDropdownIndex - 1 + items.length) % items.length;
            updateDropdownHighlight(items);
        } else if (e.key === "Enter" && activeDropdownIndex >= 0) {
            e.preventDefault();
            const selectedTitle = items[activeDropdownIndex].dataset.title;
            if (selectedTitle) {
                elements.movieInput.value = selectedTitle;
                elements.autocompleteDropdown.classList.add("hidden");
                fetchRecommendations(selectedTitle);
            }
        }
    });

    function updateDropdownHighlight(items) {
        items.forEach((item, idx) => {
            item.classList.toggle("selected", idx === activeDropdownIndex);
        });
    }

    elements.autocompleteDropdown.addEventListener("click", (e) => {
        const item = e.target.closest(".autocomplete-item");
        if (item && item.dataset.title) {
            elements.movieInput.value = item.dataset.title;
            elements.autocompleteDropdown.classList.add("hidden");
            fetchRecommendations(item.dataset.title);
        }
    });

    document.addEventListener("click", (e) => {
        if (!elements.movieInput.contains(e.target) && !elements.autocompleteDropdown.contains(e.target)) {
            elements.autocompleteDropdown.classList.add("hidden");
        }
    });

    // Method selector toggle (TF-IDF vs Count)
    elements.methodSelector.addEventListener("click", (e) => {
        const btn = e.target.closest(".segment-btn");
        if (!btn) return;
        elements.methodSelector.querySelectorAll(".segment-btn").forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        state.selectedMethod = btn.dataset.method;
        showToast(`Switched vectorizer to ${state.selectedMethod.toUpperCase()}`);
        
        // Re-run recommendation if a movie is selected
        if (elements.movieInput.value.trim()) {
            fetchRecommendations(elements.movieInput.value.trim());
        }
    });

    // =========================================================================
    // 4. Recommendation Fetcher & Card Renderer
    // =========================================================================
    async function fetchRecommendations(movieTitle) {
        if (!movieTitle) return;

        elements.btnRecommend.disabled = true;
        elements.btnRecommend.innerHTML = `<span class="btn-icon">⏳</span> Computing Vectors...`;
        elements.recommendationsGrid.innerHTML = `
            <div style="grid-column: 1 / -1; text-align: center; padding: 3rem; color: var(--text-secondary);">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">⚙️</div>
                Computing NLP Cosine Similarity Matrix for "${movieTitle}"...
            </div>
        `;

        try {
            const response = await fetch("/api/recommend", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    movie: movieTitle,
                    top_n: parseInt(elements.topNSelect.value, 10),
                    method: state.selectedMethod,
                }),
            });

            const data = await response.json();
            if (!data.success) {
                showToast(data.error || "Movie not found", "error");
                elements.recommendationsGrid.innerHTML = `
                    <div style="grid-column: 1 / -1; text-align: center; padding: 2rem; color: #f87171;">
                        [!] ${data.error}
                    </div>
                `;
                return;
            }

            // Render Target Movie Header Banner
            renderTargetMovieBanner(data.target_movie);

            // Update Method Badge
            elements.recsTitle.textContent = `Recommended for: "${data.target_movie.title}"`;
            elements.recsMethodBadge.textContent = `${data.method}`;

            // Render Recommended Movie Cards
            renderRecommendationCards(data.recommendations);
            showToast(`Generated ${data.count} recommendations!`);

        } catch (error) {
            console.error("Error fetching recommendations:", error);
            showToast("Failed to compute recommendations.", "error");
        } finally {
            elements.btnRecommend.disabled = false;
            elements.btnRecommend.innerHTML = `<span class="btn-icon">⚡</span> Calculate Recommendations`;
        }
    }

    function renderTargetMovieBanner(movie) {
        elements.targetMovieSection.innerHTML = `
            <div class="target-movie-card">
                <img 
                    src="${movie.poster_url}" 
                    alt="${movie.title}" 
                    class="target-poster-thumb"
                    onerror="handlePosterError(this, '${movie.title}', '${movie.genre}')"
                >
                <div class="target-details">
                    <h3>${movie.title} <span style="font-size: 1.1rem; color: var(--text-muted);">(${movie.year})</span></h3>
                    <div class="target-meta">
                        <span class="genre-tag">${movie.genre}</span>
                        <span>&bull;</span>
                        <span>Directed by <strong>${movie.director}</strong></span>
                        <span>&bull;</span>
                        <span style="color: #f59e0b; font-weight: 700;">★ ${movie.rating}/10</span>
                    </div>
                    <p class="target-plot">${movie.description}</p>
                    <div style="margin-top: 0.85rem;">
                        <button class="btn btn-sm btn-outline" onclick="inspectNlp('${movie.title}')">
                            🔬 Inspect NLP Vectors in Pipeline
                        </button>
                    </div>
                </div>
            </div>
        `;
    }

    function renderRecommendationCards(movies) {
        if (!movies.length) {
            elements.recommendationsGrid.innerHTML = `
                <div style="grid-column: 1 / -1; text-align: center; padding: 3rem; color: var(--text-muted);">
                    No similar movies met the similarity threshold.
                </div>
            `;
            return;
        }

        elements.recommendationsGrid.innerHTML = movies.map(m => {
            const scoreClass = m.similarity_score >= 70 ? "high" : m.similarity_score >= 40 ? "medium" : "low";
            const keywordsHtml = m.shared_keywords && m.shared_keywords.length > 0
                ? `<div class="shared-tokens-block">
                     <span class="shared-tokens-label">Shared NLP Concepts:</span>
                     <div class="shared-tokens-list">
                       ${m.shared_keywords.map(kw => `<span class="token-pill">${kw}</span>`).join("")}
                     </div>
                   </div>`
                : "";

            return `
                <div class="movie-card" data-id="${m.id}">
                    <div class="poster-container">
                        <img 
                            src="${m.poster_url}" 
                            alt="${m.title} Poster" 
                            loading="lazy" 
                            onerror="handlePosterError(this, '${m.title}', '${m.genre}')"
                        >
                        <div class="rating-badge">
                            <span class="star-icon">★</span> ${m.rating}
                        </div>
                        <div class="year-badge">${m.year}</div>
                        <div class="similarity-badge ${scoreClass}">
                            <span>⚡</span> ${m.similarity_score}% Match
                        </div>
                    </div>
                    <div class="movie-info">
                        <div class="genre-tag">${m.genre}</div>
                        <h4 class="movie-title">${m.title}</h4>
                        <p class="movie-director">Dir: <strong>${m.director}</strong></p>
                        <p class="movie-plot">${m.description}</p>
                        ${keywordsHtml}
                        <div class="card-actions">
                            <button class="btn btn-sm btn-outline" onclick="openMovieDetails(${m.id})">Details</button>
                            <button class="btn btn-sm btn-primary" onclick="recommendFromCatalog('${m.title}')">Recommend</button>
                        </div>
                    </div>
                </div>
            `;
        }).join("");
    }

    // Trigger on button click
    elements.btnRecommend.addEventListener("click", () => {
        const title = elements.movieInput.value.trim();
        if (title) fetchRecommendations(title);
        else showToast("Please enter a movie title.", "warning");
    });

    // Quick picks chips
    elements.quickPicks.addEventListener("click", (e) => {
        const chip = e.target.closest(".chip");
        if (chip && chip.dataset.title) {
            elements.movieInput.value = chip.dataset.title;
            fetchRecommendations(chip.dataset.title);
        }
    });

    // Surprise me (random pick)
    elements.btnSurpriseMe.addEventListener("click", () => {
        if (!state.allMovies.length) return;
        const randomIndex = Math.floor(Math.random() * state.allMovies.length);
        const randomMovie = state.allMovies[randomIndex];
        elements.movieInput.value = randomMovie.title;
        fetchRecommendations(randomMovie.title);
    });

    // =========================================================================
    // 5. Natural Language & Mood Search
    // =========================================================================
    async function searchNaturalLanguage(query) {
        if (!query.trim()) {
            showToast("Please describe what kind of movie you'd like to watch.", "warning");
            return;
        }

        elements.btnNlSearch.disabled = true;
        elements.btnNlSearch.innerHTML = `<span class="btn-icon">⏳</span> Semantic Search...`;
        elements.nlResultsHeader.style.display = "flex";
        elements.nlResultsTitle.textContent = `Matches for: "${query.slice(0, 45)}..."`;
        elements.nlResultsGrid.innerHTML = `
            <div style="grid-column: 1 / -1; text-align: center; padding: 3rem; color: var(--text-secondary);">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">🧠</div>
                Transforming query to vector space and computing cosine similarity...
            </div>
        `;

        try {
            const response = await fetch("/api/search", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    query: query,
                    top_n: 6,
                    method: state.selectedMethod,
                }),
            });

            const data = await response.json();
            if (!data.success) {
                showToast(data.error || "Search failed", "error");
                elements.nlResultsGrid.innerHTML = `<div style="grid-column: 1 / -1; text-align: center; color: #f87171;">${data.error}</div>`;
                return;
            }

            elements.nlQueryTokensBadge.textContent = `Tokens: ${data.processed_query}`;

            if (!data.results.length) {
                elements.nlResultsGrid.innerHTML = `
                    <div style="grid-column: 1 / -1; text-align: center; padding: 3rem; color: var(--text-muted);">
                        No strong semantic matches found for this query. Try adding more descriptive keywords!
                    </div>
                `;
                return;
            }

            elements.nlResultsGrid.innerHTML = data.results.map(m => {
                const termsHtml = m.matched_terms && m.matched_terms.length > 0
                    ? `<div class="shared-tokens-block">
                         <span class="shared-tokens-label">Matched Query Words:</span>
                         <div class="shared-tokens-list">
                           ${m.matched_terms.map(w => `<span class="token-pill">${w}</span>`).join("")}
                         </div>
                       </div>`
                    : "";

                return `
                    <div class="movie-card" data-id="${m.id}">
                        <div class="poster-container">
                            <img 
                                src="${m.poster_url}" 
                                alt="${m.title} Poster" 
                                loading="lazy" 
                                onerror="handlePosterError(this, '${m.title}', '${m.genre}')"
                            >
                            <div class="rating-badge">
                                <span class="star-icon">★</span> ${m.rating}
                            </div>
                            <div class="year-badge">${m.year}</div>
                            <div class="similarity-badge high">
                                <span>🧠</span> ${m.relevance_score}% Relevance
                            </div>
                        </div>
                        <div class="movie-info">
                            <div class="genre-tag">${m.genre}</div>
                            <h4 class="movie-title">${m.title}</h4>
                            <p class="movie-director">Dir: <strong>${m.director}</strong></p>
                            <p class="movie-plot">${m.description}</p>
                            ${termsHtml}
                            <div class="card-actions">
                                <button class="btn btn-sm btn-outline" onclick="openMovieDetails(${m.id})">Details</button>
                                <button class="btn btn-sm btn-primary" onclick="recommendFromCatalog('${m.title}')">Find Similar</button>
                            </div>
                        </div>
                    </div>
                `;
            }).join("");

            showToast(`Found ${data.count} semantically matching movies!`);

        } catch (error) {
            console.error("Error in natural language search:", error);
            showToast("Search failed.", "error");
        } finally {
            elements.btnNlSearch.disabled = false;
            elements.btnNlSearch.innerHTML = `<span class="btn-icon">🔍</span> Search Semantically`;
        }
    }

    elements.btnNlSearch.addEventListener("click", () => {
        searchNaturalLanguage(elements.nlQueryInput.value);
    });

    elements.btnClearNl.addEventListener("click", () => {
        elements.nlQueryInput.value = "";
        elements.nlResultsGrid.innerHTML = "";
        elements.nlResultsHeader.style.display = "none";
    });

    elements.sampleChips.forEach(chip => {
        chip.addEventListener("click", () => {
            elements.nlQueryInput.value = chip.dataset.query;
            searchNaturalLanguage(chip.dataset.query);
        });
    });

    // =========================================================================
    // 6. Catalog Filtering & Exploration
    // =========================================================================
    function applyCatalogFilters() {
        const query = elements.catalogSearch.value.trim().toLowerCase();
        const genre = elements.genreFilter.value;
        const director = elements.directorFilter.value;
        const minRating = parseFloat(elements.minRatingRange.value);
        const sortBy = elements.sortBySelect.value;

        elements.ratingValue.textContent = minRating.toFixed(1);

        let filtered = state.allMovies.filter(m => {
            // Text search
            if (query) {
                const matchesText = m.title.toLowerCase().includes(query) ||
                                    m.description.toLowerCase().includes(query) ||
                                    m.director.toLowerCase().includes(query);
                if (!matchesText) return false;
            }

            // Genre filter
            if (genre !== "all" && !m.genre.toLowerCase().includes(genre.toLowerCase())) {
                return false;
            }

            // Director filter
            if (director !== "all" && m.director !== director) {
                return false;
            }

            // Rating filter
            if (m.rating < minRating) {
                return false;
            }

            return true;
        });

        // Sorting
        if (sortBy === "rating") {
            filtered.sort((a, b) => b.rating - a.rating);
        } else if (sortBy === "year") {
            filtered.sort((a, b) => b.year - a.year);
        } else if (sortBy === "title") {
            filtered.sort((a, b) => a.title.localeCompare(b.title));
        }

        renderCatalogCards(filtered);
        elements.catalogCount.textContent = `Showing ${filtered.length} of ${state.allMovies.length} movies`;
    }

    function renderCatalogCards(movies) {
        if (!movies.length) {
            elements.catalogGrid.innerHTML = `
                <div style="grid-column: 1 / -1; text-align: center; padding: 4rem; color: var(--text-muted);">
                    No movies match the selected filters.
                </div>
            `;
            return;
        }

        elements.catalogGrid.innerHTML = movies.map(m => `
            <div class="movie-card" data-id="${m.id}">
                <div class="poster-container">
                    <img 
                        src="${m.poster_url}" 
                        alt="${m.title} Poster" 
                        loading="lazy" 
                        onerror="handlePosterError(this, '${m.title}', '${m.genre}')"
                    >
                    <div class="rating-badge">
                        <span class="star-icon">★</span> ${m.rating}
                    </div>
                    <div class="year-badge">${m.year}</div>
                </div>
                <div class="movie-info">
                    <div class="genre-tag">${m.genre}</div>
                    <h4 class="movie-title">${m.title}</h4>
                    <p class="movie-director">Dir: <strong>${m.director}</strong></p>
                    <p class="movie-plot">${m.description}</p>
                    <div class="card-actions">
                        <button class="btn btn-sm btn-outline" onclick="openMovieDetails(${m.id})">Details</button>
                        <button class="btn btn-sm btn-primary" onclick="recommendFromCatalog('${m.title}')">Find Similar</button>
                    </div>
                </div>
            </div>
        `).join("");
    }

    elements.catalogSearch.addEventListener("input", () => {
        clearTimeout(state.debounceTimer);
        state.debounceTimer = setTimeout(applyCatalogFilters, 250);
    });

    elements.genreFilter.addEventListener("change", applyCatalogFilters);
    elements.directorFilter.addEventListener("change", applyCatalogFilters);
    elements.minRatingRange.addEventListener("input", applyCatalogFilters);
    elements.sortBySelect.addEventListener("change", applyCatalogFilters);

    window.recommendFromCatalog = (title) => {
        elements.movieInput.value = title;
        switchTab("recommender");
        fetchRecommendations(title);
        window.scrollTo({ top: 0, behavior: "smooth" });
    };

    // =========================================================================
    // 7. Interactive NLP Pipeline Visualizer
    // =========================================================================
    window.inspectNlp = async (textOrTitle) => {
        const text = textOrTitle || elements.visualizerInput.value.trim();
        if (!text) return;

        elements.visualizerInput.value = text;
        switchTab("nlp-visualizer");

        elements.step1Output.textContent = "Loading NLP metadata soup...";
        elements.step2Output.textContent = "Cleaning text...";

        try {
            const response = await fetch("/api/explain", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ text }),
            });

            const result = await response.json();
            if (!result.success) {
                showToast("NLP explanation failed.", "error");
                return;
            }

            const data = result.data;

            // Step 1: Raw / Soup
            elements.step1Output.textContent = data.raw_text;

            // Step 2: Cleaned
            elements.step2Output.textContent = data.cleaned_text;

            // Step 3: Tokens (Filtered vs Stopwords)
            elements.keptTokensCount.textContent = data.filtered_tokens_count;
            elements.removedTokensCount.textContent = data.removed_stopwords_count;

            elements.keptTokens.innerHTML = data.filtered_tokens.map(t => `
                <span class="token-chip">${t}</span>
            `).join("");

            elements.removedTokens.innerHTML = data.removed_stopwords.map(t => `
                <span class="token-chip">${t}</span>
            `).join("");

            // Step 4: Stemming transformations
            if (data.stem_transformations && data.stem_transformations.length > 0) {
                elements.stemTransformations.innerHTML = data.stem_transformations.map(s => `
                    <div class="stem-card">
                        <span class="stem-orig">${s.original}</span>
                        <span class="stem-arrow">&rarr;</span>
                        <span class="stem-result">${s.stemmed}</span>
                    </div>
                `).join("");
            } else {
                elements.stemTransformations.innerHTML = `
                    <div style="grid-column: 1 / -1; color: var(--text-muted); font-size: 0.85rem;">
                        All words in this segment are already in their root/stem forms.
                    </div>
                `;
            }

            // Step 5: TF-IDF feature weights
            if (data.top_tfidf_features && data.top_tfidf_features.length > 0) {
                const maxWeight = Math.max(...data.top_tfidf_features.map(f => f.weight));
                elements.tfidfBars.innerHTML = data.top_tfidf_features.map(f => {
                    const widthPercent = (f.weight / maxWeight) * 100;
                    return `
                        <div class="tfidf-bar-item">
                            <span class="tfidf-term" title="${f.term}">${f.term}</span>
                            <div class="tfidf-bar-track">
                                <div class="tfidf-bar-fill" style="width: ${widthPercent}%;"></div>
                            </div>
                            <span class="tfidf-weight">${f.weight.toFixed(4)}</span>
                        </div>
                    `;
                }).join("");
            } else {
                elements.tfidfBars.innerHTML = `
                    <div style="color: var(--text-muted); font-size: 0.85rem;">
                        No strong vocabulary matches found in the trained TF-IDF corpus.
                    </div>
                `;
            }

            showToast("NLP Pipeline updated successfully!");

        } catch (error) {
            console.error("Error inspecting NLP pipeline:", error);
            showToast("Error retrieving NLP explanation.", "error");
        }
    };

    elements.btnInspectNlp.addEventListener("click", () => {
        inspectNlp(elements.visualizerInput.value.trim());
    });

    // =========================================================================
    // 8. Movie Details Modal
    // =========================================================================
    window.openMovieDetails = (movieId) => {
        const movie = state.allMovies.find(m => m.id === movieId);
        if (!movie) return;

        elements.modalContent.innerHTML = `
            <div class="modal-movie-layout">
                <img 
                    src="${movie.poster_url}" 
                    alt="${movie.title}" 
                    class="modal-poster"
                    onerror="handlePosterError(this, '${movie.title}', '${movie.genre}')"
                >
                <div class="modal-details">
                    <h2>${movie.title} <span style="font-size: 1.2rem; color: var(--text-muted);">(${movie.year})</span></h2>
                    <div class="modal-meta-row">
                        <span class="genre-tag">${movie.genre}</span>
                        <span>&bull;</span>
                        <span>Directed by <strong>${movie.director}</strong></span>
                        <span>&bull;</span>
                        <span style="color: #f59e0b; font-weight: 700;">★ ${movie.rating}/10</span>
                    </div>

                    <div class="modal-plot-title">Plot Overview</div>
                    <p class="modal-plot-text">${movie.description}</p>

                    <div class="modal-nlp-tokens">
                        <span class="modal-nlp-tokens-label">NLP Preprocessed Tags (Stemmed / Normalized):</span>
                        <div style="font-size: 0.82rem; color: #38bdf8; word-break: break-word; font-family: monospace;">
                            ${movie.nlp_tags}
                        </div>
                    </div>

                    <div style="display: flex; gap: 1rem;">
                        <button class="btn btn-primary" onclick="recommendFromCatalog('${movie.title}'); closeModal();">
                            ⚡ Find Similar Movies
                        </button>
                        <button class="btn btn-outline" onclick="inspectNlp('${movie.title}'); closeModal();">
                            🧪 Inspect in Pipeline
                        </button>
                    </div>
                </div>
            </div>
        `;

        if (elements.movieModal.showModal) {
            elements.movieModal.showModal();
        } else {
            elements.movieModal.setAttribute("open", "true");
        }
    };

    window.closeModal = () => {
        if (elements.movieModal.close) {
            elements.movieModal.close();
        } else {
            elements.movieModal.removeAttribute("open");
        }
    };

    // =========================================================================
    // 9. Toast Notification Utility
    // =========================================================================
    let toastTimeout = null;
    function showToast(message, type = "info") {
        if (!elements.toast) return;
        clearTimeout(toastTimeout);

        const icon = type === "error" ? "⚠️" : type === "warning" ? "🔔" : "✨";
        elements.toast.innerHTML = `<span>${icon}</span> <span>${message}</span>`;
        elements.toast.classList.remove("hidden");

        toastTimeout = setTimeout(() => {
            elements.toast.classList.add("hidden");
        }, 3200);
    }

    // =========================================================================
    // 10. Initial Run
    // =========================================================================
    // Automatically run recommendations for initial default movie (Interstellar)
    fetchRecommendations("Interstellar");
});
