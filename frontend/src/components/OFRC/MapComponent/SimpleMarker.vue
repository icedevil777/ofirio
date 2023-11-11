<script lang="ts">
import { defineComponent, toRaw } from 'vue';
import MapInitMixin from './MapInit.mixin';

export default defineComponent({
  mixins: [ MapInitMixin ],
  methods: {
    onInit() {
      if (!this.api || !this.map)
        return;
      
      const [map, lat, lng] = [ this.map, toRaw(this.lat), toRaw(this.lng) ];

      this.entity = new this.api.Marker({
        position: { lat, lng },
        optimized: true,
        map,
        ...toRaw(this.markerOptions)
      });
    },
    onDestroy() {
      this.entity.setMap(null);
    }
  }
})
</script>