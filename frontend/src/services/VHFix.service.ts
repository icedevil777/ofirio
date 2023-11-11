function calcVh() {
  if (!document) return;

  (<HTMLElement>document.querySelector(':root')).style.setProperty('--vh', window.innerHeight/100 + 'px');
}

function watchOnceChanged() {
  const i = setInterval(() => {
    if (window.innerWidth > 0) {
      calcVh();
      clearInterval(i);
    }
  }, 100);
}

window.addEventListener('resize', calcVh);
if (window.innerWidth == 0)
  watchOnceChanged();
else
  calcVh();

export default undefined;