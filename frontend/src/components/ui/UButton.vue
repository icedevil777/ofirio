/**
 * @usage:
 *
 *   <UTextInput value="value_name" name="input_name" v-model="model">Label</UTextInput>
 *
 */

<template>
  <button class="ui-button" :class="{ busy: activeBusy }" type="button" v-if="$attrs.href == undefined" v-bind="$attrs"><slot></slot></button>
  <a class="ui-button" v-else-if="$attrs.href != undefined" v-bind="$attrs"><slot></slot></a>
</template>


<style lang="less" scoped>
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
.ui-button {
  background: transparent;
  border: none;
  outline: none;

  &[disabled], &.disabled { cursor: not-allowed; }
  &.ui-btn-iconic {
    display: inline-flex;
    align-items: center;
    justify-items: flex-start;

    &::v-deep > .svg-icon {
      @s: 20px;
      width: @s;
      height: @s;
      margin-right: @s/4;
    }
  }


  &.ui-btn-text {
    color: @col-blue;
    fill: @col-blue;
    font-weight: bold;
    transition: color ease .2s;
    padding: 0;
    margin: 0;

    &:hover, &:focus {
      color: @col-blue-dark;
      fill: @col-blue-dark;
    }
    &:active {
      color: darken(@col-blue-dark, 10%);
      fill: darken(@col-blue-dark, 10%);
    }
    &[disabled], &.disabled {
      color: @col-blue-light;
      fill: @col-blue-light;
    }
  }
  &.ui-btn-text-black {
    color: @col-text-dark;
    fill: @col-text-dark;
    font-weight: bold;
    transition: color ease .2s;

    &[disabled], &.disabled {
      color: @col-text-gray-dark;
      fill: @col-text-gray-dark;
    }
  }
  &.ui-btn-text-gray {
    color: @col-text-gray-dark;
    fill: @col-text-gray-dark;
    font-weight: bold;
    transition: color ease .2s;

    &:hover, &:focus {
      color: @col-text-gray-dark;
      fill: @col-text-gray-dark;
    }
    &:active {
      color: darken(@col-text-gray-dark, 10%);
      fill: darken(@col-text-gray-dark, 10%);
    }
    &[disabled], &.disabled {
      color: @col-text-gray-light;
      fill: @col-text-gray-light;
    }
  }


  &.ui-btn {
    padding: 8px 20px;
    border: 2px solid transparent;
    border-radius: @border-radius;
    text-align: center;
    color: @col-text-light;
    transition: color ease .2s, background-color ease .2s;
    font-weight: 700;

    &:not(.ui-btn-circle, .ui-btn-iconic) {
      position: relative;

      &:before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: inherit;
        border-radius: inherit;
      }
      &:after {
        @s: 1rem;
        @bs: 1.5px;

        content: '';
        position: absolute;
        top: calc(50% - @s/2 - @bs);
        left: calc(50% - @s/2 - @bs);
        width: @s;
        height: @s;
        border-radius: 50%;
        border: @bs solid transparent;
        border-left-color: #fff;
        animation-duration: .65s;
        animation-fill-mode: forwards;
        animation-iteration-count: infinite;
        animation-timing-function: linear;
        animation-name: spin;
      }
      &:before, &:after {
        opacity: 0;
        visibility: hidden;
        transition: .25s ease;
      }
      &.busy {
        &:before, &:after {
          visibility: visible;
          opacity: 1;
        }
      }
    }
    &.ui-btn-iconic { justify-content: center; }
  }
  &.ui-btn-green {
    background: @col-green;
    box-shadow: @btn-shadow @col-shadow;

    &:hover, &:focus { background: @col-green-dark; }
    &:active { background: darken(@col-green-dark, 10%); }
    &[disabled], &.disabled { background: @col-green-light; }
  }
  &.ui-btn-white {
    background: @col-bg;
    box-shadow: @btn-shadow @col-shadow;
    color: @col-text-dark;

    &:hover, &:focus { background: lighten(@col-gray-light, 15%); }
    &:active { background: @col-gray-light; }
    &[disabled], &.disabled { background: @col-gray-light; }
  }
  &.ui-btn-blue {
    background: @col-blue;
    box-shadow: @btn-shadow @col-shadow;

    &:hover, &:focus { background: @col-blue-dark; }
    &:active { background: darken(@col-blue-dark, 10%); }
    &[disabled], &.disabled { background: @col-blue-light; }
  }
  &.ui-btn-bordered {
    background: transparent;
    border-color: @col-text-dark;
    color: @col-text-dark;

    &.busy, &:before { background: @col-text-dark; }
    &:after { border-left-color: @col-text-light; }

    &:hover, &:focus, &:active { color: @col-text-light; }
    &:before, &:hover, &:focus { background: @col-text-dark; }
    &:active { background: darken(@col-text-dark, 10%); }
    &[disabled], &.disabled {
      color: @col-text-gray-darker;
      background: transparent;
      border-color: @col-text-gray-darker;
    }
  }
  &.ui-btn-bordered-green {
    background: transparent;
    border-color: @col-green;
    color: @col-green;

    &.busy, &:before { background: @col-green; }

    &:hover, &:focus, &:active { color: @col-text-light; }
    &:hover, &:focus {
      background: @col-green-dark;
      border-color: @col-green-dark;
    }
    &:active { background: darken(@col-green-dark, 10%); }
    &[disabled], &.disabled {
      color: @col-text-gray-darker;
      background: transparent;
      border-color: @col-text-gray-darker;
    }
  }
  &.ui-btn-bordered-blue {
    background: transparent;
    border-color: @col-blue;
    color: @col-blue;

    &.busy, &:before { background: @col-blue; }

    &:hover, &:focus, &:active { color: @col-text-light; }
    &:hover, &:focus {
      background: @col-blue-dark;
      border-color: @col-blue-dark;
    }
    &:active { background: darken(@col-blue-dark, 10%); }
    &[disabled], &.disabled {
      color: @col-text-gray-darker;
      background: transparent;
      border-color: @col-text-gray-darker;
    }
  }
  &.ui-btn-bordered-gray {
    background: transparent;
    border-color: @col-gray;
    border-width: 1px;
    color: @col-text-dark;
    transition: color ease .2s, background-color ease .2s, border-color ease .2s;

    &.busy, &:before { background: @col-gray; }
    &:after { border-left-color: @col-text-dark; }

    &:hover, &:focus, &:active { background: lighten(@col-gray, 12%); }
    &:hover, &:focus { border-color: @col-text-dark; }
    &:active { background: lighten(@col-gray, 8%); }
    &[disabled], &.disabled {
      color: @col-text-gray-darker;
      background: transparent;
      border-color: @col-text-gray-darker;
    }
  }


  &.ui-btn-circle {
    @s: 50px;
    width: @s;
    height: @s;
    border-radius: 50%;
    border: none;
    box-shadow: @btn-circle-shadow @col-shadow;
    fill: @col-text-gray-dark;
    transition: fill ease .2s, background-color ease .2s;
    background: @col-bg;
    padding: 0;

    &::v-deep .svg-icon {
      fill: inherit;
      width: @s/2 - 10px;
      height: @s/2 - 10px;
      margin: 0;
    }
    &:hover, &:focus { background: @col-disabled; }
    &:active { fill: @col-text-dark; }
  }
  &.ui-btn-circle-on-dark {
    box-shadow: none;
    background: @col-text-gray-dark;
    fill: @col-text-light;

    &:hover, &:focus, &:active {
      background: @col-text-gray-dark;
      fill: @col-text-light;
    }
  }
}
</style>


<script lang="ts">
import { defineComponent, PropType } from 'vue';

export default defineComponent({
  props: {
    busy: { type: [Promise, Boolean] as PropType<Promise<any> | boolean | undefined> },
    busyPromise: Promise,
  },
  data() {
    return {
      activeBusy: true,
      promise: undefined as Promise<any> | undefined
    }
  },
  watch: {
    busyPromise(newPromise) {
      this.promiseWatch(newPromise);
    },
    busy() {
      this.checkActivation();
    }
  },
  methods: {
    checkActivation() {
      if (this.busy instanceof Promise)
        this.promiseWatch(this.busy);
      else
        this.activeBusy = this.busy || false;
    },
    promiseWatch(promise: Promise<any>) {
      this.activeBusy = true;
      this.promise = promise;
      promise.finally(() => {
        if (this.promise == promise)
          this.activeBusy = false
      });
    }
  },
  mounted() {
    this.checkActivation();
  }
});
</script>