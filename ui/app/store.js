import Vuex from 'vuex';
import Vue from 'vue';


Vue.use(Vuex);

export default new Vuex.Store({
  state: {
    installationContext: {
      isAdmin: false,
    },
  },

  getters: {
    installationContext: ({ installationContext }) => installationContext,
  },

  mutations: {
    setInstallationContext(state, ctx) {
      state.installationContext = Object.assign(state.installationContext, ctx);
    },
  },
});
