<template>
  <div class="account-internal-padding favs">
    <h1 class="heading">Favorites</h1>
    <div class="account-sub-block">
      <template v-if="items === undefined">
        <UPreloader v-for="i of 5" :key="i" mode="favorites" :activation="true" />
      </template>
      <table class="favorites-list" v-else-if="items && items.length > 0">
        <tr v-for="fav of favList" :key="fav" :class="{ 'unavailable': !fav.is_available, 'hidden': !Account.Basis.isPremium }">
          <td class="property-small-info flex">
            <img v-if="fav.photo1" class="property-image" :src="fav.photo1">
            <img v-else src="@/assets/images/common/image-placeholder.png" alt="No Image" class="image-placeholder property-image">
            <Property--ShortInfo :property="fav"/>
          </td>
          <td class="self-pad">
            <UnlockAnalytics v-if="!Account.Basis.isPremium" />
            <USmallProp :value="fav.cash_on_cash" :formatter="$format['%']" :label="$isMobile.value ? 'COC' : 'Cash on cash'" colorScheme="cap-coc"/>
          </td>
          <td class="self-pad">
            <USmallProp :value="fav.cap_rate" :formatter="$format['%']" label="CAP rate" colorScheme="cap-coc"/>
          </td>
          <td class="self-pad">
            <USmallProp :value="fav.total_return" :formatter="$format['%']" label="Total Return"/>
          </td>
          <td class="self-pad">
            <USmallProp :value="fav.predicted_rent" :formatter="$format['usdInt']" label="EST. RENT"/>
          </td>
          <td class="self-pad fav-btn"><FavoriteHeart :property="fav" forceInitState :forceInitStateValue="true" @fav-removed="removeFavorite(fav)" /></td>
        </tr>
      </table>
    </div>
    <UPagination v-if="items" v-show="items.length > 10" v-model="pages" :chunkSize="10" :dataCount="items.length"/>
  </div>
</template>

<style lang="less" scoped>
.favs > h1.heading {
  @media @mobile { margin-bottom: 20px; }
}
.favorites-list {
  width: 100%;

  tr.unavailable {
    td:first-child, .ui-small-prop { opacity: .5; }
  }
  tr {
    &.hidden {
      td { position: relative; }
      .unlock-analytics {
        position: absolute;
        top: 20px;
        left: 0;
        width: 350%;
        height: 50px;
        z-index: 1;
  
        @media @mobile {
          width: 100%;
          top: auto;
          bottom: 60px;
          height: 40px;
        }
      }
      .ui-small-prop::v-deep {
        .value { margin-bottom: 20px; }
      }
      @media @mobile {
        position: relative;

        td { position: static; }
      }
    }
  }
  td {
    @p: 20px;

    vertical-align: middle;
    padding: @p 0;

    &.self-pad {
      padding: @p;

      @media @mobile {
        padding: 0 0 @p;
        width: calc(25% - 5px);
      }
    }
    &.property-small-info {
      justify-content: flex-start;
      align-items: center;

      .property-image {
        display: block;
        margin-right: 20px;
        width: 100px;
        min-width: 100px;
        height: 80px;
        min-height: 80px;
        border-radius: @border-radius;

        &.image-placeholder {
          object-fit: contain;
          padding: 10px 0;
          background: @col-gray-light;
        }
        @media @mobile {
          @s: 70px;

          width: @s;
          min-width: @s;
          height: @s;
          min-height: @s;
        }
      }
      &::v-deep > .property-short-info > span { display: inline-block; }
      @media @mobile {
        width: 100%;
        padding-right: 20px;
      }
    }
    &.fav-btn {
      vertical-align: top;
      text-align: right;
      padding-right: 0;

      &::v-deep .svg-icon {
        fill: @col-blue;
        stroke: @col-blue;
        cursor: pointer;

        @media @mobile {
          @s: 18px;

          position: absolute;
          top: @p;
          right: 0;
          width: @s;
          height: @s;
        }
      }
    }
  }
  tr + tr { border-top: 1px solid @col-gray; }
  @media @mobile {
    tr {
      display: flex;
      flex-wrap: wrap;
      position: relative;
      justify-content: space-between;
      align-content: flex-start;
    }
  }
}
.ui-pagination { margin-top: 30px; }
</style>

<script lang="ts">
import { defineComponent } from 'vue';

import Property__ShortInfo from '@/components/Property/sub/ShortInfo.vue';
import USmallProp from '@/components/ui/USmallProp.vue';
import UPagination from '@/components/ui/UPagination.vue';
import UPreloader from '@/components/ui/UPreloader.vue';
import FavoriteHeart from '@/components/Property/sub/FavoriteHeart.vue';
import UnlockAnalytics from '@/components/OFRC/UnlockAnalytics.vue';

import AccountStore from '@/models/Account';
import { TAccountDTO__FavoriteItem } from '@/models/Account/favorites/api';
import { observe } from '@/services/LocalstorageWatcher.service';

export default defineComponent({
  components: {
    'Property--ShortInfo': Property__ShortInfo,
    UPagination,
    USmallProp,
    UPreloader,
    FavoriteHeart,
    UnlockAnalytics
  },
  computed: {
    favList() {
      if (!this.items)
        return [];
      
      //@ts-ignore
      return this.items.slice(this.pages[0] - this.pages[1]);
    },
    Account() {
      return AccountStore;
    }
  },
  data() {
    return {
      items: undefined as undefined | TAccountDTO__FavoriteItem[],
      pages: [0,0],
      observes: [] as Array<Function>
    }
  },
  methods: {
    removeFavorite(fav: any) {
      if (!this.items)
        return;

      const i = this.items.indexOf(fav);
      if (i == -1)
        return;
        
      this.items.splice(i, 1);
    },
    async loadItems() {
      await AccountStore.Favorites.load();
      this.items = AccountStore.Favorites.dto?.items;
    }
  },
  async mounted() {
    this.loadItems();
    this.observes.push(observe('ofirio-favorite-added', () => {
      this.loadItems();
    }));
    this.observes.push(observe('ofirio-favorite-removed', () => {
      this.loadItems();
    }));
  },
  beforeUnmount() {
    this.observes.forEach(unwatch => unwatch());
  }
})
</script>