async function searchArticles(event) {
    event.preventDefault();
    
    const submitButton = event.target.querySelector('button[type="submit"]');
    const spinner = submitButton.querySelector('.loading-spinner');
    
    elements.search.results.innerHTML = '';
    elements.search.error.style.display = 'none';
    submitButton.disabled = true;
    spinner.style.display = 'inline-block';
    
    try {
        const response = await fetch(`/api/search/content?query=${encodeURIComponent(elements.search.input.value)}`);
        if (!response.ok) throw new Error(`Error: ${response.statusText}`);
        
        const articles = await response.json();
        renderSearchResults(articles, elements.search.results);
    } catch (error) {
        elements.search.error.textContent = error.message;
        elements.search.error.style.display = 'block';
    } finally {
        submitButton.disabled = false;
        spinner.style.display = 'none';
    }
}

function renderSearchResults(articles, container) {
    if (articles.length === 0) {
        container.innerHTML = '<div class="alert alert-info">No content found.</div>';
        return;
    }
    
    container.innerHTML = articles.map(article => {
        const articleTopics = article.topics.map(topic => {
            const isActive = state.activeTags.has(topic);
            return `
                <button class="badge topic-badge ${isActive ? 'active' : ''}"
                        onclick="searchByTopic('${topic}')"
                        title="${isActive ? 'Remove tag' : 'Add tag'}">${topic}</button>
            `;
        }).join('');

        return `
            <div class="card mb-3">
                <div class="card-body">
                    <h6 class="card-title">${article.title}</h6>
                    <p class="card-text small">${article.summary}</p>
                    <div class="d-flex justify-content-between align-items-center">
                        <div class="d-flex flex-wrap gap-1">
                            ${articleTopics}
                        </div>
                        <div class="d-flex align-items-center gap-2">
                            <small class="text-muted">
                                <i class="bi bi-clock"></i> ${article.reading_time} min
                            </small>
                            <a href="${article.url}" target="_blank" class="btn btn-sm btn-outline-primary">Read</a>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }).join('');
} 