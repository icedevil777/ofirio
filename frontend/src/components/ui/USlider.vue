/**
 * @usage:
 *
 *   <UTextInput value="value_name" name="input_name" v-model="model">Label</UTextInput>
 *
 */

<template>
  <div class="ui-slider" :class="[className]">
    <Slider v-bind="$attrs" @update="upd" :min="min" :max="max" :options="format" ref="slider"/>
    <div class="stopBar" v-for="(v, i) of visibleStopBars" :key="v" :style="{ left: v*100 + '%' }" :class="[ `stopBar-${i}` ]"></div>
    <!-- <div class="percentiles flex" v-if="showPercentiles">
      <span class="percentile ui-text-left">25th Percentile</span>
      <span class="percentile ui-text-center"></span>
      <span class="percentile ui-text-right">75th Percentile</span>
    </div> -->
    <div class="percentiles flex" v-if="showPercentiles && percetileMode == 'estimatedRent'">
      <span class="percentile ui-text-center">Estimated Rent</span>
    </div>
  </div>
</template>


<style lang="less" scoped>
  .ui-slider {
    @col-slider-bg: #e4e4e4;

    width: calc(100% - 24px);
    margin-left: auto;
    margin-right: auto;
    position: relative;

    .stopBar {
      @h: 20px;
      @w: 3px;

      position: absolute;
      top: 3px - @h/2;
      border-radius: @w/2;
      height: @h;
      width: @w;
      background: @col-slider-bg;
    }
    .percentiles {
      width: 100%;
      margin-top: 15px;
      font-size: .75rem;
      color: @col-text-gray-darker;
      justify-content: space-between;
      align-content: center;
      align-items: center;

      .percentile { flex: 1; }
    }
    &::v-deep {
      .slider-base { background: @col-slider-bg; }
      .slider-connect { background: @col-blue; }
      .slider-handle {
        @s: 26px;
        width: @s;
        height: @s;
        top: -@s/2 + 2px;
        right: -@s/2;

        &:before {
          @ps: 10px;
          @bs: 1px;
          content: '';
          position: absolute;
          top: @s/2 - @ps/2 - @bs;
          left: @s/2 - @ps/2 - @bs;
          border-radius: 50%;
          width: 10px;
          height: 10px;
          background: transparent;
          border: 1px solid @col-text-gray;
          transition: background-color .2s ease;
        }
        &.slider-active:before { background: @col-blue; }
      }
    }
  }
</style>


<script lang="ts">
import { defineComponent } from 'vue';
import '@vueform/slider/themes/default.css';
import Slider from '@vueform/slider';

const EPS = 1e-5;

export default defineComponent({
  props: {
    stops: Array,
    stopBuffer: Number,
    stopsVisible: Array,
    min: Number,
    max: Number,
    showPercentiles: Boolean,
    percetileMode: String,
    className: String,
    prefix: String
  },
  components: {
    Slider
  },
  computed: {
    range():number {
      if (this.$props.max != undefined && this.$props.min != undefined)
        return this.$props.max - this.$props.min;
      
      return 0;
    },
    stopsValues():Array<number> {
      if (!this.$props.stops)
        return [];

      return this.$props.stops.map((v:any) => v * this.range + <number>this.$props.min);
    },
    visibleStopBars():Array<number> {
      if (this.$props.stopsVisible == undefined)
        return <any>this.$props.stops;
      
      return (<any>this.$props.stops).filter((v:any, i:number) => (<any>this.$props.stopsVisible)[i]);
    },
    stopButterValue():number {
      if (this.stopBuffer == undefined)
        return 0.01 * this.range;
      return <number>this.stopBuffer;
    }
  },
  data() {
    return {
      attrs: null as null | object,

      stickedTo: [NaN, NaN],

      // TODO: Move to setup (or created)
      format: {
        format: {
          to (v:number) {
            return v.toString();
          },
          from (v:string) {
            return Number(v);
          }
        }
      }
    }
  },
  methods: {
    upd(value:any) {
      if (Array.isArray(value))
        value.forEach((val, i, arr) => {
          for (let stop of this.stopsValues) {
            const diff = Math.round(Math.abs(val - stop) * 10000) / 10000;
            if (diff < this.stopButterValue && diff > EPS) {
              arr[i] = stop;
              this.stickedTo[i] = stop;
              return;
            }
          }
          this.stickedTo[i] = NaN;
        });

      else {
        for (let stop of this.stopsValues) {
          const diff = Math.round(Math.abs(value - stop) * 10000) / 10000;
          if (diff < this.stopButterValue && diff > EPS) {
            if (this.stickedTo[0] != stop) {
              this.stickedTo[0] = stop;
              (<any>this.$refs.slider).update(stop);
            }
            return;
          }
        }
        this.stickedTo[0] = NaN;
      }

          
    }
  }
});
</script>