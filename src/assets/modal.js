// Modal logic for keyword explanations
const KEYWORDS = {};

fetch('/assets/keywords.json')
  .then(res => res.json())
  .then(data => Object.assign(KEYWORDS, data));

function showKeywordModal(keyword) {
  const info = KEYWORDS[keyword.toLowerCase()];
  if (!info) return;
  let modal = document.getElementById('keyword-modal');
  if (!modal) {
    modal = document.createElement('div');
    modal.id = 'keyword-modal';
    modal.innerHTML = `
      <div class="modal-backdrop"></div>
      <div class="modal-content">
        <button class="modal-close" aria-label="Close">&times;</button>
        <h3 id="modal-title"></h3>
        <div id="modal-body"></div>
      </div>
    `;
    document.body.appendChild(modal);
    modal.querySelector('.modal-close').onclick = closeKeywordModal;
    modal.querySelector('.modal-backdrop').onclick = closeKeywordModal;
  }
  modal.querySelector('#modal-title').innerHTML = info.title;
  modal.querySelector('#modal-body').innerHTML = info.content;
  modal.classList.add('open');
}

function closeKeywordModal() {
  const modal = document.getElementById('keyword-modal');
  if (modal) modal.classList.remove('open');
}

document.addEventListener('click', function(e) {
  if (e.target.classList.contains('keyword-link')) {
    e.preventDefault();
    showKeywordModal(e.target.dataset.keyword);
  }
});
