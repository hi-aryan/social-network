class FlashCard {
  constructor(id = 'flash-overlay') {
    this.overlay = document.getElementById(id);
    if (!this.overlay) return;
    this.card     = this.overlay.querySelector('.card-flash');
    this.closeBtn = this.overlay.querySelector('#flash-close');
    this.autoCloseTimer = null;
    this.init();
  }
  init() {
    this.closeBtn.addEventListener('click', ()=> this.close());
    this.overlay.addEventListener('click', e => {
      if (e.target === this.overlay) this.close();
    });
    // Auto-close after 5 seconds
    this.autoCloseTimer = setTimeout(() => this.close(), 6000);
  }
  close() {
    // Clear timer if manually closed
    if (this.autoCloseTimer) {
      clearTimeout(this.autoCloseTimer);
      this.autoCloseTimer = null;
    }
    this.overlay.classList.add('closing');
    this.card.classList.add('closing');
    this.card.addEventListener('animationend', ()=> {
      this.overlay.remove();
    }, { once: true });
  }
}
function startFlashCard() {
  new FlashCard();
}
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', startFlashCard);
} else {
  startFlashCard();
}