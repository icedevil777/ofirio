<template>
  <div class="ui-map-infowindow-list" ref="infoWindow">
    <template v-if="mode == 'default'">
      <PropertyCard mode="line" :property="p" v-for="p of properties" :financialProps="p.financialData" :key="p" />
    </template>
    <template v-else-if="mode == 'rent_anal'">
      <span v-if="!$isMobile.value && properties.length > 1" class="properties-list-title">{{ `${properties[0].address.split(',')[0]} - ${properties.length} listings` }}</span>
      <PropertyCardRentAnal :property="p" v-for="p of properties" :key="p" />
    </template>
  </div>
</template>

<style lang="less" scoped>
.ui-map-infowindow-list::v-deep {
  font-family: 'Raleway', 'Arial', sans-serif;
  
  .property-card {
    padding: 10px;

    @media @desktop { max-width: 400px; }

    + .property-card { border-top: 1px solid @col-gray; }
    .image {
      @s: 110px;
      
      width: @s;
      min-width: @s;
      height: @s;

      .svg-icon--heart-save {
        top: 5px;
        right: 5px;
      }
    }
    .label-block {
      top: auto;
      bottom: 10px;
      align-items: flex-start;
      flex-direction: column;

      .label { margin: 6px 0 0; }
    }

    .data {
      .street {
        font-size: .975rem;
        margin-bottom: 3px;
      }
      .quick-props {
        font-size: .875rem;
        margin-bottom: 9px;
      }
      .price { font-size: 1rem; }
      .premium-only { margin-bottom: 0; }
      .ui-small-prop:nth-child(3) { display: none; }
      .ui-small-prop { margin-top: 3px; }
      .ui-small-prop .value { font-size: .975rem; margin-bottom: 1px; }
      .ui-small-prop .label { font-size: .625rem; }
    }
    &.property-card-card {
      box-shadow: none;
      border-radius: 0;
      padding: 0;

      .image {
        border-radius: 0;
        padding-bottom: 75%;

        .label-block {
          top: 10px;
          bottom: auto;
          flex-direction: row;

          .label { margin: 0 6px 0; }
        }
      }
      .data { padding: 15px @mm 0; }
      &::v-deep {
        .data {
          .street {
            font-size: 1.214rem;
            line-height: 1.5rem;
          }
          .quick-props { font-size: 1.07rem; }
          .price { font-size: 1.285rem; }

          .ui-small-prop .value { font-size: 1.428rem ;}
          .ui-small-prop .label { font-size: .875rem ;}
        }
      }
    }
  }
  .properties-list-title {
    font-size: 1rem;
    font-weight: 700;
    display: inline-block;
    padding-bottom: 1rem/2;
    width: 100%;
    border-bottom: 1px solid @col-gray;
  }

}
</style>

<script lang="ts">
import { defineComponent } from 'vue';

import PropertyCard from '@/components/Property/Card.vue';
import PropertyCardRentAnal from '@/components/Property/RentAnalCard.vue';

export default defineComponent({
  props: {
    dontRemove: { type: Boolean, default: false },
    mode: { type: String, default: 'default' }
  },
  components: {
    PropertyCard,
    PropertyCardRentAnal
  },
  data() {
    return {
      properties: []
    }
  },
  methods: {
    setProperties(properties: any) {
      this.properties = properties;
    }
  },
  mounted() {
    if (this.dontRemove)
      return;
      
    const el = <HTMLDivElement>this.$refs.infoWindow;
    el.parentNode && el.parentNode.removeChild(el)
  },
})
</script>