import { createApp } from 'vue';
import router from './router';

import App from './App.vue';
import bootstrap from '@/bootstrap';
import envModel from './models/env.model';

// Self-Initing services
import isMobile from '@/services/isMobile.service';
import '@/services/VHFix.service';

import UIcon from '@/components/ui/UIcon.vue';
import { ColorSchemeDirective } from '@/directives/ColorScheme.directive';
import FormatterPipe from '@/pipes/Formatter.pipe';

(async () => {

  await bootstrap();
  
  const app = createApp(App);

  app.use(router)
  .component('UIcon', UIcon)
  .directive('colorBy', ColorSchemeDirective)
  
  app.config.globalProperties.$format = FormatterPipe;
  app.config.globalProperties.$env = envModel;
  app.config.globalProperties.$isMobile = isMobile;

  
  app.mount('#app');

})();