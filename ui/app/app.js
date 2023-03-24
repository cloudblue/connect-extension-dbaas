import Vue from 'vue';
import store from './store';
import App from './App.vue';

import createApp, {
  Card,
} from '@cloudblueconnect/connect-ui-toolkit';


createApp({
  'ui-card': Card,
}).then(connectBus => {
  store.registerModule('bus', {
    namespaced: true,

    actions: {
      emit(o, { name, value }) {
        connectBus.emit(name, value);
      },
    },
  });

  const app = new Vue({
    store,

    render: h => h(App),
  });

  app.$mount('#app');
});
