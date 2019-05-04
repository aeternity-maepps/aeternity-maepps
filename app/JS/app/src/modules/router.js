import Router from 'vue-router';
import Vue from 'vue';
import Home from '../components/Home/Home';
import PageNotFound from '../components/PageNotFound';
import SignUp from '../components/SignUp/SignUp';
import ActivationPage from '../components/SignUp/ActivationPage';
import EditableaeventInfo from '../components/Editing/EditableaeventInfo';
import EditableaembassadorInfo from '../components/Editing/EditableaembassadorInfo';

Vue.use(Router);

const routes = [
  { path: '/', name: 'home', component: Home },
  { path: '/sign-up', name: 'signup', component: SignUp },
  { path: '/users/:id/activate', name: 'activate', component: ActivationPage },
  { path: '/aevent/:aevent_id', name: 'EditableaeventInfo', component: EditableaeventInfo },
  { path: '/aevents/:aevent_id', name: 'EditableaembassadorInfo', component: EditableaembassadorInfo },
  
  // catch all route
  { path: '*', component: PageNotFound }
];

export default new Router({
  mode: 'history',
  routes: routes
});