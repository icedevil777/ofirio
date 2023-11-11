<script lang="ts">

import { defineComponent, toRaw } from 'vue';
import MapInitMixin from './MapInit.mixin';

export default defineComponent({
  props: {
    data: { type: Object, required: true },
    type: { type: String, required: true }
  },
  mixins: [ MapInitMixin ],
  methods: {
    onInit() {
      if (!this.api || !this.map)
        return;
      
      const [map, lat, lng, type] = [ this.map, toRaw(this.lat), toRaw(this.lng), this.type ];

      this.entity = new this.api.Marker({
        position: { lat, lng },
        optimized: true,
        icon: this.getIconType(type),
        map,
        ...toRaw(this.markerOptions)
      });
    },
    getIconType(type:string) {
      if (type === 'higher')
        return '/mapMarkerIcons/rent-estimator-marker-red.svg';
      else if (type === 'moderate')
        return '/mapMarkerIcons/rent-estimator-marker-blue.svg';
      else
        return '/mapMarkerIcons/rent-estimator-marker-green.svg';
    },
    onDestroy() {
      this.entity.setMap(null);
    }
  }
})
</script>