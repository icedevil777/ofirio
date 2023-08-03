<template>
  <div class="find-investment-component">
    <UPageHeader :wavePosition="wavePosition">
      <div class="title-block">
        <UIcon class="hide-mobile" name="rounded-arrow" />
        <h1 class="title">Find an Investment Property in Seconds</h1>
        <span class="text">AI-powered solution to help you easily find the best deals</span>
      </div>
      <div class="radio-select">
        <URadioChip class="radio-1" v-model="searchType" name="find-investment-component-radio" value="find-investment">Investment Finder</URadioChip>
        <URadioChip class="radio-2" v-model="searchType" name="find-investment-component-radio" value="rent-estimate" @click="() => $router.push({ name: 'rent-estimator'})">Rent Analyzer</URadioChip>
      </div>
      <div class="input-block flex">
        <SearchComponent :syncWith="$root.$refs.header.$refs.headerSearch">
          <template v-slot:postpend="{ useFirst }" v-if="!$isMobile.value">
            <UButton class="ui-btn ui-btn-green" @click="useFirst"><span class="hide-mobile">Search</span></UButton>
          </template>
        </SearchComponent>
      </div>
      <div class="ai-powered flex">
        <img class="ai-powered-icon" src="@/assets/icons/ai-powered.svg" alt="ai-powered">
        <span>AI powered</span>
      </div>
    </UPageHeader>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import UPageHeader from '@/components/ui/UPageHeader.vue'
import UButton from '@/components/ui/UButton.vue';
import URadioChip from '@/components/ui/URadioChip.vue';
import SearchComponent from '@/components/Search/SearchComponent.vue';

export default defineComponent({
  components: {
    UPageHeader,
    UButton,
    URadioChip,
    SearchComponent
  },
  props: {
    wavePosition: { type: String, default: 'bottom' }
  },
  data() {
    return {
      searchType: 'find-investment'
    }
  }
})
</script>

<style lang="less" scoped>
  .static-page-header {
    text-align: center;
    background-image: url("../../assets/images/static/common/find-investment-header-bg.png");
    display: flex;

    @media @mobile {
      &::v-deep {
        .wrapper { padding: 5vh 20px; }
      }
    }
  }
  .title-block {
    position: relative;
    margin-bottom: 40px;

    .svg-icon {
      @s: 100px;

      position: absolute;
      left: -20px;
      bottom: calc(-1 * @s * 0.7);
      width: @s;
      height: @s;
      fill: @col-text-light;
    }

    .title {
      font-size: 3.125rem;
      font-weight: 800;
      color: @col-text-light;
      margin-bottom: 25px;
    }

    .text {
      font-size: 1.25rem;
      font-weight: 600;
      line-height: 2rem;
      color: @col-text-light;
    }

    @media @mobile {
      margin-bottom: 30px;

      .title {
        font-size: 2.3rem;
        line-height: 2.7rem;
        margin-bottom: 20px;
      }
      .text { font-size: 1.2rem; }
    }
  }

  .radio-select {
    background: @col-bg;
    width: fit-content;
    padding: 6px;
    margin: 0 auto;
    border-radius: 80px;

    .ui-radio-chip {
      margin: 0 auto;
      background: @col-text-light;
      color: @col-text-gray-dark;
      font-weight: 700;
      box-shadow: none;
      transition: none;
      font-size: 0.875rem;
      padding: 4px 20px;
      height: 100%;

      &.selected {
        background: @col-green;
        color: @col-text-light;
        border-radius: 80px;

        &::after {
          @s: 14px;

          content: '';
          position: absolute;
          width: @s;
          height: @s;
          background-color: @col-green;
          transform: rotate(45deg);
          bottom: -7px;
          left: calc(50% - @s/2);
        }
      }
      @media @mobile {
        padding: 2px 12px;
        font-size: 1rem;
      }
    }
  }

  .input-block {
    @p: 10px;
    @h: 70px;

    margin: 20px 0 30px;
    text-align: left;
    box-shadow: 0px 15px 45px rgba(0, 0, 0, 0.25);
    border-radius: @border-radius;
    background: @col-bg;

    .search-component::v-deep {
      width: 100%;

      .input-wrapper {
        height: @h;
        padding: @p @p @p 15px;
        background: @col-bg;

        .ui-btn {
          height: @h - 2*@p;
          min-width: 200px;
        }

        .svg-icon--magnifier {
          @s: 40px;

          background: @col-green;
          width: @s;
          min-width: @s;
          height: @s;
          min-height: @s;
          padding: 13px;
          border-radius: @border-radius;
          stroke: @col-bg;
          box-shadow: @btn-shadow @col-shadow;

          @media @mobile {

          }
        }
      }
      .suggestion-list { padding-top: @h; }
    }

    @media @mobile {
      @h: 50px;
      height: @h;
      margin: 15px 0 20px;

      .search-component::v-deep {
        .input-wrapper {
          height: @h;
          
          .svg-icon--magnifier {
            @s: 36px;

            width: @s;
            min-width: @s;
            height: @s;
            min-height: @s;
            padding: 11px;
          }
        }
        .suggestion-list { padding-top: @h; }

        &.active .svg-icon--magnifier {
          background: transparent;
          stroke: @col-text-dark;
          box-shadow: none;
        }
      }
    }
  }

  .ai-powered {
    align-items: center;
    justify-content: center;
    color: @col-text-light;
    text-transform: uppercase;
    font-weight: 700;
    font-size: 0.75rem;

    .ai-powered-icon {
      @s: 1.4rem;

      width: @s;
      height: @s;
      margin-right: 6px;
    }
  }
</style>