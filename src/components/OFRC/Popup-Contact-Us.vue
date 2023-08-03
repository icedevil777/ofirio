<template>
  <div class="popup-contact-us">
    <h1 class="ui-text-center">Contact Agent</h1>
    <UMessageList ref="callUsMessageList" />
    <UFloatingInput label="Full Name" v-model="query.full_name" :scheme="validators.VFullName"/>
    <UFloatingInput label="Email" v-model="query.email" :scheme="validators.VEmail" />
    <UFloatingInput label="Phone" v-model="query.phone" :scheme="validators.VPhoneNumber"/>
    <UFloatingTextarea label="Your Request" v-model="query.request" />
    <UButton class="ui-btn ui-btn-green" @click="send">Send Message</UButton>
    <UDivider />
    <span class="agreement">
      By sending message you agree to Ofirio’s
      <router-link :to="{ name: 'static-terms-and-conditions' }">
        <a @click="() => $root.$refs.popupCallUs.close()" class="ui-href ui-href-underline">Terms of Use</a>
      </router-link>
      and
      <router-link :to="{ name: 'static-privacy-policy' }">
        <a @click="() => $root.$refs.popupCallUs.close()" class="ui-href ui-href-underline">Privacy Policy</a>
      </router-link>
    </span>
    <UIcon class="ui-popup-default-close-icon" name="cross" @click="() => $root.$refs.popupCallUs.close()" />
  </div>
</template>

<style lang="less" scoped>
.popup-contact-us {
  position: relative;
  width: 100%;
  max-width: 600px !important;
  padding: 40px 100px;

  @media @mobile {
    height: 100%;
    overflow-y: auto;
    padding: 50px 20px;
  }
  > h1 {
    font-weight: 800;
    font-size: 1.875rem;
    margin-bottom: 20px;
  }
  .ui-floating-input, .ui-floating-textarea {
    width: 100%;
    margin: 10px 0;
  }
  .ui-floating-textarea {
    line-height: 1.25rem;

    &::v-deep textarea { resize: none; }
  }
  > .ui-btn-green {
    margin: 10px 0;
    width: 100%;
    height: 50px;
  }
  > span.agreement {
    display: block;
    font-weight: 400;
    font-size: .875rem;
    line-height: 1.25rem;
    text-align: center;
    color: @col-text-gray-dark;
  }

}
</style>

<script lang="ts">
import { defineComponent, watch } from 'vue';

import UButton from '@/components/ui/UButton.vue';
import UFloatingInput from '@/components/ui/UFloatingInput.vue';
import UFloatingTextarea from '@/components/ui/UFloatingTextarea.vue';
import UMessageList from '@/components/ui/UMessageList.vue';
import UDivider from '@/components/ui/UDivider.vue';
import { VEmail, VFullName, VPhoneNumber, VAgents } from '@/models/yups.model';

import AccountStore from '@/models/Account';
import { callAgents } from '@/models/Property/basis';

export default defineComponent({
  components: {
    UButton,
    UFloatingInput,
    UFloatingTextarea,
    UMessageList,
    UDivider
  },
  computed: {
    validators() {
      return { VEmail, VFullName, VPhoneNumber }
    }
  },
  data() {
    return {
      query: {
        full_name: '',
        email: '',
        phone: '',
        request: 'Enter your text here...'
      },
      watcher: () => {}
    }
  },
  methods: {
    setProperty(property: any) {
      if (!property || !property.Basis?.dto?.address)
        return;

      this.query.request = `I’m interested in ${ property.Basis.dto.address.line }, ${ property.Basis.dto.address.city } ${ property.Basis.dto.address.zip }`;
    },
    async send() {
      const route = this.$route;
      if (route.name != 'property')
        return;

      if (!route.params.id)
        return;

      try { await VAgents.validate(this.query); }
      catch (ex) { return (<any>this.$refs).callUsMessageList.push({ type: 'error', message: ex.message }); }

      const ans = await callAgents({ ...this.query, prop_id: <string>route.params.id });
      
      (<any>this.$root).$refs.globMessages.push({
        type: ans ? 'success' : 'error',
        message: ans ? 'Success!' : 'Error occurred, please try again later'
      });

      if (ans)
        (<any>this.$root).$refs.popupCallUs.close();

    },
    fillExistingData() {
      this.query.full_name = AccountStore.Basis.isLoggedIn ? AccountStore.Basis.dto?.first_name + ' ' + AccountStore.Basis.dto?.last_name : '';
      this.query.email = AccountStore.Basis.isLoggedIn ? AccountStore.Basis.dto?.email + '' : '';
    }
  },
  mounted() {
    this.fillExistingData();
    this.watcher = watch(() => AccountStore.Basis.isLoggedIn, (state: boolean) => {
      this.fillExistingData();
    });
  },
  beforeUnmount() {
    this.watcher();
  }
  
})
</script>