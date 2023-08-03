<template>
  <div class="ui-property-feature-block">
    <template v-if="featureName && featureValue">
      <div class="feature-header flex"><UIcon :name="icon" /> {{ featureName }}</div>
      <template v-if="isNestedFeature(featureValue)">
        <template v-for="(fsvalue, fsname) in featureValue" :key="fsname">

          <template v-if="isNestedFeature(fsvalue, true)">
            <div class="feature-section">
              <div class="feature-subheading">{{ fsname }}</div>
              <ul class="features-section-list">
                <li v-for="(fevalue, fename) in fsvalue" :key="fename">
                  <span class="title">{{ fename }}:</span>
                  <span class="value">{{ fevalue }}</span>
                </li>
              </ul>
            </div>
          </template>
          <template v-else>
            <div class="feature-section">
              <div class="feature-subheading">{{ fsname }}</div>
              <ul class="features-section-list">
                <li><span class="value">{{ fsvalue }}</span></li>
              </ul>
            </div>
          </template>


        </template>
      </template>
      <template v-else>
        <div class="feature-section">
          <ul class="features-section-list">
            <li v-for="(fevalue, fename) in featureValue" :key="fename">
              <span class="title">{{ fename }}:</span>
              <span class="value">{{ fevalue }}</span>
            </li>
          </ul>
        </div>
      </template>
    </template>
    <slot v-else></slot>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'

export default defineComponent({
  props: {
    featureName: String,
    featureValue: Object,
    icon: String
  },
  methods: {
    isNestedFeature(o: Record<string, any>, direct: boolean = false) {
      if (direct)
        return typeof o == 'object';

      const keys = Object.keys(o);
      return typeof o[keys[0]] == 'object';
    }
  }
})
</script>

<style lang="less">
.ui-property-feature-block {
  border: 1px solid @col-gray-light;
  border-radius: @border-radius;

  .feature-header {
    @h: 50px;
    
    justify-content: flex-start;
    align-items: center;
    height: @h;
    padding: 0 20px;
    background: @col-disabled;
    border-radius: @border-radius @border-radius 0 0;
    font-size: 1.125rem;
    font-weight: 700;

    .svg-icon {
      @s: 24px;

      width: @s;
      height: @s;
      margin-right: 10px;
    }
  }
  .feature-section {
    padding: 20px 20px 0;

    + .feature-section {
      border-top: 1px solid @col-gray-light;
    }
    .feature-subheading {
      font-weight: 700;
      margin-bottom: 20px;
    }
    .features-section-list {
      list-style: none;
      display: grid;
      grid-template-columns: 1fr 1fr 1fr;
      grid-template-rows: repeat(1fr);

      @media @mobile { grid-template-columns: 1fr; }

      li {
        @lh: 24px;

        margin-bottom: 20px;
        padding-left: 20px;
        position: relative;
        line-height: @lh;

        &:before {
          @s: 8px;

          content: '';
          width: @s;
          height: @s;
          border-radius: 50%;
          background: @col-gray-light;
          display: block;
          position: absolute;
          left: 0;
          top: @lh/2 - @s/2;
        }

        .title {
          color: @col-text-gray-dark;
          margin-right: 10px;
          display: inline-block;
        }
      }
    }
  }
}
</style>
