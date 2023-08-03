<script lang="ts">
import { defineComponent, toRaw } from 'vue';
import MapInitMixin from './MapInit.mixin';

export default defineComponent({
  props: {
    data: { type: Object, required: true },
    radius: { type: Number, required: true }
  },
  mixins: [ MapInitMixin ],
  methods: {
    onInit() {
      if (!this.api || !this.map)
        return;

      const [map, lat, lng, radius] = [ this.map, toRaw(this.lat), toRaw(this.lng), this.radius ];

      this.entity = new this.api.Circle({
        center: { lat, lng },
        radius: radius * 1609,
        strokeWeight: 0,
        fillColor: '#6454C3',
        fillOpacity: 0.07,
        map,
      });
    },
    onDestroy() {
      this.entity.setMap(null);
    }
  }
})
</script>