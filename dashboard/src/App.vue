<script lang="ts">
import overview from './components/overview.vue';
import forcegraph from './components/Forcedgraph.vue'
import correlation from './components/correlation.vue'

export default {
  data(){
    return {
      graphSelected: false,
      graph_id: -1,
      graph_label: -1,
      node_id: -1,
    }
  },
  components: {
    overview,
    forcegraph,
    correlation
  },
  created(){
  },
  mounted(){},
  methods: {
    handlegraphSelected(selected) {
        console.log('parent noticed change graph ' + selected);
        if (selected != -1) {
          this.graph_id = selected;
          this.graphSelected = true;
        }
        else {
          this.graph_id = -1;
          this.graphSelected = false;
        }
    },
    handlegraphColor(label){
        console.log('parent noticed change graph ' + label);
        this.graph_label = label;
    },
    handlenodeSelected(selected) {
        console.log('parent noticed change node ' + selected);
        this.node_id = selected;
    },
  }
}
</script>

<!--This is using the grid component from Vuetify to do layout design-->
<template>
  <v-container id="main-container" class="d-flex flex-row flex-nowrap" fluid>
    <v-col>
        <overview  @graphChange="handlegraphSelected" @graphColor="handlegraphColor"/>
    </v-col>
    <v-col>
        <forcegraph v-if="graphSelected" :graphID="graph_id" :graphColor="graph_label" @nodeChange="handlenodeSelected"/>
    </v-col>
    <v-col>
        <correlation v-if="graphSelected" :graphID="graph_id" :graphColor="graph_label" :nodeID="node_id"/>
    </v-col>
  </v-container>
</template>

<style scoped>
#main-container{
  height: 100%;
  width: 100%;
}
</style>
