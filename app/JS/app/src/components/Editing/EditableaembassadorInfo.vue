<template>
  <b-card bg-variant="light" class="editable-aevent">

    <!--  SPINNER FOR LOADING -->
    <span style="font-size: 3.5rem;" class="centered" v-if="state === 'loading'">
      <spinner :text="'loading aevent info...'"/>
    </span>

    <!-- EDITABLE aevent CONTENT -->
    <b-container class="aevent-content" v-else>
      <b-row class="mt-2">
        <b-col sm="12">
          <b-form-group label="Name:"
                        horizontal
                        label-text-align="right"
                        :label-cols="2">
            <b-form-input v-model="aevent.name" class="bold" />
          </b-form-group>
        </b-col>
      </b-row>

      <!-- ADDRESS -->
      <b-row md="12">
        <b-col sm="12">
          <b-form-group label="Address:"
                        horizontal
                        label-text-align="right"
                        :label-cols="2">
            <b-form-input id="address" v-model="aevent.address"/>
          </b-form-group>
        </b-col>
      </b-row>

      <!--  city, st zip -->
      <b-row class="mt-2" align-h="end">
          <b-col sm="12" md="5">
            <b-form-group label="City:" label-text-align="left">
              <b-form-input v-model="aevent.city" />
            </b-form-group>
          </b-col>
          <b-col sm="6" md="3">
            <b-form-group label="State:" label-text-align="left">
              <b-form-select :options="stateList" v-model="aevent.state"></b-form-select>
            </b-form-group>
          </b-col>

          <b-col sm="6" md="2">
            <b-form-group label="Zip Code:" label-text-align="left">
              <b-form-input v-model="aevent.zip"/>
            </b-form-group>
          </b-col>
        <!--</div>-->
      </b-row>

      <!-- WEBSITE -->
      <b-row class="mt-2">
        <b-col sm="12">
          <b-form-group label="Website:"
                        horizontal
                        label-text-align="right"
                        :label-cols="2">
            <b-form-input id="website" v-model="aevent.website" style="color:#0000EE;"/>
          </b-form-group>
        </b-col>
      </b-row>

      <!--  WEEKDAY HOURS -->
      <b-row class="mt-2" >
        <b-col sm="12" md="6">
          <b-form-group v-for="weekday in weekday_fields"
                        horizontal
                        :label-cols="5"
                        label-class="capitalize"
                        :label="`${weekday} Hours:`"
                        :key="weekday" class="mt-2">
            <b-form-input :id="weekday" v-model="aevent[weekday]" placeholder="ex: 11am-7pm" />
          </b-form-group>
        </b-col>
        <b-col sm="12" md="6">
          <b-form-group label="aevent Description:" label-text-align="left" class="mt-2" id="description">
            <b-form-textarea :rows="weekday_fields.length + 6" v-model="aevent.comments"></b-form-textarea>
          </b-form-group>
        </b-col>

      </b-row>

      <!--  SAVE BUTTON AND TYPE -->
      <b-row class="mt-4">
        <b-col sm="6">
          <b-form-group label="Type">
            <b-form-radio-group v-model="aevent.aevent_type" :options="typeOptions">
            </b-form-radio-group>
          </b-form-group>
        </b-col>

        <b-col sm="6">
          <div class="save-container">
            <div class="buttons-container" v-if="state === 'loaded'">
              <b-button @click="saveChanges" class="theme mt-2" >Save Changes</b-button>
              <b-button class="bold mt-2 ml-4" variant="danger" @click="deleteaevent">Delete aevent</b-button>
            </div>

            <div v-else>
              <spinner text="Saving Changes..." :visible="state === 'saving'"/>

              <b-alert :show="1" @dismissed="state = 'loaded'"
                       v-if="state === 'saved'"
                       variant="success">
                Successfully Updated aevent.
              </b-alert>

              <b-alert :show="1" @dismissed="state = 'loaded'"
                       v-if="state === 'error'"
                       variant="danger">
                Failed to Update aevent, please try again.
              </b-alert>
            </div>
          </div>
        </b-col>
      </b-row>

      <!--  aembassador ROWS -->
      <b-row class="mt-4">
        <accordion :header="'Featured aembassadors'" @action-btn-clicked="addaembassador">
          <template slot="action_btn">
            <i class="fas fa-plus-circle" title="add new aembassador"></i>
          </template>

          <b-list-group v-for="aembassador in aembassadors" v-show="aembassadors.length" :key="aembassador.id">
            <aembassador-preview :aembassador="aembassador" @delete-aembassador="deleteaembassador"/>
          </b-list-group>

          <h5 v-show="!aembassadors.length" style="color: gray;" class="mt-2">No aembassadors found, use plus button to add new aembassadors</h5>

        </accordion>
      </b-row>

    </b-container>

  </b-card>
</template>

<script>
  import api from '../../modules/api';
  import enums from '../../modules/enums';
  import Accordion from '../UI/Accordion';
  import { EventBus } from "../../modules/EventBus";
  import swal from 'sweetalert2';
  import aembassadorPreview from './aembassadorPreview';

  export default {
    name: "aevent-info",
    components: {
      Accordion,
      aembassadorPreview
    },
    data(){
      return {
        state: 'loading',
        aevent: {},
        copy: {},
        weekday_fields: ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday'],
        stateList: enums.states,
        aembassadors: [],
        typeOptions: [
          { text: 'aevent', value: 'aevent' },
          { text: 'aevent Pub', value: 'aevent Pub' }
        ]
      }
    },

    async mounted(){
      console.log('mounted editable aevent: ', this.$route.params);
    },

    // we want to make sure to intercept this to force the router to update
    // the current aevent
    beforeRouteEnter(to, from, next){
      next(async (vm)=>{
        // vm is reference to this component!
        await vm.update(to.params.aevent_id);
        console.log('updated aevent and calling next: ', vm.aevent);
        next();
      })

    },

    beforeRouteLeave (to, from, next) {
      // called when the route that renders this component is about to
      // be navigated away from.
      // has access to `this` component instance.
      // make sure there haven't been any changes before leaving route
      console.log('BEFORE aevent ROUTE LEAVE')
      if (this.state !== 'deleted' && JSON.stringify(this.aevent) != JSON.stringify(this.copy)){
        swal({
          type: 'warning',
          title: 'You have unsaved Edits',
          text: 'You are about to leave this page but have unsaved edits. Do you want to save your changes before proceeding?',
          showCancelButton: true,
          confirmButtonColor: 'forestgreen',
          cancelButtonColor: '#d33',
          cancelButtonText: "Don't Save Changes",
          confirmButtonText: 'Save Changes'
        }).then((choice)=>{
          if (choice){
            // save here before proceeding
            console.log('SAVE HERE!');
            this.saveChanges();
          }

          // now proceed
          next();
        })
      } else {
        next();
      }
    },

    methods: {
      async update(id){
        this.state = 'loading';
        this.aembassadors.length = 0;
        if (!id){
          id = this.$route.params.aevent_id;
        }
        this.aevent = await api.getaevents({id: id, options: { f: 'json'} });
        this.copy = Object.assign({}, this.aevent);
        this.updateaembassadors();
        this.state = 'loaded';
        return this.aevent;
      },

      async updateaembassadors(){
        this.aembassadors.length = 0;
        this.aembassadors.push(...await api.getaembassadorsFromaevent(this.aevent.id));
      },

      deleteaevent(){
        console.log('clicked delete aevent!')
        swal({
          title: 'Are you sure?',
          text: 'Once deleted, this operation cannot be undone',
          type: 'warning',
          showCancelButton: true,
          confirmButtonText: 'Yes, Delete',
          confirmButtonColor: 'forestgreen',
          showLoaderOnConfirm: true,
          allowOutsideClick: ()=> !swal.isLoading(),
          preConfirm: async ()=> {
            return await api.deleteItem('aevents', this.aevent.id);
          }
        }).then((res)=> {
          console.log('RES: ', res.value);
          this.state = 'deleted';
          EventBus.$emit('aevent-changed', {
            id: this.aevent.id,
            type: 'delete'
          });
          swal({
            type: 'success',
            title: 'Success!',
            text: 'successfully deleted aevent'
          }).then(()=>{
            this.$router.push({name: 'home'});
          });
        }).catch((err)=> {
          swal({
            type: 'error',
            title: 'Unable to Delete aevent',
            text: "please make sure you're logged in to make this change"
          })
        })
      },

      async addaembassador(){
        console.log('clicked add aembassador');
        swal({
          title: 'Create New aembassador',
          input: 'text',
          showCancelButton: true,
          confirmButtonText: 'Create',
          confirmButtonColor: 'forestgreen',
          showLoaderOnConfirm: true,
          allowOutsideClick: ()=> !swal.isLoading(),
          preConfirm: async (name)=> {
            return await api.createItem('aembassadors', {
              aevent_id: this.aevent.id,
              name: name
            });
          }
        }).then((res)=> {
          const newaembassadorId = res.value.id;
          console.log('CREATE aembassador RESPONSE: ', res, newaembassadorId);
          swal({
            title: 'Success',
            text: 'successfully created new aembassador',
            confirmButtonText: 'Go To New aembassador',
            cancelButtonText: 'Stay Here',
            showCancelButton: true
          }).then((res)=>{
            res.value ? this.goToEditaembassador(newaembassadorId): this.emitaembassadorChange(newaembassadorId, 'create');
          });

        }).catch(err =>{
          console.log('error creating aembassador: ', err);
          swal({
            type: 'error',
            title: 'Unable to Create aembassador',
            text: "please make sure you're logged in to make this change"
          })
        });
      },

      deleteaembassador(id){
        //const component = this
        swal({
          title: 'Are you sure?',
          text: 'Once deleted, this operation cannot be undone',
          type: 'warning',
          showCancelButton: true,
          confirmButtonText: 'Yes, Delete',
          confirmButtonColor: 'forestgreen',
          showLoaderOnConfirm: true,
          allowOutsideClick: ()=> !swal.isLoading(),
          preConfirm: async ()=> {
            return await api.deleteItem('aembassadors', id);
          }
        }).then((res)=> {
          console.log('RES: ', res.value);
          this.emitaembassadorChange(id, 'delete');

          swal({
            type: 'success',
            title: 'Success!',
            text: 'successfully deleted aembassador'
          });
        }).catch((err)=> {
          swal({
            type: 'error',
            title: 'Unable to Delete aembassador',
            text: "please make sure you're logged in to make this change"
          })
        })
      },

      goToEditaembassador(id){
        console.log('navigating to new aembassador: ', id);
        this.emitaembassadorChange(id, 'create');
        setTimeout(()=>{
          this.$router.push({ name: 'editableaembassadorInfo', params: { aembassador_id: id } });
        }, 250);
      },

      async saveChanges(){
        console.log('submitting edits: ', this.aevent);
        this.state = 'saving';
        try {
          const resp = await api.updateItem('aevents', this.aevent);

          // make sure to update copy so router guard isn't thrown
          this.copy = Object.assign({}, this.aevent);

          // emit change
          this.emitaeventChange('update');
          this.state = 'saved';
        } catch(err){
          console.log('err: ', err);
          this.state = 'error';
        }

      },

      emitaeventChange(type){
        EventBus.$emit('aevent-changed', {
          id: this.aevent.id,
          type: type
        });
      },

      emitaembassadorChange(id, type){
        console.log('emitting aembassadors-changed: ', this.aevent.id);
        EventBus.$emit('aembassadors-changed', {
          aevent_id: this.aevent.id,
          aembassador_id: id,
          type: type
        });
        this.updateaembassadors();
      },
    }
  }
</script>

<style>

  .editable-aevent {
    min-height: calc(100vh - 60px);
  }

</style>