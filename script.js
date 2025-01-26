// Language Switcher
document.getElementById('en-btn').addEventListener('click', () => switchLanguage('en'));
document.getElementById('de-btn').addEventListener('click', () => switchLanguage('de'));

function switchLanguage(language) {
    const elements = document.querySelectorAll('[data-en], [data-de]');

    elements.forEach(element => {
        const enText = element.getAttribute('data-en');
        const deText = element.getAttribute('data-de');

        if (language === 'en' && enText) {
            element.textContent = enText;
        } else if (language === 'de' && deText) {
            element.textContent = deText;
        }
    });
}

// Comment Submission Logic with Sentiment Analysis (AI-powered)
document.getElementById('comment-form').addEventListener('submit', function(event) {
    event.preventDefault();
    const name = document.getElementById('name').value;
    const comment = document.getElementById('comment').value;

    // Simple sentiment logic (just as a placeholder)
    const sentiment = analyzeSentiment(comment); // Example function
    const sentimentClass = sentiment === 'positive' ? 'positive-comment' : 'negative-comment';

    const commentList = document.getElementById('comments-list');
    const listItem = document.createElement('li');
    listItem.className = sentimentClass;
    listItem.innerHTML = `<strong>${name}</strong>: ${comment}`;
    commentList.appendChild(listItem);

    // Clear the form after submission
    document.getElementById('name').value = '';
    document.getElementById('comment').value = '';
});

function analyzeSentiment(comment) {
    // AI-based sentiment analysis (to be replaced by real API call)
    return comment.includes("good") ? 'positive' : 'negative';
}
