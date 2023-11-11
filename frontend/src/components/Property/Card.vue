<template>
  <div class="property-card flex" :class="[ 'property-card-' + mode ]">
    <div class="image">
      <router-link :to="{ name: 'property', params: { id: property.prop_id, financialProps: financialData } }" v-if="property.prop_id != null" :target="!$isMobile.value ? '_blank' : ''" class="router-link">
        <img v-if="property.photo1" :src="property.photo1" alt="Image" class="main-image">
        <img v-else src="@/assets/images/common/image-placeholder.png" alt="No Image" class="image-placeholder main-image">
      </router-link>
      <FavoriteHeart v-if="!property.hidden && Account.Auth.isLoggedIn" :property="property" />
      <div class="label-block flex">
        <StatusLabel :label="badge" v-for="badge of property.badges" :key="badge" />
        <StatusLabel label="55plus" v-if="property.is_55_plus" />
        <StatusLabel label="cash_only" v-if="property.is_cash_only" />
        <StatusLabel label="rehab" v-if="property.is_rehab && $isMobile.value" />
      </div>
      <StatusLabel label="rehab" v-if="property.is_rehab && !$isMobile.value" />
    </div>
    <div class="data">
      <ShortInfo :property="property" :financialProps="financialProps" />
      <UnlockAnalytics v-if="!Account.Basis.isPremium" />
      <div class="props flex" :class="{ 'hidden': !Account.Basis.isPremium }">
        <USmallProp colorScheme="cap-coc" :label="$isMobile.value || mode == 'card' ? 'COC' : 'Cash On Cash'" :value="property.cash_on_cash" :formatter="$format['%']"/>
        <USmallProp colorScheme="cap-coc" :label="$isMobile.value || mode == 'card' ? 'Cap Rate' : 'Cap Rate'" :value="property.cap_rate" :formatter="$format['%']"/>
        <USmallProp :label="$isMobile.value || mode == 'card' ? 'Total Return' : 'Total Return'" :value="property.total_return" :formatter="$format['%']"/>
        <USmallProp :label="$isMobile.value || mode == 'card' ? 'Est. Rent' : 'Est. Rent'" :value="property.predicted_rent" :formatter="$format['usdInt']"/>
      </div>
    </div>
  </div>
</template>

<style lang="less" scoped>
.property-card {
  position: relative;
  justify-content: flex-start;
  align-content: stretch;
  align-items: stretch;
  white-space: nowrap;


  @media @mobile {
    flex-wrap: wrap;
    align-items: flex-start;
    padding: 0 @mm;
  }

  .image {
    position: relative;
    width: 190px;
    min-width: 190px;
    border-radius: @border-radius;
    overflow: hidden;

    @media @mobile {
      @s: 125px;
      width: @s;
      min-width: @s;
      height: @s;
    }

    > a::before {
      content: '';
      display: block;
      position: absolute;
      width: 100%;
      height: 100%;
      z-index: 1;
    }
    .main-image {
      display: block;
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      object-fit: cover;

      &.image-placeholder {
        object-fit: contain;
        padding: 25px 0;
        background: @col-gray-light;
      }
    }
    &::v-deep .svg-icon--heart-save {
      position: absolute;
      right: 10px;
      top: 10px;
      width: 24px;
      height: 24px;
      z-index: 2;

      @media @mobile {
        top: 5px;
        right: 5px;
      }
    }
    .label-block {
      position: absolute;
      top: 10px;
      left: 10px;
      flex-direction: row;
      max-width: 146px;
      flex-wrap: wrap;

      .label { margin: 0 6px 6px 0; }

      @media @mobile {
        top: auto;
        bottom: 5px;
        align-items: flex-start;
        flex-direction: column;

        .label { margin: 0 0 3px; }
      }
    }
    > .rehab-opportunity {
      position: absolute;
      bottom: 10px;
      left: 10px;
    }
  }
  .data {
    flex: 1;
    margin-left: 20px;
    overflow: hidden;
    position: relative;

    .unlock-analytics {
      position: absolute;
      width: 100%;
      height: 45px;
      bottom: 15px;

      @media @mobile { height: 35px; }
    }
    @media @mobile {
      .ui-small-prop:nth-child(3) { display: none; }
    }
    .ui-small-prop { flex: 1; }
    .ui-small-prop + .ui-small-prop { margin-left: 10px; }
    .props {
      margin-top: 10px;
      justify-content: flex-start;
      align-items: flex-start;

      &.hidden {
        .ui-small-prop::v-deep .value { margin-bottom: 20px; }
      }
    }
  }
  &.property-card-card {
    box-shadow: 0px 3px 10px rgba(0, 0, 0, 0.15);
    border-radius: @border-radius;
    flex-direction: column;
    justify-content: stretch;
    align-items: stretch;

    @media @mobile {
      box-shadow: none;
      border-radius: 0;
      padding: 0;
    }
    .image {
      width: 100%;
      height: auto;
      padding-bottom: 50%;
      border-radius: @border-radius @border-radius 0 0;
      margin: 0;

      .label-block { max-width: none; }

      @media @mobile {
        border-radius: 0;
        padding-bottom: 75%;

        .label-block {
          top: 10px;
          bottom: auto;
          flex-direction: row;

          .label { margin: 0 6px 0; }
        }
      }
    }
    .data {
      padding: 15px;
      margin: 0;
      display: flex;
      flex-wrap: nowrap;
      flex-direction: column;
      justify-content: space-between;
      align-items: space-between;
      
      @media @mobile { padding: 15px @mm 0; }
      .unlock-analytics {
        width: calc(100% - 30px);
        height: 30px;
        bottom: 30px;

        @media @mobile { bottom: 20px; }
      }
      .props {
        &.hidden {
          .ui-small-prop::v-deep .value { margin-bottom: 15px; }
        }
      }
      .ui-small-prop + .ui-small-prop { margin-left: 5px; }
    }
    &::v-deep {
      .data {
        .street {
          font-size: .9375rem;
          line-height: 1.25rem;
          white-space: normal;
        }
        .quick-props { font-size: .875rem; }
        .price { font-size: 1rem; }

        .ui-small-prop .value { font-size: .9375rem ;}
        .ui-small-prop .label { font-size: .625rem ;}
      }

      @media @mobile {
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
}
</style>

<script lang="ts">
import { defineComponent } from 'vue';

import qs from 'query-string';

import ShortInfo from './sub/ShortInfo.vue';
import StatusLabel from './sub/StatusLabel.vue';
import FavoriteHeart from './sub/FavoriteHeart.vue';
import USmallProp from '@/components/ui/USmallProp.vue';
import UButton from '@/components/ui/UButton.vue';
import UnlockAnalytics from '@/components/OFRC/UnlockAnalytics.vue';
import AccountStore from '@/models/Account';

export default defineComponent({
  props: {
    property: { required: true, type: Object },
    mode: { type: String, default: 'line' },
    valueMode: { type: String, default: 'normal' },
    financialProps: Object
  },
  components: {
    ShortInfo,
    USmallProp,
    UButton,
    StatusLabel,
    FavoriteHeart,
    UnlockAnalytics
  },
  computed: {
    Account() {
      return AccountStore;
    },
    financialData():string | undefined {
      if (this.financialProps)
        return qs.stringify(this.financialProps);
      return undefined
    }
  },
  methods: {
    changeProperty() {
      this.property.address = '8301 Sands Point Blvd Apt S105 Tamarac Florida 33321';
      this.property.beds = 4;
      this.property.baths = 2;
      this.property.price = 850000;
      this.property.building_size = 2720;
    }
  },
  mounted() {
    if (this.property.hidden)
      this.changeProperty();
  }
})
</script>