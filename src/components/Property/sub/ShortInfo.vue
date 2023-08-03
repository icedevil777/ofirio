<template>
  <div class="property-short-info" v-if="property">
    <router-link class="street" :to="{ name: 'property', params: { id: property.prop_id, financialProps: financialData} }" :target="!$isMobile.value ? '_blank' : ''" v-if="property.prop_id != null && property.is_available != false">{{ property.address }}</router-link>
    <span class="street" v-else-if="property.is_available === false">{{ property.address }}</span>
    <span class="street" v-else-if="Account.Basis.isLoggedIn && !Account.Basis.dto?.verified" @click="$root['ev-popup-login-open']('email-validation')">{{ property.address }}</span>
    <span class="street" @click="$root['ev-popup-login-open']('register')" v-else>{{ property.address }}</span>
    <div class="quick-props">
      <span class="prop">{{ property.beds }} beds</span>
      <span class="prop">{{ property.baths }} baths</span>
      <span class="prop">{{ property.building_size }} sq.ft</span>
    </div>
    <span class="price">{{ $format['usdInt'](property.price) }}</span>
    <StatusLabel :label="property.status"></StatusLabel>
  </div>
  <div class="property-short-info" v-else>
    <span class="street">336 Brandford Street</span>
    <div class="quick-props">
      <span class="prop">4 beds</span>
      <span class="prop">2 baths</span>
      <span class="prop">2720 sq.ft</span>
    </div>
    <span class="price">$1,540,000</span>
  </div>

</template>

<style lang="less" scoped>
.property-short-info {
  line-height: 1.125rem;
  max-width: 100%;

  > a, span { display: block; }
  .street {
    font-weight: 600;
    font-size: 1.0625rem;
    margin-bottom: 5px;
    cursor: pointer;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 100%;

    @media @mobile {
      white-space: normal;
      line-height: 1.25rem;
      overflow: hidden;
    }
  }
  .quick-props {
    color: @col-text-gray-darker;
    font-size: 0.9875rem;
    margin-bottom: 10px;

    .prop { display: inline; }
    .prop + .prop:before {
      content: '\00B7';
      vertical-align: middle;
      display: inline-block;
      margin: 0 5px;
    }
  }
  .price {
    font-weight: 700;
    font-size: 1.125rem;
    display: inline;
    vertical-align: middle;
  }
  .label {
    display: inline;
    margin-left: 10px;
    vertical-align: middle;
  }
}
</style>

<script lang="ts">
import { defineComponent } from 'vue';
import qs from 'query-string';

import StatusLabel from './StatusLabel.vue';
import AccountStore from '@/models/Account'

export default defineComponent({
  components: {
    StatusLabel
  },
  props: {
    property: Object,
    financialProps: Object
  },
  computed: {
    Account() { return AccountStore; },
    financialData():string | undefined {
      if (this.financialProps)
        return qs.stringify(this.financialProps);
      return undefined
    }
  }
})
</script>