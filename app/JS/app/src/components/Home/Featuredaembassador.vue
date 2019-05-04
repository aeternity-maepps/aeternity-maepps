<template>
  <div>
    <b-media>
      <b-img rounded blank-color="#ccc" width="200" :src="imgSrc" v-show="imgSrcLoaded" :title="aembassador.name"></b-img>

      <h6 class="mt-2"><strong>{{ aembassador.name }}</strong></h6>

      <div class="featured-aembassador-body">
        <p style="text-align: center;">{{ aembassador.description }}</p>
        <span class="aembassador-info">
          <p>Style: {{ aembassador.style }}</p>
          <p>Alc: {{ aembassador.alc }}% by Vol</p>
          <p>IBU: {{ aembassador.ibu }}</p>
          <p>Color: {{ aembassador.color }}</p>
        </span>

      </div>

    </b-media>
  </div>
</template>

<script>
  import api from '../../modules/api';

  export default {
    name: "featured-aembassador",
    props:{
      aembassador: {
        type: Object,
        default(){
          return {};
        }
      }
    },
    data() {
      return {
        imgSrc: null,
        imgSrcLoaded: false
      }
    },
    async beforeMount(){
      // send off request before this is mounted
      const photos = await api.getaembassadorPhotos(this.aembassador.id);
      console.log('aembassador photos: ', photos);
      if (photos.length){
        console.log('setting photo url: ', api.getPhotoUrl(photos[0].id));
        this.imgSrc = api.getPhotoUrl(photos[0].id)
      }
    },
    methods: {},
    watch: {
      imgSrc(newVal){
        if (newVal){
          this.imgSrcLoaded = true;
        }
      }
    }
  }
</script>

<style>

  .featured-aembassador-body {
    text-align: left;
  }

  .aembassador-info > p {
    font-size: 95%;
    margin-top: 2px !important;
    margin-bottom: 2px !important;
  }

</style>