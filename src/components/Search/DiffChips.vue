<template>
  <swiper
    v-if="ready"
    :loop="false"
    :freeMode="true"
    :slidesPerView="'auto'"
    :spaceBetween="5"
    :navigation="{
      nextEl: $refs.swiperNext.$el,
      prevEl: $refs.swiperPrev.$el,
    }"
  >
    <swiper-slide tag="div" v-for="diff of customizationDiff" :key="diff">
      <UChip v-if="diff == 'cap_rate'" @onRemove="resetter('cap_rate')">Cap Rate {{ $format['%Int'](customization.values[diff]) }}</UChip>
      <UChip v-else-if="diff == 'coc_rate'" @onRemove="resetter('coc_rate')">Cash on Cash {{ $format['%Int'](customization.values[diff]) }}</UChip>
      <UChip v-else-if="diff == 'price' && customization.values.price[1] == customization.defaults.price[1]" @onRemove="resetter('price')">Price from {{ $format['usdInt'](customization.values[diff][0]) }}</UChip>
      <UChip v-else-if="diff == 'price'" @onRemove="resetter('price')">Price {{ $format['usdInt'](customization.values[diff][0]) }} - {{ $format['usdInt'](customization.values[diff][1]) }}</UChip>
      <UChip v-else-if="diff == 'monthly_rent'" @onRemove="resetter('monthly_rent')">Monthly Rent {{ $format['usdInt'](customization.values[diff]) }}</UChip>
      <UChip v-else-if="diff == 'property_type'" @onRemove="resetter('property_type')">{{ customization.values[diff][0] == 'condo-apt' ? 'Condo Apts.' : 'Single Family' }}</UChip>
      <UChip v-else-if="diff == 'predicted_rent_min'" @onRemove="resetter('predicted_rent_min')">Est. Rent {{ $format['usdInt'](customization.values[diff]) }}</UChip>
      <UChip v-else-if="diff == 'beds'" @onRemove="resetter('beds')">Beds {{ $format['number'](customization.values[diff][0]) }} - {{ $format['number'](customization.values[diff][1]) }}</UChip>
      <UChip v-else-if="diff == 'baths'" @onRemove="resetter('baths')">Baths {{ $format['number'](customization.values[diff]) }}+</UChip>
      <UChip v-else-if="diff == 'years'" @onRemove="resetter('years')">Built years {{ customization.values[diff][0] }} - {{ customization.values[diff][1] }}</UChip>
      <UChip v-else-if="diff == 'buildingSize' && customization.values.buildingSize[1] == customization.defaults.buildingSize[1]" @onRemove="resetter('buildingSize')">Building Size is at least {{ $format['number'](customization.values[diff][0]) }}</UChip>
      <UChip v-else-if="diff == 'buildingSize'" @onRemove="resetter('buildingSize')">Building Size {{ $format['number'](customization.values[diff][0]) }} - {{ $format['number'](customization.values[diff][1]) }}</UChip>
      <UChip v-else-if="diff == 'lotSize'" @onRemove="resetter('lotSize')">Lot Size {{ $format['number'](customization.values[diff][0]) }} - {{ $format['number'](customization.values[diff][1]) }}</UChip>
      <UChip v-else-if="diff == 'down_payment'" @onRemove="resetter('down_payment')">Down Payment {{ $format['%Int'](customization.values[diff].value) }}</UChip>
      <UChip v-else-if="diff == 'loan_type'" @onRemove="resetter('loan_type')">Loan Term {{ customization.values[diff].value }} years</UChip>
      <UChip v-else-if="diff == 'interest_rate'" @onRemove="resetter('interest_rate')">Interest Rate {{ $format['%'](customization.values[diff]) }}</UChip>
      <UChip v-else-if="diff == 'status_pending'" @onRemove="resetter('status_pending')">Pending</UChip>
      <UChip v-else-if="diff == 'status_sold'" @onRemove="resetter('status_sold')">Sold</UChip>

      <UChip v-else-if="diff == 'is_55_plus'" @onRemove="resetter('is_55_plus')">55+ Community</UChip>
      <UChip v-else-if="diff == 'is_rehab'" @onRemove="resetter('is_rehab')">Rehab Opprotunity</UChip>
      <UChip v-else-if="diff == 'is_cash_only'" @onRemove="resetter('is_cash_only')">Cash Only</UChip>
      <UChip v-else-if="diff == 'is_good_deal'" @onRemove="resetter('is_good_deal')">Good Deal</UChip>

      <UChip v-else-if="diff == 'hide_is_55_plus'" @onRemove="resetter('hide_is_55_plus')">Exclude 55+ Community</UChip>
      <UChip v-else-if="diff == 'hide_is_rehab'" @onRemove="resetter('hide_is_rehab')">Exclude Rehab</UChip>
      <UChip v-else-if="diff == 'hide_is_cash_only'" @onRemove="resetter('hide_is_cash_only')">Exclude Cash Only</UChip>
    </swiper-slide>
    <swiper-slide tag="div">
      <UChip v-if="customization.values.status_for_sale && (customizationDiff.includes('status_pending') || customizationDiff.includes('status_sold'))" @onRemove="customization.values.status_for_sale = false; resetter([], 'force')">For Sale</UChip>
    </swiper-slide>
  </swiper>
  <UButton class="ui-btn ui-btn-iconic ui-btn-circle swiper-chips-prev" ref="swiperPrev"><UIcon name="smooth-arrow"/></UButton>
  <UButton class="ui-btn ui-btn-iconic ui-btn-circle swiper-chips-next" ref="swiperNext"><UIcon name="smooth-arrow"/></UButton>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import UChip from '@/components/ui/UChip.vue'
import UButton from '@/components/ui/UButton.vue'
import SwiperCore, { Navigation } from 'swiper';
import { Swiper, SwiperSlide } from 'swiper/vue';

SwiperCore.use([ Navigation ]);

export default defineComponent({
  components: {
    UChip,
    UButton,
    Swiper,
    SwiperSlide
  },
  props: {
    resetter: { required: true, type: Function },
    customizationDiff: { required: true, type: Array },
    customization: { required: true, type: Object }
  },
  data() {
    return {
      ready: false
    }
  },
  mounted() {
    this.ready = true;
  }
})
</script>

<style>@import '~swiper/components/navigation/navigation.min.css';</style>
<style lang="less" scoped>
  .ui-chip {
    background: #F0EEF9;
    color: @col-blue;

    &::v-deep .svg-icon--cross { fill: @col-blue; }
  }
  .swiper-slide { width: auto; }
  button.ui-btn.swiper-chips-prev,
  button.ui-btn.swiper-chips-next {
    position: absolute;
    background: @col-bg;
    top: -10px;
    z-index: 2;
    transition: opacity .3s ease, visibility .3s ease;
    box-shadow: 0 0 10px 2px @col-bg;
    cursor: pointer;

    &.swiper-button-disabled {
      opacity: 0;
      visibility: hidden;
      cursor: default;
    }
    @media @mobile { display: none; }
    &:hover, &:focus { background: @col-bg; }
  }
  button.ui-btn.swiper-chips-prev {
    left: -10px;
    transform: rotate(-90deg);
  }
  button.ui-btn.swiper-chips-next {
    right: -10px;
    transform: rotate(90deg);
  }
</style>