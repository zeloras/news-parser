// Content processing
async function processUrls(event) {
    event.preventDefault();
    
    const submitButton = event.target.querySelector('button[type="submit"]');
    const spinner = submitButton.querySelector('.loading-spinner');
    const urlsText = elements.process.urls.value.trim();
    
    elements.process.results.style.display = 'none';
    elements.process.error.style.display = 'none';
    elements.process.contentList.innerHTML = '';
    submitButton.disabled = true;
    spinner.style.display = 'inline-block';
    
    try {
        // Parse URLs
        const urls = urlsText.split('\n')
            .map(url => url.trim())
            .filter(url => url && url.startsWith('http'));
            
        if (urls.length === 0) {
            throw new Error('Please enter at least one valid URL');
        }
        
        // Prepare request body
        const body = urls.length === 1 
            ? { url: urls[0] }
            : { urls: urls };
        
        const response = await fetch('/api/content/process', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || `Error: ${response.statusText}`);
        }
        
        const data = await response.json();
        const contents = Array.isArray(data) ? data : [data];
        
        // Render results
        contents.forEach(content => renderContent(content));
        elements.process.results.style.display = 'block';
        
    } catch (error) {
        elements.process.error.textContent = error.message;
        elements.process.error.style.display = 'block';
    } finally {
        submitButton.disabled = false;
        spinner.style.display = 'none';
    }
}

function renderContent(content) {
    const template = document.querySelector('#contentTemplate');
    const contentElement = template.content.cloneNode(true);
    
    // Set content data
    contentElement.querySelector('.content-title').textContent = content.title;
    contentElement.querySelector('.reading-time-value').textContent = content.reading_time;
    
    const sourceLink = contentElement.querySelector('.content-source');
    sourceLink.href = content.url;
    sourceLink.querySelector('small').textContent = content.source;
    
    contentElement.querySelector('.content-summary').textContent = content.summary;
    
    // Render topics
    const topicsContainer = contentElement.querySelector('.content-topics');
    topicsContainer.innerHTML = content.topics
        .map(topic => `<button class="badge topic-badge" onclick="searchByTopic('${topic}')">${topic}</button>`)
        .join('');
    
    // Update sentiment
    const sentimentContainer = contentElement.querySelector('.content-sentiment');
    const sentimentIcon = sentimentContainer.querySelector(`.sentiment-${content.sentiment}`);
    sentimentContainer.querySelector('.sentiment-value').textContent = content.sentiment;
    
    if (sentimentIcon) {
        sentimentIcon.style.display = 'inline-block';
    }
    
    // Add to results
    elements.process.contentList.appendChild(contentElement);
} 