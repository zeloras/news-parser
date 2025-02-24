document.querySelectorAll('[data-section]').forEach(link => {
    link.addEventListener('click', (e) => {
        e.preventDefault();
        const section = link.dataset.section;
        
        document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
        link.classList.add('active');
        
        Object.entries(elements.sections).forEach(([key, element]) => {
            element.style.display = key === section ? 'block' : 'none';
        });

        if (section === 'tags' && state.allTags.size === 0) {
            loadAvailableTags();
        }
    });
}); 