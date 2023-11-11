<template>
  <div class="wrapper">
    <template v-if="tokenAlive == false">
      <UIcon name="cross" />
      <span class="title">Restore Code is Invalid</span>
    </template>
    <template v-else-if="tokenAlive == true">
      <span class="title">Reset Your Password</span>
      <div class="max-wide">
        <UMessageList ref="passwordMessageList" />
        <UFloatingInput v-model="password_new1" label="New password" type="password" required :scheme="Validators.VPassword" />
        <PasswordStrength :passmodel="password_new1" />
        <UFloatingInput v-model="password_new2" label="Confirm new Password" type="password" required :scheme="Validators.VPassword" />
        <UButton
          @click="actionPasswordChange"
          class="ui-btn ui-btn-green"
        >Update password</UButton>
      </div>
    </template>
    <template v-else>
      Loading...
    </template>
  </div>
  <OFRC_FindInvestment wavePosition="top"/>
  <UFooter />
</template>

<style lang="less" scoped>
  .wrapper {
    margin: 70px auto;
    text-align: center;
    
    .svg-icon {
      width: 60px;
      height: 60px;
      fill: @col-err;

      @media @mobile {
        width: 40px;
        height: 40px;
      }
    }
    .title {
      display: block;
      font-size: 2.625rem;
      font-weight: 800;
      margin: 30px 0 40px;
    }

    @media @mobile {
      margin: 50px auto;
      padding: 0 20px;

      .title { font-size: 1.85rem; }
    }
  }
  .max-wide {
    max-width: 380px;
    margin: 0 auto;
    text-align: left;
  }
  .ui-floating-input, .ui-btn { width: 100%; }
  .ui-floating-input { margin: 0; }
  .password-strength { margin-bottom: 20px; }
  .ui-btn {
    margin-top: 30px;
    height: 50px;
  }  
</style>

<script lang="ts">
import { defineComponent } from 'vue'
import UButton from '@/components/ui/UButton.vue';
import OFRC_FindInvestment from '@/components/OFRC/FindInvestment.vue';
import UFooter from '@/components/static/footer.vue'

import UFloatingInput from '@/components/ui/UFloatingInput.vue';
import UMessageList from '@/components/ui/UMessageList.vue';
import PasswordStrength from '@/components/Account/password-strength.vue';

import AccountStore from '@/models/Account';
import { VPassword } from '@/models/yups.model';
import { sendEvent } from '@/services/LocalstorageWatcher.service';

export default defineComponent({
  components: {
    UButton,
    UFloatingInput,
    UMessageList,
    PasswordStrength,
    OFRC_FindInvestment,
    UFooter
  },
  computed: {
    Account: function () {
      return AccountStore;
    },
    Validators: function () {
      return { VPassword }
    }
  },
  data() {
    return {
      busy: false,
      tokenAlive: null as null | boolean,
      token: '',
      password_new1: '',
      password_new2: ''
    }
  },
  methods: {
    processServerMessages(err: TServerDefaultResponse) {
      if (err.server_messages) {
        for (let msg of err.server_messages)
          (<any>this.$refs.passwordMessageList).push({
            type: msg.level,
            message: msg.message
          })
      }
      this.busy = false;
    },

    async actionPasswordChange() {
      if (this.busy)
        return;

      if (this.password_new1 != this.password_new2)
        return (<any>this.$refs.passwordMessageList).push({
          type: 'error',
          message: 'Passwords are not the equal'
        });

      const isValidNewPassword = await VPassword.isValid(this.password_new1);

        if (isValidNewPassword) {
          this.busy = true;

          AccountStore.Auth.changePasswordByResetToken(this.token, this.password_new1).then(() => {
            this.busy = false;
            sendEvent('ofirio-action-reload-auth');
            this.$router.push({ name: 'static-home' });
          }, (err) => this.processServerMessages(err));
        }
    }
  },
  mounted() {
    const token = <string>(<any>this.$route).params.token;
    AccountStore.Auth.checkPasswordResetToken(token)
    .then((a) => {
      this.tokenAlive = true;
      this.token = token;
    })
    .catch((e) => {
      this.tokenAlive = false;
    });
  }
})
</script>