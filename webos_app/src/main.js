import Vue from 'vue'
import App from './App.vue'
import vuemqtt from 'vue-mqtt'
import vuetify from './plugins/vuetify';
import './registerServiceWorker'

Vue.config.productionTip = false
Vue.use(vuemqtt, 'ws://test.mosquitto.org:8080/mqtt', {});

new Vue({
  vuetify,
  render: h => h(App)
}).$mount('#app')
