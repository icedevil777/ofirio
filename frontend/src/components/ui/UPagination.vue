<template>
  <div class="ui-pagination flex">
    <UButton class="ui-btn-text ui-btn-text-gray ui-btn-iconic ui-pagination-arrow" @click="() => incPage(-1)"><UIcon name="smooth-arrow" /></UButton>
    <template v-for="page of calcPaginators" :key="page">
      <UButton
        v-if="page != null"
        v-text="page"
        v-bind:class="{ active: page === currentPage }"
        @click="setPage(page)"
        class="ui-btn ui-btn-iconic ui-btn-circle"
      ></UButton>
      <div v-else class="ui-pagination-dot">&hellip;</div>
    </template>
    <UButton class="ui-btn-text ui-btn-text-gray ui-btn-iconic ui-pagination-arrow" @click="() => incPage(1)"><UIcon name="smooth-arrow" /></UButton>
  </div>
</template>


<style lang="less" scoped>
.ui-pagination {
  align-items: center;
  user-select: none;
  justify-content: center;

  .ui-btn { margin: 0 10px; }
  .ui-pagination-arrow {
    @s: .875rem;

    fill: @col-text-on-disabled;
    width: @s;
    min-width: @s;
    height: @s;
    min-height: @s;

    &:first-child { transform: rotate(-90deg); }
    &:last-child { transform: rotate(90deg); }
    &::v-deep .svg-icon { margin: 0 }
  }
  .ui-btn-circle {
    box-shadow: none;
    background: lighten(@col-gray, 8%);
    color: @col-text-dark;
    transition: none;

    &:hover { background: @col-gray; }
    &.active {
      background: @col-blue;
      color: @col-text-light;
    }
  }
  .ui-pagination-dot {
    width: 30px;
    text-align: center;
    font-weight: bold;
    color: @col-text-on-disabled;
  }

  @media @mobile {
    justify-content: space-between;
    padding: 0 20px;

    .ui-btn {
      width: 40px;
      height: 40px;
      margin: 0 2px;
    }
  }
}
</style>


<script lang="ts">
import { defineComponent } from 'vue';
import UButton from './UButton.vue';

export default defineComponent({
  components: {
    UButton
  },
  props: {
    modelValue: { default: [0,0], required: true },
    chunkSize: { default: 0, type: Number },
    dataCount: { required: true, default: 1 },
    startPage: { type: Number, default: 1 }
  },
  data() {
    return {
      currentPage: 1
    }
  },
  watch: {
    'currentPage': function () {
      this.emitModel();
    }
  },
  computed: <any>{
    calcPagesCount():Number {
      const newValue = this.chunkSize == 0 ? 1 : Math.ceil(this.dataCount / this.chunkSize);
      this.currentPage = 1;
      return newValue;
    },
    calcPaginators() {
      return [ // null === ... in view
        1,
        null,
        this.calcPagesCount - this.currentPage < 2 ? this.currentPage - 2 : -1,
        this.currentPage - 1,
        this.currentPage,
        this.currentPage + 1,
        this.currentPage < 2 ? this.currentPage + 2 : -1,
        null,
        this.calcPagesCount
      ]
      .filter(el => el === null || (el >= 1 && el <= this.calcPagesCount))
      .filter((el, i, arr) => el === null || (arr.indexOf(el) === i))
      .filter((el, i, arr) => el !== null || arr[i+1] - arr[i-1] > 1);
    }
  },
  methods: {
    mapRange(i:number) {
      return Math.max(1, Math.min(<number>this.calcPagesCount, i));
    },
    setPage(i:number) {
      this.currentPage = this.mapRange(i);
    },
    incPage(i:number) {
      this.currentPage = this.mapRange(this.currentPage + i);
    },
    emitModel() {
      this.$emit('update:modelValue', [
        this.chunkSize * (this.currentPage - 1),
        Math.min(this.chunkSize * this.currentPage, this.dataCount)
      ]);
    }
  },
  mounted() {
    if (this.startPage)
      this.setPage(this.startPage);
    this.emitModel();
  }
});
</script>