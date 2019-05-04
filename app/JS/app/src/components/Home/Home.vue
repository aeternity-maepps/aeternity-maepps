<template>
  <div class="home-page">

    <!-- sidebar -->
    <sidebar ref="sidebar" @toggled="handleExpand">

      <!-- slot for sidebar content -->
      <typeahead v-if="menuActive" />

      <keep-alive>

        <!-- Aevent IDENTIFY CONTENT -->
        <aevent-info
                v-if="identifyActive"
                :userIsAuthenticated="userIsAuthenticated"
                :feature="selectedaevent">
        </aevent-info>

      </keep-alive>

    </sidebar>

    <!-- MAP VIEW-->
    <map-view
            ref="mapView"
            :userIsAuthenticated="userIsAuthenticated"
            @clicked-add-aevent="handleAddaevent"
            @new-aevent-point="createNewaevent"
            @add-aevent-cancelled="deactivateAddaevent"
            @toggle-identify="identifyActivePanel"
            @cleared-selection="clearSelection"
            @aevent-identified="showaeventInfo"
            @toggle-menu="menuActivePanel">
    </map-view>

    
  </div>
</template>

<script>
  import MapView from './MapViewMglv';
  import Sidebar from './Sidebar';
  import aeventInfo from './aeventInfo';
  import Typeahead from './Typeahead';
  import swal from 'sweetalert2';
  import api from '../../modules/api';
  import  { EventBus } from '../../modules/EventBus';
  import enums from '../../modules/enums';

  export default {
    name: "home",
    components: {
      MapView,
      Sidebar,
      aeventInfo,
      Typeahead
    },

    data(){
      return {
        selectedaevent: null,
        menuActive: true,
        identifyActive: false,
        addaeventActive: false,
        sidebarActive: false,
        newaeventPoint: null,
        userIsAuthenticated: false
      }
    },

    mounted(){
      console.log('MOUNTED HOME COMPONENT!');
      console.log('ref to map view: ', this.$refs.mapView);

      // need to manually update this, because feature returned from map click is not
      // the original object
      EventBus.$on('aevent-changed', async (obj)=>{
        console.log('aevent-change! ', obj)

        if (this.selectedaevent && obj.id === this.selectedaevent.properties.id){
          if (obj.type === 'delete'){
            this.clearSelection();
          } else {
            const resp = await api.getaevent(obj.id, { f: 'geojson' });
            if (resp.features.length){
              // update aevent
              Object.assign(this.selectedaevent, resp.features[0]);
            }
          }
        }
        if (obj.type === 'create'){
          this.deactivateAddaevent();
        }
      });
    },

    methods: {

      showaeventInfo(aevent){
        // force panel to open with identify active
        this.selectedaevent = aevent;
        if (aevent){
          this.$refs.sidebar.expand();
          this.menuActive = false;
          this.identifyActive = true;
        }
      },

      clearSelection(){
        this.selectedaevent = null;
        if (this.identifyActive){
          this.$refs.sidebar.collapse();
        }
      },

       menuActivePanel(){
        // if identify is shown, toggle on menu
        this.sidebarActive = this.$refs.sidebar.active;
        if (this.identifyActive && this.$refs.sidebar.active){
          this.identifyActive = false;
          this.menuActive = true;
        } else {
          this.identifyActive = false;
          this.menuActive = true;
          this.$refs.sidebar.toggle();
        }
      },

      identifyActivePanel(){
        this.sidebarActive = this.$refs.sidebar.active;
        if (this.menuActive && this.$refs.sidebar.active){
          this.menuActive = false;
          this.identifyActive = true;
        } else {
          this.menuActive = false;
          this.identifyActive = true;
          this.$refs.sidebar.toggle();
        }
      },
      handleAddaevent(){
        this.addaeventActive = true;
        this.activateButton('.add-aevent');
      },

      deactivateAddaevent(){
        const btn = document.querySelector('.add-aevent');
        btn ? btn.classList.remove('control-btn-active'): null;
        this.addaeventActive = false;
        this.$refs.mapView.deactivateAddaevent();
      },


      async createNewaevent(point){

        swal({
          title: 'Create New aevent',
          input: 'text',
          showCancelButton: true,
          confirmButtonText: 'Create',
          confirmButtonColor: 'forestgreen',
          showLoaderOnConfirm: true,
          allowOutsideClick: ()=> !swal.isLoading(),
          preConfirm: async (name)=> {
            const lat = point.lat;
            const lng = point.lng;

            // fetch access token from root vue instance "config" prop
            const accessToken = this.$root.config.map.accessToken;
            const params = await api.maboxReverseGeocode(lat, lng, accessToken);

            // add x,y coords
            params.x = point.lng;
            params.y = point.lat;

            // add aevent name to params and create new aevent
            params.name = name;
            const resp = await api.createItem('aevents', params);

            // notify new aevent has been created
            EventBus.$emit('aevent-change', {
              id: resp.id,
              type: 'create'
            });

            this.deactivateAddaevent();
            return resp;
          }
        }).then((res)=> {
          const newaeventId = res.value.id;
          this.emitaeventChange(newaeventId, 'create');
          swal({
            title: 'Success',
            text: 'successfully created new aevent',
            confirmButtonText: 'Go To New aevent',
            cancelButtonText: 'Stay Here',
            showCancelButton: true
          }).then((res)=>{
            res.value ? this.goToEditaevent(newaeventId): null;
          });

        }).catch(err =>{
          console.log('error creating aevent: ', err);
          swal({
            type: 'error',
            title: 'Unable to Create aevent',
            text: "please make sure you're logged in to make this change"
          })
        });

      },

      goToEditaevent(id){
        // open editable aevent page and pass in the aevent id
        this.$router.push({ name: 'editableaeventInfo', params: { aevent_id: id }})
      },

      emitaeventChange(id, type){
        EventBus.$emit('aevent-changed', {
          id: id,
          type: type
        })
      },

      // Below methods are not what we normally do in Vue.js, things are done 
      // with vanilla js to interact with elements within the Mapboxgl canvas container
      handleExpand(expanded){
        // listen for sidebar to open and update move map's left position
        const map = document.querySelector('#map');
        if (map){
          map.style.left = `${expanded ? 350: 0}px`;
        }
        
        if (!expanded){
          this.clearActiveButtons();
        } else {
          this.activateButton(`.expand-${this.menuActive ? 'menu': 'identify'}`)
        }
      },

      clearActiveButtons(){
        const active = document.querySelectorAll('.control-btn-active:not(.add-aevent)');
        active.forEach(e => e.classList.remove('control-btn-active'));
      },

      activateButton(selector){
        // Normally do not have to do things like this in Vue
        this.clearActiveButtons();
        const btn = document.querySelector(selector);
        if (this.$refs.sidebar.active){
          if (!btn.classList.contains('control-btn-active')){
            btn.classList.add('control-btn-active');
          } else {
            btn.classList.remove('control-btn-active');
          }
        } else {
          // check if it is add aevent button
          if (selector === '.add-aevent'){
            console.log('it is add aevent button!')
            btn.classList.add('control-btn-active');
          }
        }
      }
    },
    
    watch: {

      menuActive(newVal){
        // handle state when panel is already open, and switched from identify to menu
        if (newVal){
          this.activateButton('.expand-menu');
        }
      },

      identifyActive(newVal){
        // handle state when panel is already open, and switched from menu to identify
        if (newVal){
          this.activateButton('.expand-identify');
        }
      },

      '$root.userIsAuthenticated'(newVal){
        this.userIsAuthenticated = newVal;
      }
    }
  }
</script>