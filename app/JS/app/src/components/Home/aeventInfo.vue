<template>
  <div class="aevent-info-container">
    <b-card v-if="Object.keys(feature || {}).length">
      <span class="aevent-info-header">
        <h4><strong>{{ properties.name }}</strong></h4>
        <span class="float-right edit-btn"
              title="edit aevent info"
              @click="editaevent"
              v-show="userIsAuthenticated" >
          <font-awesome-icon prefix="fas" icon="pen" />
        </span>
      </span>

      <hr>
      <p>{{ properties.address }}</p>
      <p>{{ properties.city }}, {{ properties.state }} {{ properties.zip }}</p>
      <b-link :href="properties.website" target="_blank" v-if="properties.website">website</b-link> | 
      <b-link :href="directionsUrl" target="_blank" v-if="directionsUrl">directions</b-link>

      <!-- featured aembassadors -->
      <div v-if="featuredaembassadors.length">
        <hr>
        <h5><strong>Featured aembassadors</strong></h5>
        <b-list-group class="featured-aembassadors-container">
          <b-list-group-item v-for="aembassador in featuredaembassadors" :key="aembassador.id">
            <featured-aembassador :aembassador="aembassador"></featured-aembassador>
          </b-list-group-item>
        </b-list-group>
      </div>

    </b-card>

    <div v-else>
      <h4 class="no-features mt-4">No Features Found</h4>
    </div>

  </div>
</template>

<script>
  import { EventBus } from "../../modules/EventBus";
  import api from '../../modules/api';
  import Featuredaembassador from './Featuredaembassador';

  export default {
    name: "aevent-info",
    props: {
      feature: {
        type: Object,
        default(){
          return {
            properties: {}
          }
        }
      },
      userIsAuthenticated: false
    },
    components: {
      Featuredaembassador
    },
    data() {
      return {
        featuredaembassadors: []
      }
    },

    mounted(){
      console.log('MOUNTED aevent INFO COMPONENT: ', this);

      // load the aembassadors
      this.fetchaembassadors()

      // notify this component to reload featured aembassadors
      EventBus.$on('aembassadors-changed', (obj)=>{
        console.log('aembassadors-changed event received: ', obj);
        if (obj.aevent_id == this.properties.id){
          this.fetchaembassadors();
        }
      });
      
    },

    methods: {

      getDirectionsUrl(feature){
        const addr_parts = [feature.name, feature.address, feature.city, feature.state, feature.zip];

        // form query url for google directions, try address first if has address city st zip else use x,y
        const dest = addr_parts.every(f => !!f) ? addr_parts.join(' ').replace(/\s/g, '+'): `${feature.y},${feature.x}`;
        return `https://www.google.com/maps/dir/Current+Location/${dest}`;
      },

      editaevent(){
        // this.$router.push(`/aevent/${this.feature.properties.id}`);
        this.$router.push({
          name: 'editableaeventInfo',
          params: {
            aevent_id: this.feature.properties.id
          }
        });
      },

      async fetchaembassadors(id){
        const aembassadors = await api.getaembassadorsFromaevent(id || this.properties.id);
        this.featuredaembassadors.length = 0;
        this.featuredaembassadors.push(...aembassadors);
      }

    },

    computed: {
      properties(){
        return (this.feature || {}).properties || this.feature || {};
      },

      directionsUrl(){
        return Object.keys(this.properties).length ? this.getDirectionsUrl(this.properties): null;
      }
    },

    watch: {
      'properties.id'(newVal){
        // make sure to fetch aembassadors each time a new aevent is identified
        this.featuredaembassadors = [];
        if (newVal){
          this.fetchaembassadors(newVal);
        }
      }
    }
  }
</script>

<style scoped>

  .edit-btn {
    color:#f7296E;
    font-size: 1.25rem;
    cursor: pointer;
  }

  .aevent-info-header{
    display: flex;
    justify-content: space-around;
  }

  .no-features {
    color: gray;
  }

  .featured-aembassadors-container {
    max-height: 650px;
    overflow-y: auto;
  }

</style>