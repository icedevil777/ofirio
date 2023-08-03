/**
 * @usage:
 *
 *   <UTextInput value="value_name" name="input_name" v-model="model">Label</UTextInput>
 *
 */

<template>
  <div class="ui-histogram-slider">
    <div class="ui-histogram">
      <vue3-chart-js
          type="bar"
          :data="data"
          :options="opt"
          @beforeLayout="checkChartSize"
          ref="chartRef"
      ></vue3-chart-js>
    </div>
    <USlider
      v-bind="$attrs"
      :tooltips="false"
    />
  </div>
</template>


<style lang="less" scoped>
  .ui-histogram-slider {
    .ui-histogram {
      width: calc(100% - 24px);
      margin-bottom: 10px;
      margin-left: auto;
      margin-right: auto;
      height: 80px;
    }
  }
</style>


<script lang="ts">
import Vue3ChartJs from '@j-t-mcc/vue3-chartjs'
import { defineComponent } from 'vue';
import USlider from './USlider.vue';

const BAR_THICKNESS = 3;
const BAR_MARGIN = 1;

const BAR_BG = '#E5E5E5';
const BAR_HL = '#6454C2';

export default defineComponent({
  components: {
    USlider,
    Vue3ChartJs
  },
  props: {
    histArray: { type: Array, required: true },
    processArray: Boolean
  },
  data() {
    return {
      __chartSize: null as null|number,
      opt: {
        animation: false,
        interaction: { enabled: false },
        plugins: {
          legend: false,
          title: { display: false }
        },
        maintainAspectRatio: false,
        scales: {
          x: { display: false, grid: { display: false, drawBorder: false, drawTicks: false } },
          y: { display: false, grid: { display: false, drawBorder: false, drawTicks: false } }
        },
        hover: { mode: false }
      },
      data: {
        labels: [],
        datasets: [
          {
            backgroundColor: '#00D8FF',
            borderRadius: Number.MAX_VALUE,
            borderSkipped: false,
            barThickness: 3,
            data: []
          }
        ]
      }
    }
  },
  watch: {
    /* TODO:Perf. improoving: chart.js remove? use own svg-generator? use two static histograms with upper css-clip? */
    histArray: function () {
      this.updateChart();
    },
    '$attrs.modelValue': function () {
      this.updateChart();
    }
  },
  methods: {
    checkChartSize() {
      const ref:any = this.$refs.chartRef;
      if (!ref)
        return;

      const width = <number>ref.$el.width;
      if (this.__chartSize == null || this.__chartSize != width) {
        this.__chartSize = width;

        if (this.data.datasets[0].data.length > 0)
          this.updateChart();
      }
    },
    updateChart() {
      const ref:any = this.$refs.chartRef;
      if (!ref)
        return;

      let dataArray = this.histArray;
      if (this.processArray === true) {

        const width = this.__chartSize;
        if (!width)
          return;

        const chunkCount = Math.ceil((width - BAR_MARGIN) / (BAR_THICKNESS + BAR_MARGIN));
        const chunkSize = Math.ceil(this.histArray.length / chunkCount);

        let acc = 0;
        dataArray = [];
        for (let i = 0; i < this.histArray.length; i++) {
          if (i !== 0 && i % chunkSize == 0) {
            dataArray.push(acc);
            acc = 0;
          }
          acc += <number>this.histArray[i];
        }
        dataArray.push(acc);
      }
      
      const maxMinDiff = <number>this.$attrs.max - <number>this.$attrs.min + 1;
      const leftHandle = (<number>(<any>this.$attrs.modelValue)[0] - <number>this.$attrs.min) / maxMinDiff;
      const rightHandle = (<number>(<any>this.$attrs.modelValue)[1] - <number>this.$attrs.min) / maxMinDiff;

      const bgColors = dataArray.map((e, i, arr) => {
        const pct = i / arr.length;
        return pct >= leftHandle && pct <= rightHandle ? BAR_HL : BAR_BG;
      });

      this.data.labels = <any>dataArray.map(e => '');
      this.data.datasets = [
        {
          backgroundColor: <any>bgColors,
          borderRadius: Number.MAX_VALUE,
          borderSkipped: false,
          barThickness: BAR_THICKNESS,
          data: <any>dataArray
        }
      ];
      ref.update(0);
    }
  },
  mounted() {
    this.updateChart();
  }
});
</script>