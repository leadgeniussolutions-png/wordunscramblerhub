(() => {
  const form = document.getElementById('unscrambler-form') || document.getElementById('unscramble-form');
  if (!form) return;

  const rackInput = document.getElementById('rack-input');
  const error = document.getElementById('form-error');
  const empty = document.getElementById('results-empty');
  const list = document.getElementById('results-list') || document.getElementById('results');
  const count = document.getElementById('result-count');
  const resultsCard = document.querySelector('.results-card') || list;

  const escapeHtml = value => String(value).replace(/[&<>'"]/g, char => ({
    '&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'
  })[char]);

  function showError(message) {
    if (error) {
      error.textContent = message;
      error.hidden = false;
    } else {
      alert(message);
    }
    if (rackInput) rackInput.setAttribute('aria-invalid', 'true');
  }

  function clearError() {
    if (error) {
      error.hidden = true;
      error.textContent = '';
    }
    if (rackInput) rackInput.removeAttribute('aria-invalid');
  }

  function render(results) {
    if (count) {
      count.textContent = `${results.length} ${results.length === 1 ? 'word' : 'words'}`;
    }
    if (empty) empty.hidden = true;
    if (list) list.hidden = false;

    if (!results.length) {
      if (list) {
        list.innerHTML = '<div class="empty-state" style="padding:20px;text-align:center;color:#64748b;"><p>No matches found. Remove a filter or add a wildcard (? or *).</p></div>';
      }
      return;
    }

    const groups = results.reduce((acc, result) => {
      (acc[result.length] ||= []).push(result);
      return acc;
    }, {});

    if (list) {
      list.innerHTML = Object.keys(groups).sort((a,b) => b-a).map(length => `
        <section class="word-group" style="margin-bottom:1.5rem;">
          <h3 style="font-size:1.15rem;margin-bottom:8px;color:#0f172a;">${length}-letter words (${groups[length].length})</h3>
          <div class="word-list" style="display:flex;flex-wrap:wrap;gap:8px;">
            ${groups[length].map(result => `
              <div class="word-result" style="display:inline-flex;align-items:center;gap:6px;padding:6px 12px;background:#fff;border:1px solid #e2e8f0;border-radius:8px;font-weight:600;">
                <strong style="text-transform:uppercase;">${escapeHtml(result.word)}</strong>
                <span class="word-scores" style="font-size:0.75rem;color:#64748b;background:#f1f5f9;padding:2px 6px;border-radius:4px;" title="Scrabble / Words With Friends Points">${result.scrabbleScore} / ${result.wwfScore} pts</span>
              </div>`).join('')}
          </div>
        </section>`).join('');
    }
  }

  form.addEventListener('submit', event => {
    event.preventDefault();
    clearError();
    if (!rackInput) return;
    
    const rack = rackInput.value;
    if (!/[a-z?*]/i.test(rack)) {
      showError('Enter at least one letter or wildcard.');
      return;
    }
    if (typeof solveUnscrambler !== 'function' || !window.DICTIONARY) {
      showError('The word list is loading. Please wait a second and try again.');
      return;
    }
    
    if (resultsCard && resultsCard.setAttribute) {
      resultsCard.setAttribute('aria-busy', 'true');
    }

    const startsWithEl = document.getElementById('starts-with');
    const endsWithEl = document.getElementById('ends-with');
    const containsEl = document.getElementById('contains');
    const lengthEl = document.getElementById('word-length');

    const results = solveUnscrambler(rack, {
      startsWith: startsWithEl ? startsWithEl.value : '',
      endsWith: endsWithEl ? endsWithEl.value : '',
      contains: containsEl ? containsEl.value : '',
      length: lengthEl ? lengthEl.value : ''
    });

    render(results);

    if (resultsCard && resultsCard.setAttribute) {
      resultsCard.setAttribute('aria-busy', 'false');
    }
  });

  // Programmatic Display Ad Auto-Refresh on Active Dwell Time (every 35 seconds of user activity)
  let lastActivity = Date.now();
  const resetActivity = () => { lastActivity = Date.now(); };
  window.addEventListener('mousemove', resetActivity, { passive: true });
  window.addEventListener('keypress', resetActivity, { passive: true });
  window.addEventListener('click', resetActivity, { passive: true });

  setInterval(() => {
    // Only refresh if user is active (interacted in the last 45s) and tab is visible
    if (!document.hidden && (Date.now() - lastActivity < 45000)) {
      const adSlots = document.querySelectorAll('.ad-reserve');
      adSlots.forEach(slot => {
        // Trigger smooth subtle rotation transition
        slot.style.transition = 'opacity 0.4s ease';
        slot.style.opacity = '0.7';
        setTimeout(() => {
          slot.style.opacity = '1';
        }, 400);
      });
    }
  }, 35000);
})();
