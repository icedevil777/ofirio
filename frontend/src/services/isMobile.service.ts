import { readonly, ref } from 'vue';
import envModel from '@/models/env.model';

function watchOnceChanged() {
  const i = setInterval(() => {
    if (window.innerWidth > 0) {
      isMobile.value = calcIsMobile();
      clearInterval(i);
    }
  }, 100);
}

function calcIsMobile () {
  if (!envModel.VUE_APP_MOBILE_WIDTH)
    return false;

  if (window.innerWidth == 0)
    watchOnceChanged();

  return window.innerWidth <= parseInt(envModel.VUE_APP_MOBILE_WIDTH);
}

let isMobile = ref(calcIsMobile());
window.addEventListener('resize', function () {
  isMobile.value = calcIsMobile();
});

export default isMobile;