const elements = {
    sections: {
        process: document.querySelector('#processSection'),
        search: document.querySelector('#searchSection'),
        tags: document.querySelector('#tagsSection')
    },
    tags: {
        active: document.querySelector('#activeTags'),
        available: document.querySelector('#availableTags'),
        results: document.querySelector('#tagSearchResults'),
        error: document.querySelector('#tagSearchError'),
        noTags: document.querySelector('#noTagsMessage')
    },
    search: {
        form: document.querySelector('#searchForm'),
        input: document.querySelector('#searchQuery'),
        results: document.querySelector('#searchResults'),
        error: document.querySelector('#searchError')
    },
    process: {
        form: document.querySelector('#processForm'),
        urls: document.querySelector('#urls'),
        results: document.querySelector('#results'),
        contentList: document.querySelector('#contentList'),
        error: document.querySelector('#error')
    }
};

const state = {
    activeTags: new Set(),
    allTags: new Set()
}; 