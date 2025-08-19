class FlashCard {
  constructor(id = 'flash-overlay') {
    this.overlay = document.getElementById(id);
    if (!this.overlay) return;
    this.card     = this.overlay.querySelector('.card-flash');
    this.closeBtn = this.overlay.querySelector('#flash-close');
    this.init();
  }
  init() {
    this.closeBtn.addEventListener('click', ()=> this.close());
    this.overlay.addEventListener('click', e => {
      if (e.target === this.overlay) this.close();
    });
  }
  close() {
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