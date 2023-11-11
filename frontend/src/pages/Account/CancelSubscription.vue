<template>
  <div class="account-internal-padding cancel-sub">
    <h1 class="heading">Cancel subscription</h1>
    <span class="sub-heading">We’re sad to see you go. Please let us know why you would like to cancel your subscription.</span>
    <div class="flex selector-reason" :class="{ 'reason-selected': selectedReason != null }">
      <div class="reason" v-for="reason of reasons" :key="reason" :class="{ active: reason == selectedReason, inactive: reason != selectedReason }">
        <UIcon :name="reason.icon" />
        <div class="reason-info">
          <span class="name" v-text="reason.title"></span>
          <p class="description" v-text="reason.desc"></p>
          <UButton class="ui-btn ui-btn-bordered-green btn-select" @click="selectedReason = reason">Select</UButton>
          <UButton class="ui-btn-text ui-btn-text-black btn-back hide-desktop" @click="selectedReason = null"><UIcon name="smooth-arrow" /></UButton>
        </div>
      </div>
    </div>

    <transition name="fade" mode="out-in">
      <div
        class="flex reason reason-expensive"
        v-if="selectedReason && selectedReason.name == 'expensive'"
        key="reason-expensive"
      >
        <div class="action">
          <span class="save">Save 15%</span>
          <div class="price">
            <span class="old">$199.96</span>
            <span class="new">$167.96</span>
          </div>
          <UButton class="ui-btn ui-btn-blue">Switch to Quarterly</UButton>
        </div>
        <div class="action">
          <span class="save">Save 25%</span>
          <div class="price">
            <span class="old">$599.88</span>
            <span class="new">$479.88</span>
          </div>
          <UButton class="ui-btn ui-btn-blue">Switch to Annual</UButton>
        </div>
        <div class="action">
          <span class="text">We can help you get more out of Ofirio</span>
          <UButton class="ui-btn ui-btn-bordered-blue">Chat with us</UButton>
        </div>
      </div>


      <div
        class="flex reason reason-difficult"
        v-else-if="selectedReason && selectedReason.name == 'difficult'"
        key="reason-difficult"
      >
        <div class="action">
          <span class="text">If you feel that Ofirio is difficult to use then we’re here to help!</span>
          <UButton class="ui-btn ui-btn-bordered-blue">Live Chat With Us</UButton>
        </div>
        <div class="action">
          <span class="text">We have easy to follow videos that can teach you how to effectively use Ofirio!</span>
          <UButton class="ui-btn ui-btn-bordered-blue">Watch Tutorials</UButton>
        </div>
      </div>


      <div
        class="flex reason reason-not-interested"
        v-else-if="selectedReason && selectedReason.name == 'not-interested'"
        key="reason-not-interested"
      >
        <div class="action">
          <span class="text">If you feel that Ofirio is difficult to use then we’re here to help!</span>
          <UButton class="ui-btn ui-btn-bordered-blue">Pause Account</UButton>
        </div>
        <div class="action">
          <span class="text">We have easy to follow videos that can teach you how to effectively use Ofirio!</span>
          <UButton class="ui-btn ui-btn-bordered-blue" @click="cancelSubscription">Cancel Subscription</UButton>
        </div>
      </div>
      
      
      <div
        class="flex reason reason-missing-data"
        v-else-if="selectedReason && selectedReason.name == 'missing-data'"
        key="reason-missing-data"
      >
        <div class="action">
          <span class="text">Can't Find your city of some of the data is missing?</span>
          <UButton class="ui-btn ui-btn-bordered-blue">Request Missing Data</UButton>
        </div>
        <div class="action">
          <span class="text">It's very possible that Ofirio has the data you need</span>
          <UButton class="ui-btn ui-btn-bordered-blue">Chat With Us</UButton>
        </div>
        <div class="action">
          <span class="text">I'm not confident that the numbers are accurate</span>
          <UButton class="ui-btn ui-btn-bordered-blue">Inaccurate Data</UButton>
        </div>
      </div>


      <div
        class="reason reason-else"
        v-else-if="selectedReason"
        key="reason-else"
      >
        <span class="heading">Please let us know why you would like to cancel</span>
        <UTextarea rows="10" v-model="reasonDescription" placeholder="Message"></UTextarea>
        <span class="text">If you cancel, all your data will be deleted and you will lose access to your account</span>
        <UButton class="ui-btn ui-btn-blue" @click="cancelSubscription">Cancel Subscription</UButton><UButton class="ui-btn ui-btn-bordered-blue">Live Chat With Us</UButton>
      </div>

    </transition>


    <transition name="fade" mode="out-in">
      <div class="really-cancel" v-if="selectedReason && [ 'expensive', 'difficult', 'not-interested', 'missing-data' ].includes(selectedReason.name)">
        <span class="heading">Still want to cancel?</span>
        <span class="text">If you cancel your subscription all your data will be deleted and you will lose access to your account and all of the premium features.</span>
        <UButton
          class="ui-btn-text-gray"
          @click="() => $refs['popup-rly-cancel'].open()"
        >Cancel subscription</UButton>
      </div>
    </transition>


  </div>


<UPopup ref="popup-rly-cancel" class="popup-cancel-sub">
  <div class="content">
    <h2>Maybe we can help</h2>
    <p class="description">Don't lose out on the most cutting-edge real estate deal finding tools! Please consider our offer:</p>
    <div class="special-offer">
      <span class="save">SAVE 15% PERMANENTLY</span>
    </div>
    <UButton class="ui-btn ui-btn-green btn-take">I'll take the offer!</UButton>
    <span class="decline-offer">No thanks, delete my data and <UButton class="ui-btn-text ui-btn-text-gray" @click="cancelSubscription">Cancel my account</UButton></span>
    <UIcon class="ui-popup-default-close-icon" name="cross" @click="() => $refs['popup-rly-cancel'].close()" />
  </div>
</UPopup>

</template>

<style lang="less" scoped>
&.fade-enter-active,
&.fade-leave-active {
  transition: opacity 0.3s ease;
}

&.fade-enter-from,
&.fade-leave-to {
  opacity: 0;
}

.account-internal-padding > h1.heading {
  @media @mobile { margin-bottom: 15px; }
}

.cancel-sub {
  > .sub-heading {
    font-weight: 600;
    color: @col-text-gray-dark;
    font-size: 1.125rem;
    margin-bottom: 50px;
    line-height: 1.5rem;
    display: block;
  }
  .selector-reason {
    justify-content: space-between;
    align-items: stretch;

    .reason {
      @m-shift: 30px;

      max-width: 220px;
      border-radius: @border-radius;
      background: @col-bg;
      padding: 20px;
      box-shadow: @shadow @col-shadow;
      transition: transform .3s ease;
      text-align: center;
      position: relative;

      &:before {
        @s: 10px;

        content: '';
        display: block;
        position: absolute;
        bottom: -20px;
        height: 0;
        width: 0;
        left: calc(50% - @s/2);
        border: @s solid transparent;
        border-bottom-color: #f4f4f4;
        transform: translateY(30px);
        transition: transform .3s ease, opacity .3s ease;
        transition-delay: .05s;
        opacity: 0;
        visibility: hidden;
        border-radius: 4px;
      }
      & + .reason { margin-left: 20px; }
      &.active {
        transform: translateY(30px);
        background: @col-green;
        color: @col-bg;

        &:before {
          transform: translateY(0);
          opacity: 1;
          visibility: visible;
        }
        .svg-icon { fill: @col-bg; }
        p.description { color: @col-disabled; }
        .ui-btn {
          background: @col-green-dark;
          color: inherit;

          &:hover, &:active, &:focus { background: darken(@col-green-dark, 10%); }
        }
        @media @mobile {
          transform: none;
          max-width: calc(100% - @m-shift);

          .btn-back {
            opacity: 1;
            visibility: visible;
          }
        }
      }
      > .svg-icon {
        @s: 42px;

        display: block;
        margin: 0 auto 20px;
        height: @s;
        min-height: @s;
        width: @s;
        min-width: @s;
        fill: @col-green;

        @media @mobile {
          margin: 0 15px 0 0;
        }
      }
      span, p { display: block; }
      span.name {
        font-weight: 700;
        margin-bottom: 1rem;
        font-size: 1.125rem;
      }
      p.description {
        color: @col-text-gray-dark;
        font-size: 0.875rem;
        line-height: 1.25rem;
        margin-bottom: 25px;

        @media @mobile { margin-bottom: 0; }
      }
      .btn-select {
        width: 100%;
        font-weight: 700;
        height: 46px;

        @media @mobile {
          position: absolute;
          opacity: 0;
          top: 0;
          right: 0;
          left: 0;
          bottom: 0;
          height: auto;
        }
      }
      .btn-back {
        @s: 12px;

        position: absolute;
        top: calc(50% - @s/2);
        left: -@m-shift;
        transform: rotate(-90deg);
        opacity: 0;
        visibility: hidden;
        transition: opacity .3s ease-in-out;

        .svg-icon {
          width: @s;
          height: @s;
          fill: @col-text-dark;
          margin: 0;
        }
      }

      @media @mobile {
        margin-top: 20px;
        max-width: 100%;
        display: flex;
        transition: max-width .3s ease;
        align-items: center;

        & + .reason { margin-left: 0 }
      }
    }

    @media @mobile {
      flex-direction: column;
      align-items: flex-end;

      &.reason-selected > .reason.inactive {
        display: none;
      }
    }
  }

  > .reason {
    background: @col-bg;
    border-radius: @border-radius;
    padding: 0;
    margin-top: 50px;
    box-shadow: @shadow @col-shadow;

    .action {
      flex: 1;
      padding: 30px;
      text-align: center;
      line-height: 1.25rem;

      & + .action {
        border-left: 1px solid #e1e1e1;

        @media @mobile {
          border-left: none;
          border-top: 1px solid #e1e1e1;
        }
      }
      .text {
        display: block;
        color: @col-text-gray-dark;
        line-height: 1.25rem;
        font-size: 0.875rem;
        margin-bottom: 15px;
      }
      .ui-button {
        font-weight: 700;
        height: 46px;
        padding: 0 2rem;
        margin-top: 20px;

        @media @mobile {
          min-width: 80%;
        }
      }
      .ui-btn-bordered-blue { margin-top: 16px; }
    }
    @media @mobile {
      margin-top: 20px;
      flex-direction: column;
    }
  }

  .reason-expensive, .reason-difficult {
    justify-content: stretch;
    align-content: stretch;
  }

  .reason-expensive {
    .action {
      .save {
        display: block;
        margin-bottom: 10px;
        color: @col-green;
        font-weight: 700;
        text-transform: uppercase;
      }
      .price {
        line-height: inherit;
        font-weight: 700;

        .old {
          font-size: 0.875rem;
          color: @col-text-gray-darker;
          text-decoration: line-through;
        }
        .new {
          font-size: 1.125rem;
          margin-left: 10px;
        }
      }
    }
  }

  .reason-else, .really-cancel {
    padding: 30px;

    span { display: block; }
    span.heading {
      font-weight: 800;
      font-size: 1.625rem;
      margin-bottom: 30px;
    }
    span.text {
      color: @col-text-gray-dark;
      line-height: 1.5rem;
      margin-top: 30px;
    }
    .ui-button {
      margin-top: 20px;
      
      & + .ui-button {
        margin-left: 20px;

        @media @mobile {
          margin-left: 0;
          margin-top: 20px;
        }
      }
      &.ui-btn-blue { border: 2px solid transparent; }

      @media @mobile {
        display: block;
        width: 100%;
        height: 40px
      }
    }
  }
  .really-cancel {
    margin-top: 50px;
    padding: 0;

    .ui-btn-text-gray {
      text-transform: uppercase;
      padding: 0;
      font-size: 0.875rem;
      font-weight: 800;
      margin-top: 30px;
    }
  }
}

.popup-cancel-sub {
  > .content {
    padding: 40px 100px;
    text-align: center;
    max-width: 600px;
    line-height: 1.4rem;
    position: relative;

    > h2 {
      font-weight: 800;
      font-size: 1.875rem;
      line-height: 2rem;
      display: block;
      margin-bottom: 20px;
    }
    .description {
      color: @col-text-gray-darker;
      font-weight: 600;
      margin-bottom: 30px;
    }
    .special-offer {
      padding: 20px 10px;
      border-radius: @border-radius;
      border: 1px solid @col-text-gray-light;
      font-size: 1.125rem;
      margin-bottom: 30px;

      span { display: block; }
      span.save {
        color: @col-green;
        // margin-bottom: 10px;
        font-weight: 700;
      }
      span.time {
        font-weight: 800;
        text-transform: uppercase;
      }
    }
    .btn-take {
      width: 100%;
      margin-bottom: 20px;
      height: 50px;
    }
    .decline-offer {
      font-weight: 700;
      color: @col-text-gray-darker;

      .ui-button {
        color: inherit;
        text-decoration: underline;
      }
    }

    @media @mobile {
      width: 100%;
      height: 100%;
      overflow-y: auto;
      border-radius: 0;
      padding: 50px 20px;
    }
  }
}
</style>

<script lang="ts">
import { defineComponent } from 'vue';
import UButton from '@/components/ui/UButton.vue';
import UTextarea from '@/components/ui/UTextarea.vue';
import UPopup from '@/components/ui/UPopup.vue';

import AccountStore from '@/models/Account';

const reasons = [
  {
    name: 'expensive',
    icon: 'coins',
    title: 'Too Expensive',
    desc: 'My subscription costs too much',
  },
  {
    name: 'difficult',
    icon: 'pushing-stone',
    title: 'Difficult to Use',
    desc: 'I can’t figure out how to effectively use Ofirio',
  },
  {
    name: 'not-interested',
    icon: 'crossed-circle',
    title: 'Not interested',
    desc: 'I\'m not looking for deals anymore',
  },
  {
    name: 'missing-data',
    icon: 'document-plot-missing-data',
    title: 'Missing Data',
    desc: 'Ofirio is missing information',
  },
  {
    name: 'else',
    icon: 'ellipsis',
    title: 'Something Else',
    desc: 'Its none of the other options',
  },
];

export default defineComponent({
  components: {
    UButton,
    UTextarea,
    UPopup
  },
  data() {
    return {
      busy: false,
      selectedReason: null as null | Record<string, string>,
      reasonDescription: '',
      reasons
    }
  },
  methods: {
    cancelSubscription() {
      if (!this.selectedReason || this.busy)
        return;

      let reason = this.selectedReason.title;
      if (this.selectedReason.name == 'else')
        reason = this.reasonDescription;
      
      if (reason == '')
        return;

      this.busy = true;
      AccountStore.Subscriptions.stopSubscription(reason)
      .then(async () => {
        await Promise.all([
          AccountStore.Auth.loadAccountDTO(),
          AccountStore.Subscriptions.load()
        ]);
        this.$router.push({ name: 'account-subscriptions' });
      })
      .catch((msg:any) => {
        alert('TEMPORARY: subscription is not cancelled - see err in console');
        console.error(msg);
      })
      .finally(() => {
        this.busy = false;
      });
    }
  }
})
</script>