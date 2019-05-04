<template>
  <b-list-group-item>
    <b-media>
      <b-img-lazy slot="aside" :src="thumbnailUrl" v-if="thumbnailUrl" height="128"/>
      <span slot="aside" title="no image available" v-else><font-awesome-icon prefix="fas" icon="image" class="no-img"/></span>
      <h5>{{ aembassador.name }}
        <span class="float-right action-btn" @click="emitDeleteaembassador">
          <i class="fas fa-minus-circle remove-aembassador"
             title="remove aembassador">
          </i>
        </span>
        <span class="float-right action-btn" style="margin-right: 0.35rem;" @click="goToaembassador">
          <i class="fas fa-pen" style="color: forestgreen;" title="edit aembassador"></i>
        </span>
      </h5>
      <p :class="[(aembassador.description || '').trim().length < 1 ? 'no-desc': 'desc']">{{ aembassador.description || 'no description available, click pen to edit' }}</p>

    </b-media>
  </b-list-group-item>
</template>

<script>
  import api from '../../modules/api';
  export default {
    name: "aembassador-preview",
    mounted(){
      this.getThumbnailUrl();
      hook.bp=this;
    },

    props: {
      aembassador: {
        type: Object,
        default(){
          return {};
        }
      }
    },
    data(){
      return {
        thumbnailUrl: null
      }
    },
    methods: {
      goToaembassador(){
        console.log('going to aembassador! ', this.aembassador.id);
        this.$router.push({ name: 'editableaembassadorInfo', params: { aembassador_id: this.aembassador.id } })

      },

      async emitDeleteaembassador(){
        this.$emit('delete-aembassador', this.aembassador.id);
        console.log('deleting aembassador with id: ', this.aembassador.id)
      },

      async getThumbnailUrl(){
        const photos = await api.getaembassadorPhotos(this.aembassador.id);
        console.log('aembassador photos: ', photos);
        if (photos.length){
          console.log('setting photo url: ', api.getPhotoUrl(photos[0].id));
          this.thumbnailUrl = api.getPhotoUrl(photos[0].id, true)
        }
      }
    }
  }
</script>

<style scoped>
  .desc {
    color: gray;
  }
  .no-desc {
    color: darkgray !important;
    font-style: italic;
  }
  .no-img {
    color: lightgray;
    font-size: 128px;
  }

  .action-btn {
    cursor: pointer;
    font-size: 1.25rem;
  }

  .remove-aembassador {
    color: red;
  }

</style>