<template>
  <div class="property-card flex">
    <div class="image">
      <UIcon :name="getPropertyIcon()"/>
    </div>
    <div class="data">
      <span class="distance">{{ property.distance }} mi</span>
      <span class="address">{{ property.address.split(',')[0] }}</span>
      <div class="quick-props">
        <span class="prop">{{ property.beds }} beds</span>
        <span class="prop">{{ property.baths }} baths</span>
        <span class="prop">{{ property.building_size }} sq.ft</span>
      </div>
      <span class="price" v-colorBy:rentAnalyzerMarker="property.type">{{ $format['usdInt'](property.price) }}</span>
      <span class="property-type">{{ property.prop_type2 }}</span>
    </div>
  </div>
</template>

<style lang="less" scoped>
.property-card {
  position: relative;
  justify-content: flex-start;
  align-content: center;
  align-items: center;
  white-space: nowrap;

  @media @mobile { justify-content: space-evenly; }

  .image { 
    height: auto !important;
    width: auto !important;
    min-width: auto !important;
    margin-right: 22px;

    .svg-icon {
      @s: 70px;
      width: @s;
      height: @s;
      fill: @col-gray;
    }
  }
  .data {
    span {
      display: block;
      font-weight: 700;
      font-size: 1rem;
    }
    .distance {
      color: @col-green;
      
      @media @mobile { margin-bottom: 5px; }
    }
    .address { font-weight: 600; }
    .price, .property-type { display: inline; }
    .price { margin-right: 20px; }
    .quick-props {
      color: @col-text-gray-darker;
      margin: 5px 0 10px 0;

      .prop {
        display: inline;
        font-weight: 500;
        font-size: 0.875rem;
      }
      .prop + .prop:before {
        content: '\00B7';
        vertical-align: middle;
        display: inline-block;
        margin: 0 5px;
      }
    }
  }
}
</style>

<script lang="ts">
import { defineComponent } from 'vue';

import ShortInfo from './sub/ShortInfo.vue';
import StatusLabel from './sub/StatusLabel.vue';
import USmallProp from '@/components/ui/USmallProp.vue';
import UButton from '@/components/ui/UButton.vue';
import AccountStore from '@/models/Account';
import { colorSchemePipeStyle } from '@/pipes/ColorSchemes.pipe';

export default defineComponent({
  props: {
    property: { required: true, type: Object },
  },
  components: {
    ShortInfo,
    USmallProp,
    UButton,
    StatusLabel
  },
  computed: {
    Account() {
      return AccountStore;
    }
  },
  methods: {
    changeProperty() {
      this.property.beds = 4;
      this.property.baths = 2;
      this.property.price = 850000;
      this.property.building_size = 2720;
    },
    getPropertyIcon() {
      return this.property.prop_type2 == 'Single Family' ? 'house-single-family' : 'house-condo-apps';
    },
    getColorScheme(type:string) {
      return colorSchemePipeStyle('rentAnalyzerMarker', type);
    }
  },
  mounted() {
    if (this.property.hidden)
      this.changeProperty();
  }
})
</script>