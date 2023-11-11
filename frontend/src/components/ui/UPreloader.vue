<template>
  <div class="ui-preloader" :style="style" v-if="active">
    <div class="ui-preloader-content">
      <div class="ui-preloader-block" v-for="c of preloader.children" :key="c" :style="c"></div>
    </div>
  </div>
  <slot v-else></slot>
</template>

<script lang="ts">
import { ComputedRef, defineComponent, PropType } from 'vue';

const DSizes:Record<string, any> = {
  'simple': {
    ratio: 'auto',
    children: [
      { top: 0, left: 0, width: '100%', height: '100%' }
    ]
  },
  '2to1': {
    ratio: 2,
    children: [
      { top: 0, left: 0, width: '100%', height: '100%' }
    ]
  },
  'searchResults': {
    ratio: 10,
    children: [
      { top: 0, left: 0, width: '250px', height: '32px' }
    ]
  },
  'propertyCard': {
    ratio: 'auto',
    styles: {
      'height': '117.25px'
    },
    children: [
      { top: 0, left: 0, width: '190px', height: '100%', 'border-radius': '8px' },

      { top: 0, left: '210px', width: '60%', height: '20px' },
      { top: '25px', left: '210px', width: '40%', height: '20px' },

      { top: '70px', left: '210px', width: '95px', height: '25px' },
      { bottom: '0', left: '210px', width: '95px', height: '15px' },

      { top: '70px', left: '315px', width: '95px', height: '25px' },
      { bottom: '0', left: '315px', width: '95px', height: '15px' },

      { top: '70px', left: '420px', width: '95px', height: '25px' },
      { bottom: '0', left: '420px', width: '95px', height: '15px' },

      { top: '70px', left: '525px', width: '95px', height: '25px' },
      { bottom: '0', left: '525px', width: '95px', height: '15px' }
    ]
  },
  'propertyCard__mobile': {
    ratio: 'auto',
    styles: {
      'height': '125px'
    },
    children: [
      { top: 0, left: '20px', width: '125px', height: '100%', 'border-radius': '8px' },

      { top: 0, left: '165px', width: '50%', height: '40px' },
      { top: '45px', left: '165px', width: '50%', height: '15px' },

      { bottom: '15px', left: '165px', width: '15%', height: '15px' },
      { bottom: '0', left: '165px', width: '15%', height: '10px' },

      { bottom: '15px', left: 'calc(165px + 18%)', width: '15%', height: '15px' },
      { bottom: '0', left: 'calc(165px + 18%)', width: '15%', height: '10px' },

      { bottom: '15px', left: 'calc(165px + 36%)', width: '15%', height: '15px' },
      { bottom: '0', left: 'calc(165px + 36%)', width: '15%', height: '10px' },
    ]
  },
  'charsRow': {
    ratio: 7.5,
    children: [
      { top: '0', left: '0', width: '90px', height: '15px' },
      { top: '20px', left: '0', width: '90px', height: '30px' },

      { top: '0', left: '100px', width: '90px', height: '15px' },
      { top: '20px', left: '100px', width: '90px', height: '30px' },

      { top: '0', left: '200px', width: '90px', height: '15px' },
      { top: '20px', left: '200px', width: '90px', height: '30px' },

      { top: '0', left: '300px', width: '90px', height: '15px' },
      { top: '20px', left: '300px', width: '90px', height: '30px' },
    ]
  },
  'charsRow__mobile': {
    ratio: 'auto',
    styles: {
      height: '38px',
      'margin-bottom': '20px'
    },
    children: [
      { top: '0', left: '0', width: '22%', height: '35%' },
      { bottom: '0', left: '0', width: '22%', height: '55%' },

      { top: '0', left: '26%', width: '22%', height: '35%' },
      { bottom: '0', left: '26%', width: '22%', height: '55%' },

      { top: '0', left: '52%', width: '22%', height: '35%' },
      { bottom: '0', left: '52%', width: '22%', height: '55%' },

      { top: '0', left: '78%', width: '22%', height: '35%' },
      { bottom: '0', left: '78%', width: '22%', height: '55%' },
    ]
  },
  'propertyAddress': {
    ratio: 10,
    children: [
      { top: '0', left: '0', width: '100%', height: '60%' },
      { top: '70%', left: '0', width: '90%', height: '30%' },
    ]
  },
  'propertyAddress__mobile': {
    ratio: 'auto',
    styles: {
      height: '52px'
    },
    children: [
      { top: '0', left: '5%', width: '90%', height: '60%' },
      { top: '70%', left: '5%', width: '50%', height: '30%' },
    ]
  },
  'breadcrumbs': {
    ratio: 11.1,
    children: [
      { top: '20%', left: '0', width: '100%', height: '50%' },
    ]
  },
  'breadcrumbs__mobile': {
    ratio: 'auto',
    styles: {
      height: '14px'
    },
    children: [
      { top: '0', left: '5%', width: '90%', height: '100%' },
    ]
  },
  'propertyImages': {
    ratio: 1.27,
    children: [
      { top: '0', left: '0', width: '100%', height: '100%', 'border-radius': '8px' },
    ]
  },
  'propertyImages__mobile': {
    ratio: 'auto',
    styles: {
      height: '230px',
      'margin-bottom': '20px'
    },
    children: [
      { top: '0', left: '0', width: '100%', height: '100%'},
    ]
  },
  'smallPropsTable': {
    ratio: 4.75,
    children: [
      { top: '0', left: '0', width: '100%', height: '80%' },
    ]
  },
  'slider': {
    ratio: 60,
    children: [
      { top: '0', left: '0', width: '100%', height: '100%' },
    ]
  },
  'sliderInfo': {
    ratio: 4,
    children: [
      { top: '0', left: '0', width: '100%', height: '100%' },
    ]
  },
  'tabs': {
    ratio: 3.3,
    children: [
      { top: '25%', left: '0', width: '15%', height: '50%', 'border-radius': '8px' },
      { top: '25%', left: '22%', width: '15%', height: '50%', 'border-radius': '8px' },
      { top: '25%', left: '44%', width: '15%', height: '50%', 'border-radius': '8px' },
      { top: '25%', left: '66%', width: '15%', height: '50%', 'border-radius': '8px' },
    ]
  },
  'tabs__mobile': {
    ratio: 'auto',
    styles: {
      height: '70px',
      margin: '50px 0 30px'
    },
    children: [
      { bottom: '0', left: '5%', width: '18%', height: '100%', 'border-radius': '8px' },
      { bottom: '0', left: '29%', width: '18%', height: '100%', 'border-radius': '8px' },
      { bottom: '0', left: '53%', width: '18%', height: '100%', 'border-radius': '8px' },
      { bottom: '0', left: '76%', width: '18%', height: '100%', 'border-radius': '8px' },
    ]
  },
  'basicAssumptionsTitle': {
    ratio: 6,
    children: [
      { top: '0', left: '0', width: '100%', height: '70%' },
    ]
  },
  'basicAssumptionsTitle__mobile': {
    ratio: 'auto',
    styles: {
      height: '20px',
      'margin-bottom': '1.25rem'
    },
    children: [
      { top: '0', left: '5%', width: '60%', height: '100%' },
    ]
  },
  'basicAssumptionsInputs': {
    ratio: 13,
    children: [
      { top: '0', left: '0', width: '15%', height: '70%', 'border-radius': '8px' },
      { top: '0', left: '17%', width: '15%', height: '70%', 'border-radius': '8px' },
      { top: '0', left: '34%', width: '15%', height: '70%', 'border-radius': '8px' },
      { top: '0', left: '51%', width: '15%', height: '70%', 'border-radius': '8px' },
      { top: '0', left: '68%', width: '15%', height: '70%', 'border-radius': '8px' },
      { top: '0', left: '85%', width: '15%', height: '70%', 'border-radius': '8px' },
    ]
  },
  'basicAssumptionsInputs__mobile': {
    ratio: 'auto',
    styles: {
      height: '200px',
      'margin-bottom': '2rem'
    },
    children: [
      { top: '0', left: '5%', width: '44%', height: '32%', 'border-radius': '8px' },
      { top: '0', left: '51%', width: '44%', height: '32%', 'border-radius': '8px' },
      { top: '34%', left: '5%', width: '44%', height: '32%', 'border-radius': '8px' },
      { top: '34%', left: '51%', width: '44%', height: '32%', 'border-radius': '8px' },
      { top: '68%', left: '5%', width: '44%', height: '32%', 'border-radius': '8px' },
      { top: '68%', left: '51%', width: '44%', height: '32%', 'border-radius': '8px' },
    ]
  },
  'finDetails': {
    ratio: 1.125,
    children: [
      { top: '0', left: '0', width: 'calc(50% - 20px)', height: '560px', 'border-radius': '8px' },
      { top: '0', right: '0', width: 'calc(50% - 20px)', height: '560px', 'border-radius': '8px' },
      { top: '600px', left: '0', width: '100%', height: '468px', 'border-radius': '8px' },
    ]
  },
  'finDetails__mobile': {
    ratio: 'auto',
    styles: {
      height: '1500px'
    },
    children: [
      { top: '0', left: '5%', width: '90%', height: '32%', 'border-radius': '8px' },
      { top: '34%', right: '5%', width: '90%', height: '32%', 'border-radius': '8px' },
      { top: '68%', left: '5%', width: '90%', height: '32%', 'border-radius': '8px' },
    ]
  },
  'proForma': {
    ratio: 2,
    children: [
      { top: '50px', left: '0', width: '100%', height: '555px', 'border-radius': '8px' },
    ]
  },
  'proForma__mobile': {
    ratio: 'auto',
    styles: {
      height: '500px',
      'margin-top': '50px'
    },
    children: [
      { top: '0', left: '5%', width: '90%', height: '100%', 'border-radius': '8px' },
    ]
  },
  'emailSettings': {
    ratio: 10,
    styles: {
      'min-height': '26px'
    },
    children: [
      { top: '0', left: '0', width: '100%', height: '26px', 'border-radius': '8px' },
    ]
  },
  'favorites': {
    ratio: 18,
    styles: {
      'margin-bottom': '40px',
      'margin-top': '20px',
      'min-height': '80px'
    },
    children: [
      { top: '0', left: '0', width: '100px', height: '100%', 'border-radius': '8px' },
      { top: '0', left: '120px', width: '25%', height: '25%' },
      { top: '35%', left: '120px', width: '15%', height: '20%' },
      { top: '75%', left: '120px', width: '10%', height: '25%' },

      { top: '15%', right: '8%', width: '10%', height: '75%', 'border-radius': '8px' },
      { top: '15%', right: '20%', width: '10%', height: '75%', 'border-radius': '8px' },
      { top: '15%', right: '32%', width: '10%', height: '75%', 'border-radius': '8px' },
      { top: '15%', right: '44%', width: '10%', height: '75%', 'border-radius': '8px' },
    ]
  },
  'favorites__mobile': {
    ratio: 3,
    styles: {
      'margin-bottom': '60px',
      'margin-top': '20px',
      'min-height': '140px'
    },
    children: [
      { top: '0', left: '0', width: '70px', height: '70px', 'border-radius': '8px' },
      { top: '0', left: '90px', width: '60%', height: '20%' },
      { top: '25%', left: '90px', width: '50%', height: '10%' },

      { bottom: 0, left: 0, width: '20%', height: '30%', 'border-radius': '8px' },
      { bottom: 0, left: '26%', width: '20%', height: '30%', 'border-radius': '8px' },
      { bottom: 0, left: '52%', width: '20%', height: '30%', 'border-radius': '8px' },
      { bottom: 0, left: '78%', width: '20%', height: '30%', 'border-radius': '8px' },
    ]
  },
  'reportsHeadings': {
    ratio: 18,
    children: [
      { top: '20px', left: '30px', width: '10%', height: '30px' },
      { top: '20px', left: 'calc(30px + 20%)', width: '10%', height: '30px' },
      { top: '20px', left: 'calc(30px + 40%)', width: '10%', height: '30px' },
      { top: '20px', left: 'calc(30px + 60%)', width: '10%', height: '30px' },
    ]
  },
  'reportsFilters': {
    ratio: 'auto',
    styles: {
      'height': '60px'
    },
    children: [
      { top: '20px', left: '30px', width: '5%', height: '50%', 'border-radius': '15px' },
      { top: '20px', left: 'calc(40px + 5%)', width: '10%', height: '50%', 'border-radius': '15px' },
      { top: '20px', left: 'calc(50px + 15%)', width: '10%', height: '50%', 'border-radius': '15px' },
    ]
  },
  'reportsFilters__mobile': {
    ratio: 'auto',
    styles: {
      'height': '60px'
    },
    children: [
      { top: '20px', left: '20px', width: '20%', height: '50%', 'border-radius': '15px' },
      { top: '20px', left: 'calc(30px + 20%)', width: '35%', height: '50%', 'border-radius': '15px' },
      { top: '20px', left: 'calc(40px + 55%)', width: '30%', height: '50%', 'border-radius': '15px' },
    ]
  },
  'reports': {
    ratio: 23,
    children: [
      { top: '0', left: '30px', width: '10%', height: '20px' },
      { top: '0', left: 'calc(30px + 20%)', width: '10%', height: '20px' },
      { top: '0', left: 'calc(30px + 40%)', width: '10%', height: '20px' },
      { top: '0', left: 'calc(30px + 60%)', width: '10%', height: '20px' },
      { top: '0', left: 'calc(30px + 80%)', width: '10%', height: '20px' },
    ]
  },
  'reports__mobile': {
    ratio: 'auto',
    styles: {
      'height': '120px',
      'margin-bottom': '20px'
    },
    children: [
      { top: '0', left: '20px', width: '30%', height: '10%', },
      { bottom: '0', left: '20px', width: '40%', height: '80%', 'border-radius': '8px' },
      { bottom: '0', right: '20px', width: '40%', height: '80%', 'border-radius': '8px' },
    ]
  },
  


};

export default defineComponent({
  props: {
    activation: { required: true, type: [Promise, Boolean] as PropType<Promise<any> | boolean> },
    livePromise: Promise,
    mode: { required: true, type: String },
    width: { default: 100, type: Number }
  },
  computed: {
    preloader():Record<string, any> {
      if ((<any>this).$isMobile.value && DSizes[this.mode + '__mobile'])
        return DSizes[this.mode + '__mobile'];
      return DSizes[this.mode];
    },
    style(): Record<string, any> {
      let styles:Record<string, any> = {};

      if (this.preloader.ratio > 1)
        styles = { width: this.width + '%', 'padding-bottom': this.width / this.preloader.ratio + '%' };
      if (this.preloader.ratio <= 1)
        styles = { width: this.width + '%', 'padding-bottom': this.width * this.preloader.ratio + '%' };

      return Object.assign({}, styles, this.preloader.styles);
    }
  },
  data() {
    return {
      active: true,
      promise: undefined as Promise<any> | undefined
    }
  },
  watch: {
    livePromise(newPromise) {
      this.promiseWatch(newPromise);
    },
    activation() {
      this.checkActivation();
    }
  },
  methods: {
    checkActivation() {
      if (this.activation instanceof Promise)
        this.promiseWatch(this.activation);
      else
        this.active = this.activation;
    },
    promiseWatch(promise: Promise<any>) {
      this.active = true;
      this.promise = promise;
      promise.finally(() => {
        if (this.promise == promise)
          this.active = false
      });
    }
  },
  mounted() {
    this.checkActivation();
  }
})
</script>

<style lang="less" scoped>

@keyframes placeholderAnimate {
    0%{ background-position: -650px 0; }
    100%{ background-position: 650px 0; }
}

.ui-preloader {
  width: 100%;
  position: relative;
  height: 0;

  .ui-preloader-content {
    position: absolute;
    overflow: hidden;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;

    .ui-preloader-block {
      position: absolute;
      animation-duration: 1.3s;
      animation-fill-mode: forwards;
      animation-iteration-count: infinite;
      animation-timing-function: ease-in-out;
      animation-name: placeholderAnimate;
      background: #f6f7f8; // Fallback
      background: linear-gradient(to right, #eee 2%, #ddd 18%, #eee 33%);
      background-size: 1300px; // Animation Area
      border-radius: @border-radius/2;
    }
  }
}
</style>