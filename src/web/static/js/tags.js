async function loadAvailableTags() {
    try {
        const response = await fetch('/api/search/content?query=*');
        if (!response.ok) throw new Error('Failed to load tags');
        
        const articles = await response.json();
        articles.forEach(article => {
            article.topics.forEach(topic => state.allTags.add(topic));
        });
        
        renderAvailableTags();
    } catch (error) {
        console.error('Failed to load tags:', error);
    }
}

function renderAvailableTags() {
    elements.tags.available.innerHTML = Array.from(state.allTags)
        .map(tag => `
            <button class="badge topic-badge ${state.activeTags.has(tag) ? 'active' : ''}"
                    onclick="toggleTag('${tag}')">${tag}</button>
        `).join('');
}

function renderActiveTags() {
    if (state.activeTags.size === 0) {
        elements.tags.active.innerHTML = '<small class="text-muted">No tags selected</small>';
        return;
    }
    
    elements.tags.active.innerHTML = Array.from(state.activeTags)
        .map(tag => `
            <button class="badge topic-badge active me-2"
                    onclick="toggleTag('${tag}')">${tag}</button>
        `).join('') + 
        '<span class="clear-tags" onclick="clearTags()">Clear all</span>';
}

async function toggleTag(tag) {
    if (state.activeTags.has(tag)) {
        state.activeTags.delete(tag);
    } else {
        state.activeTags.add(tag);
    }
    
    renderActiveTags();
    renderAvailableTags();
    
    if (state.activeTags.size > 0) {
        await searchByTags(Array.from(state.activeTags));
    } else {
        elements.tags.results.innerHTML = '';
    }
}

function clearTags() {
    state.activeTags.clear();
    renderActiveTags();
    renderAvailableTags();
    elements.tags.results.innerHTML = '';
}

async function searchByTags(tags) {
    elements.tags.results.innerHTML = '<div class="text-center"><div class="spinner-border" role="status"></div></div>';
    elements.tags.error.style.display = 'none';
    
    try {
        // Combine all tags into a single search query
        const query = tags.join(' ');
        const response = await fetch(`/api/search/content?query=${encodeURIComponent(query)}`);
        
        if (!response.ok) throw new Error(`Error: ${response.statusText}`);
        
        const articles = await response.json();
        
        if (articles.length === 0) {
            elements.tags.results.innerHTML = '<div class="alert alert-info">No content found with selected tags.</div>';
        } else {
            renderSearchResults(articles, elements.tags.results);
        }
    } catch (error) {
        elements.tags.error.textContent = error.message;
        elements.tags.error.style.display = 'block';
        elements.tags.results.innerHTML = '';
    }
}

async function searchByTopic(topic) {
    document.querySelector('[data-section="tags"]').click();
    if (!state.activeTags.has(topic)) {
        await toggleTag(topic);
    }
} 