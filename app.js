(() => {
  const form = document.getElementById('unscrambler-form');
  if (!form) return;

  const rackInput = document.getElementById('rack-input');
  const error = document.getElementById('form-error');
  const empty = document.getElementById('results-empty');
  const list = document.getElementById('results-list');
  const count = document.getElementById('result-count');
  const resultsCard = document.querySelector('.results-card');

  const escapeHtml = value => String(value).replace(/[&<>'"]/g, char => ({
    '&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'
  })[char]);

  function showError(message) {
    error.textContent = message;
    error.hidden = false;
    rackInput.setAttribute('aria-invalid', 'true');
  }

  function clearError() {
    error.hidden = true;
    error.textContent = '';
    rackInput.removeAttribute('aria-invalid');
  }

  function render(results) {
    count.textContent = `${results.length} ${results.length === 1 ? 'word' : 'words'}`;
    empty.hidden = true;
    list.hidden = false;

    if (!results.length) {
      list.innerHTML = '<div class="empty-state"><p>No matches found. Remove a filter or add a wildcard.</p></div>';
      return;
    }

    const groups = results.reduce((acc, result) => {
      (acc[result.length] ||= []).push(result);
      return acc;
    }, {});

    list.innerHTML = Object.keys(groups).sort((a,b) => b-a).map(length => `
      <section class="word-group">
        <h3>${length}-letter words</h3>
        <div class="word-list">
          ${groups[length].map(result => `
            <div class="word-result">
              <strong>${escapeHtml(result.word.toUpperCase())}</strong>
              <span class="word-scores" title="Scrabble / Words With Friends">${result.scrabbleScore} / ${result.wwfScore}</span>
            </div>`).join('')}
        </div>
      </section>`).join('');
  }

  form.addEventListener('submit', event => {
    event.preventDefault();
    clearError();
    const rack = rackInput.value;
    if (!/[a-z?*]/i.test(rack)) {
      showError('Enter at least one letter or wildcard.');
      return;
    }
    if (typeof solveUnscrambler !== 'function' || !window.DICTIONARY) {
      showError('The word list did not load. Refresh the page and try again.');
      return;
    }
    resultsCard.setAttribute('aria-busy', 'true');
    const results = solveUnscrambler(rack, {
      startsWith: document.getElementById('starts-with').value,
      endsWith: document.getElementById('ends-with').value,
      contains: document.getElementById('contains').value,
      length: document.getElementById('word-length').value
    });
    render(results);
    resultsCard.setAttribute('aria-busy', 'false');
  });
})();
