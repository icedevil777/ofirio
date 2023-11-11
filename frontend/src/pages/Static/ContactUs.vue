<template>
  <UPageHeader>
    <h1 class="title">Contact Us</h1>
    <p class="text hide-mobile">Whether you own or manage properties, our team of Rental <br> Management experts ensures you outperform your market!</p>
  </UPageHeader>
  <div class="contact-us wrapper">
    <div class="flex">
      <div class="send-message flex">
        <span class="title">Send Us a Message</span>
        <UMessageList ref="msgList" />
        <UFloatingInput v-model="query.full_name" label="Your name" :scheme="validators.VFullName"/>
        <UFloatingInput v-model="query.email" label="Email" :scheme="validators.VEmail"/>
        <UFloatingTextarea label="Your Request" v-model="query.message" rows="9" />
        <UButton class="ui-btn ui-btn-green hide-desktop" :class="{ disabled: busy }" @click="send">Send Message</UButton>
      </div>
      <div class="contact-info">
        <span class="title">Contact <br class="hide-mobile"> Information</span>
        <div class="contacts">
          <div>
            <UIcon name="mail" />
            <a href="mailto:help@ofirio.com">help@ofirio.com</a>
          </div>
          <div>
            <UIcon name="phone" />
            <a href="tel:+18885505978">+1 888-550-5978</a>
          </div>
        </div>
        <div class="links-block hide-mobile ">
          <a href="https://www.facebook.com/ofirio.official/">
            <UIcon name="facebook-transparent" />
          </a>
          <a href="https://www.instagram.com/ofirio.official/">
            <UIcon name="instagram-transparent" />
          </a>
          <a href="https://www.youtube.com/channel/UCrDHpDOIN6KAAsw5tKtsPNw">
            <UIcon name="youtube-transparent" />
          </a>
        </div>
      </div>
    </div>
    <UButton class="ui-btn ui-btn-green hide-mobile" :class="{ disabled: busy }" @click="send">Send Message</UButton>
  </div>
  <UDivider />
  <OFRC_FAQ />
  <OFRC_FindInvestment wavePosition="top"/>
  <UFooter />
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import UPageHeader from '@/components/ui/UPageHeader.vue'
import UFloatingTextarea from '@/components/ui/UFloatingTextarea.vue';
import UFloatingInput from '@/components/ui/UFloatingInput.vue';
import UMessageList from '@/components/ui/UMessageList.vue';
import UButton from '@/components/ui/UButton.vue';
import UDivider from '@/components/ui/UDivider.vue';
import OFRC_FindInvestment from '@/components/OFRC/FindInvestment.vue';
import OFRC_FAQ from '@/components/OFRC/FAQ.vue';
import UFooter from '@/components/static/footer.vue';

import ContactUsModel from '@/models/OFRC/ContactUs';
import { VFullName, VEmail, VContactUs } from '@/models/yups.model';

export default defineComponent({
  components: {
    UPageHeader,
    UButton,
    UMessageList,
    UFloatingTextarea,
    UFloatingInput,
    UDivider,
    OFRC_FindInvestment,
    OFRC_FAQ,
    UFooter,
  },
  data() {
    return {
      busy: false,
      validators: {
        VFullName,
        VEmail
      },
      query: {
        full_name: '',
        email: '',
        message: ''
      }
    }
  },
  methods: {
    send() {
      if (this.busy)
        return;

      const msgList = (<any>this.$refs).msgList;

      try {
        VContactUs.validateSync(this.query);
      } catch (ex) {
        msgList.push({
          type: 'error',
          message: ex.message
        })
        return;
      }
      
      this.busy = true;
      ContactUsModel.sendContactUs(this.query).then((result) => {
        if (result)
          msgList.push({ type: 'success', message: 'Successfully sent!' });
      })
      .catch((ex) => {
        this.busy = false;
        if (ex.type && ex.message)
          msgList.push(ex);
      })
    }
  }

})
</script>

<style lang="less" scoped>
  span { display: block;}
  .ui-divider { 
    margin: 90px 0;
    @media @mobile {
      margin: 50px 0;
    }
  }
  .static-page-header {
    background-image: url("../../assets/images/static/contact-us/header-bg.png");
    background-position: center;
    background-size: cover;
  }
  .contact-us {
    margin-top: 60px;

    @media @mobile {
      text-align: center;

      &.wrapper { padding: 0 25px; }
    }

    > .flex {
      justify-content: space-between;
      align-items: flex-start;

      @media @mobile { flex-direction: column; }
    }

    .send-message {
      flex: 1;
      max-width: 600px;
      flex-wrap: wrap;
      align-content: flex-start;
      align-items: flex-start;
      justify-content: space-between;

      .title {
        font-size: 2.25rem;
        font-weight: 800;
        margin-bottom: 30px;
        width: 100%;
        flex-shrink: 0;
      }
      .ui-message-list {
        flex-shrink: 0;
        width: 100%;
      }
      .ui-floating-input {
        flex: 1;
        flex-shrink: 0;

        + .ui-floating-input { margin-left: 20px; }
      }
      .ui-floating-text-area {
        margin-top: 30px;
        resize: vertical;
        flex: 1;
      }

      @media @mobile {
        .title { font-size: 1.85rem; }
        input {
          width: 100%;
          text-align: start;

          & + input { margin: 20px 0 0; }
        }
      }
    }
    .contact-info {
      background: @col-blue;
      border-radius: @border-radius;
      font-weight: 600;
      color: @col-text-light;
      padding: 40px 140px 40px 50px;

      .title {
        font-size: 2.25rem;
        font-weight: 800;
        line-height: 2.6rem;
        margin-bottom: 40px;
      }
      .contacts {
        > div { margin-bottom: 35px; }
        .svg-icon { vertical-align: middle; }
        a {
          display: inline-block;
          vertical-align: middle;
          margin-left: 15px;
        }
      }
      .links-block {
        @icon-s: 20px;

        > a {
          display: inline-block;
          width: 2*@icon-s;
          height: 2*@icon-s;
          border-radius: 50%;
          background: rgba(255, 255, 255, 0.25);
          margin-right: 15px;
        }
        .svg-icon {
          width: @icon-s;
          height: @icon-s;
          margin: @icon-s/2;
        }
      }
      @media @mobile {
        margin-top: 60px;
        padding: 40px 30px;

        .title {
          font-size: 1.85rem;
          margin-bottom: 25px;
        }
        .contacts {
          span {
            display: block;
            margin: 10px 0 0;
          }
          > div:last-child {
            margin: 0;
            font-size: 1.7rem;
          }
        }
      }
    }
    .ui-button {
      margin-top: 20px;
      padding: 15px 60px;
    }
  }
  
</style>