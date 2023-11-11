<template>
  <div class="ofrc-map" ref="mapDiv"></div>
  <slot />
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import { Loader } from '@googlemaps/js-api-loader';
import envModel from '@/models/env.model';

export default defineComponent({
  props: {
    loaderParams: Object,
    mapInitParams: Object
  },
  data() {
    return {
      inited: false,
      api: null as null | typeof google.maps,
      map: null as null | google.maps.Map,
      promise: null as null | Promise<any>,
      _promise_res: null as null | Function,
      _promise_rej: null as null | Function
    }
  },
  beforeMount() {
    this.promise = new Promise((res, rej) => {
      this._promise_res = res;
      this._promise_rej = rej;
    });
  },
  mounted() {
    const loader = new Loader({
      apiKey: "AIzaSyBATj60R98qYqjle9QsYFttUVi-b4Z2nPQ",
      ...this.loaderParams
    });
    loader.loadPromise().then(() => {
      this.api = google.maps;
      this.map = new google.maps.Map(this.$refs.mapDiv as HTMLElement, {
        zoom: 10,
        center: { lat: 47.116386, lng: -101.299591 },
        zoomControlOptions: { position: google.maps.ControlPosition.RIGHT_TOP },
        fullscreenControl: false,
        gestureHandling: 'greedy',
        ...this.mapInitParams
      });

      this.inited = true;
      this._promise_res && this._promise_res(this.map, this.api);
    });
  }
})
</script>

<style lang="less" scoped>
.ofrc-map {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}
</style>