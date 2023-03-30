import Vue from 'vue';
import store from './store';
import App from './App.vue';

import createApp, {
  Card,
  Pad,
  Tab,
  Tabs,
} from '@cloudblueconnect/connect-ui-toolkit';

import copy from 'vue-clipboard2';


Vue.use(copy);

createApp({
  'c-card': Card,
  'c-tabs': Tabs,
  'c-tab': Tab,
  'c-pad': Pad,
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
