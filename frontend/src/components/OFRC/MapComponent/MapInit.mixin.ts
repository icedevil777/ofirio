import { defineComponent, markRaw } from 'vue'

export default defineComponent({
  render: () => null,
  props: {
    lat: { type: Number, required: true },
    lng: { type: Number, required: true },
    markerOptions: Object
  },
  data() {
    return markRaw({
      entity: null as any,
      map: null as null | google.maps.Map,
      api: null as null | typeof google.maps
    })
  },
  methods: {
    onInit() {},
    onDestroy() {}
  },
  mounted() {
    const mapComponent = <any>this.$parent;
    mapComponent.promise.then((map: any, api: any) => {
      this.map = map;
      this.api = mapComponent.api;
      this.onInit();
    });
  },
  beforeUnmount() {
    this.onDestroy();
  }

})