<template>
  <div class="questions-answers-container flex wrapper">
    <div class="title-block">
      <span class="container-intro">FAQ</span>
      <span class="title">Questions &amp; Answers</span>
      <img src="@/assets/icons/people-holding-question-colored.svg" alt="people-holding-question-colored" class="questions-image">
    </div>
    <div class="questions-block">
      <UCollapsible>
        <template v-slot:header="props">
          <UIcon v-show="!props.isOpen" name="plus" />
          <UIcon v-show="props.isOpen" name="minus" />
          <span :class="{ active: props.isOpen }">
            What is Ofirio?
          </span>
        </template>
        <template v-slot:default>
          <span class="answer">
            Ofirio provides comprehensive tools to easily find and invest in high-return properties tailored to your needs. Learn more <router-link :to="{ name: 'static-about-us'}" class="ui-href ui-href-underline">about us</router-link>.
          </span>
        </template>
      </UCollapsible>
      <UCollapsible>
        <template v-slot:header="props">
          <UIcon v-show="!props.isOpen" name="plus" />
          <UIcon v-show="props.isOpen" name="minus" />
          <span :class="{ active: props.isOpen }">
            How does Ofirio help me find great deals on properties?
          </span>
        </template>
        <template v-slot:default>
          <span class="answer">
            Ofirio utilizes machine learning to show you the best investment opportunities and provide you with the ability to filter by advanced investment criteria such as Cap Rate, Cash on Cash Return, IRR, and more.
          </span>
        </template>
      </UCollapsible>
      <UCollapsible>
        <template v-slot:header="props">
          <UIcon v-show="!props.isOpen" name="plus" />
          <UIcon v-show="props.isOpen" name="minus" />
          <span :class="{ active: props.isOpen }">
            What geographical areas does Ofirio analyze?
          </span>
        </template>
        <template v-slot:default>
          <span class="answer">
            Ofirio analyzes properties throughout the United States.
          </span>
        </template>
      </UCollapsible>
      <UCollapsible>
        <template v-slot:header="props">
          <UIcon v-show="!props.isOpen" name="plus" />
          <UIcon v-show="props.isOpen" name="minus" />
          <span :class="{ active: props.isOpen }">
            How much money do I need to start investing?
          </span>
        </template>
        <template v-slot:default>
          <span class="answer">
            The amount that you need to start investing varies depending on the property and whether you plan to pay in cash or with financing. Ofirio makes things easy - use our investment calculator to see how much money will be needed upfront. 
          </span>
        </template>
      </UCollapsible>
      <UCollapsible>
        <template v-slot:header="props">
          <UIcon v-show="!props.isOpen" name="plus" />
          <UIcon v-show="props.isOpen" name="minus" />
          <span :class="{ active: props.isOpen }">
            Can Ofirio evaluate rent prices?
          </span>
        </template>
        <template v-slot:default>
          <span class="answer">
            Ofirio uses artificial intelligence to review, analyze and compare millions of current and historical data points providing you with the most accurate rent estimates.
          </span>
        </template>
      </UCollapsible>
      <UCollapsible>
        <template v-slot:header="props">
          <UIcon v-show="!props.isOpen" name="plus" />
          <UIcon v-show="props.isOpen" name="minus" />
          <span :class="{ active: props.isOpen }">
            Can Ofirio calculate property expenses?
          </span>
        </template>
        <template v-slot:default>
          <span class="answer">
            Ofirio takes into account property taxes, HOA fees, insurance, vacancy, and other expenses - allowing you to calculate and personalize based on your investment needs.
          </span>
        </template>
      </UCollapsible>

      <UCollapsible>
        <template v-slot:header="props">
          <UIcon v-show="!props.isOpen" name="plus" />
          <UIcon v-show="props.isOpen" name="minus" />
          <span :class="{ active: props.isOpen }">
            How to get started?
          </span>
        </template>
        <template v-slot:default>
          <span class="answer">
            To get started <UButton class="ui-href ui-href-underline" @click="Account.Restrictions.canCreateAccount() && $root['ev-popup-login-open']('register')">create a free account</UButton>!
          </span>
        </template>
      </UCollapsible>
    </div>
    <UButton class="ui-btn ui-btn-green hide-desktop" @click="Account.Restrictions.canStartFreeTrial() && $root.$refs.popupUpgrade.open()">Get Started</UButton>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import UCollapsible from '@/components/ui/UCollapsible.vue';
import AccountStore from '@/models/Account';
import UButton from '@/components/ui/UButton.vue';

export default defineComponent({
  components: {
    UCollapsible,
    UButton
  },
  computed: {
    Account() {
      return AccountStore;
    }
  }
})
</script>

<style lang="less" scoped>
span { display: block; }
.questions-answers-container {
  margin-top: 80px;
  margin-bottom: 80px;

  .title-block {
    @w: 25vw;

    width: @w;
    min-width: @w;
    max-width: 40%;

    .container-intro {
      font-weight: 800;
      color: @col-text-gray-light;
      text-transform: uppercase;
      margin-bottom: 20px;
    }
    .title {
      font-size: 2.25rem;
      font-weight: 800;
      line-height: 2.6rem;
    }
    .questions-image {
      margin-top: 40px;
      width: @w;
      max-width: 100%;
      height: @w;
    }
  }
  .questions-block {
    margin-left: 100px;

    .svg-icon {
      position: absolute;
      left: -30px;
      top: 4px;
      width: 12px;
      height: 12px;
      fill: @col-green;
    }

    &::v-deep .ui-collapsible {
      margin-bottom: 48px;

      .header {
        font-size: 1.125rem;
        font-weight: 700;
        line-height: 1.375rem;
        position: relative;
        cursor: pointer;
      }
    }

    .active {
      transition: color ease .2s;
      color: @col-green;
    }

    .answer {
      margin-top: 20px;
      font-weight: 400;
      line-height: 1.5rem;

      .ui-href {
        cursor: pointer;
        padding: 0;
      }
    }
  }
  > .ui-button.ui-btn {
    padding: 16px 80px;
    display: block;
    margin: 0 auto 40px;
  }
  @media @mobile {
    flex-direction: column;
    padding: 0 20px;

    .title-block {
      max-width: 100%;
      width: 100%;
      text-align: center;

      img {
        display: none;
      }
    }
    .questions-block {
      margin: 32px 0 0 20px;

      .svg-icon {
        left: -20px;
      }
    }
  }
}
</style>