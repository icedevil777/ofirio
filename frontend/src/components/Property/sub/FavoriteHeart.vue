<template>
  <slot :active="active" :toggle="toggle"><UIcon name="heart-save" class="ui-property-favorite-icon" :class="{ active }" @click="toggle" /></slot>
</template>

<style lang="less">
  .ui-property-favorite-icon {
    fill: rgba(0, 0, 0, 0.4);
    stroke: @col-bg;
    stroke-width: 1.5px;
    cursor: pointer;

    &.active { fill: @col-blue; }
  }
</style>


<script lang="ts">
import { TAccountDTO__FavoriteItem } from '@/models/Account/favorites/api';
import PropertyBasisModule, { markFavorite } from '@/models/Property/basis';
import { SearchResult } from '@/models/Search';
import AccountStore from '@/models/Account'

import { defineComponent, PropType } from 'vue';

export default defineComponent({
  emits: [ 'heart-click', 'fav-added', 'fav-removed' ],
  props: {
    property: { required: true, type: Object as PropType<PropertyBasisModule | SearchResult | TAccountDTO__FavoriteItem> },
    skipClick: { type: Boolean, default: false },
    forceInitState: { type: Boolean, default: false },
    forceInitStateValue: Boolean
  },
  data() {
    let initState = this.getPropFavAttr();
    if (this.forceInitState)
      initState = this.forceInitStateValue;

    return {
      inProgress: false,
      active: initState,
    }
  },
  methods: {
    getPropFavAttr() {
      if ((<PropertyBasisModule>this.property).dto?.favorite != undefined)
        return (<PropertyBasisModule>this.property).dto?.favorite;

      else if ((<SearchResult>this.property).favorite != undefined)
        return (<SearchResult>this.property).favorite;

      return false;
    },
    async toggle() {
      if (!AccountStore.Restrictions.canSaveProperty())
        return;

      if (this.inProgress)
        return;

      if (!this.property)
        return;

      if (this.skipClick)
        return this.$emit('heart-click');
      
      this.inProgress = true;
      const operationResult = await markFavorite(this.property, !this.active);
      this.inProgress = false;

      if (!operationResult)
        return;

      this.$emit( !this.active ? 'fav-added' : 'fav-removed');
      this.active = !this.active;
    }
  }
})
</script>