<template>
  <div class="account-internal-padding account-settings">
    <h1 class="heading">Account settings</h1>
    <div class="account-settings-list flex">
      <div class="account-sub-block profile-details">
        <div class="max-wide">
          <span class="sub-heading">Profile Details</span>
          <UMessageList ref="profileMessageList" />
          <UFloatingInput v-model="Account.Profile.dto.email" class="email" label="E-mail" type="email" required disabled readonly />
          <UFloatingInput v-model="first_name" label="First Name" type="text" required />
          <UFloatingInput v-model="last_name" label="Last Name" type="text" required />
          <!-- <UFloatingInput v-model="last_name" label="Phone" type="text" required /> -->
          <UButton
            @click="actionProfileUpdate"
            :busy="inProgressState == 'profile'"
            class="ui-btn ui-btn-green"
          >Save Details</UButton>
        </div>
      </div>
      <div class="account-sub-block password-change">
        <div class="max-wide">
          <span class="sub-heading">Change your Password</span>
          <UMessageList ref="passwordMessageList" />
          <UFloatingInput v-model="password_old" label="Current Password" type="password" required :scheme="Validators.VPassword" />
          <UFloatingInput v-model="password_new1" label="New password" type="password" required :scheme="Validators.VPassword" />
          <PasswordStrength :passmodel="password_new1" />
          <UFloatingInput v-model="password_new2" label="Confirm new Password" type="password" required :scheme="Validators.VPassword" />
          <UButton
            @click="actionPasswordChange"
            :busy="inProgressState == 'password'"
            class="ui-btn ui-btn-green"
          >Update password</UButton>
        </div>
      </div>
    </div>
  </div>
</template>

<style lang="less" scoped>
.account-sub-block .sub-heading + .ui-message-list { margin-top: -10px; margin-bottom: -20px; }
.account-settings > h1.heading { margin-bottom: 0; }
.account-settings-list {
  justify-content: space-between;
  align-items: stretch;
  align-content: flex-start;
  flex-wrap: wrap;

  > .account-sub-block {
    width: calc(50% - 25px);
    padding: 40px;
    margin-top: 40px;

    .max-wide {
      max-width: 380px;
      margin: 0 auto;
    }
    .ui-floating-input, .ui-btn { width: 100%; }
    .ui-floating-input {
      margin-top: 20px;
    }
    .ui-btn {
      margin-top: 30px;
      height: 50px;
    }

    @media @mobile {
      width: 100%;
      padding: 20px;
    }
  }
  .password-change {
    .forgot-password {
      margin: 5px 0 0;
      font-size: 0.875rem;
      
      .ui-button {
        color: @col-text-gray-darker;
        font-weight: normal;
        text-decoration: underline;
      }
    }
  }
}
</style>

<script lang="ts">
import { defineComponent } from 'vue';

import UButton from '@/components/ui/UButton.vue';
import UFloatingInput from '@/components/ui/UFloatingInput.vue';
import UMessageList from '@/components/ui/UMessageList.vue';
import PasswordStrength from '@/components/Account/password-strength.vue';

import AccountStore from '@/models/Account';
import { VPassword } from '@/models/yups.model';


export default defineComponent({
  components: {
    UButton,
    UFloatingInput,
    UMessageList,
    PasswordStrength
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
      inProgressState: false as boolean | string,
      password_old: '',
      password_new1: '',
      password_new2: '',
      // @ts-ignore
      first_name: AccountStore.Profile.dto?.first_name,
      // @ts-ignore
      last_name: AccountStore.Profile.dto?.last_name
    }
  },
  methods: {

    processServerMessages(err: TServerDefaultResponse, listRef: any) {
      if (err.server_messages) {
        for (let msg of err.server_messages)
          listRef.push({
            type: msg.level,
            message: msg.message
          })
      }
      this.inProgressState = false;
    },

    

    actionProfileUpdate() {
      if (this.inProgressState) return;

      if (this.first_name && this.last_name) {
        this.inProgressState = 'profile';

        AccountStore.Profile.update(this.first_name, this.last_name).then(() => {
          this.inProgressState = false;
          (<any>this.$root).$refs.globMessages.push({
            type: 'success',
            message: 'Successfully changed!'
          });
        }).catch((err) => this.processServerMessages(err, this.$refs.profileMessageList));
      } else
        return (<any>this.$refs.profileMessageList).push({
          type: 'error',
          message: 'First Name and Last Name must be entered'
        });
    },

    async actionPasswordChange() {
      if (this.inProgressState) return;

      if (this.password_new1 != this.password_new2)
        return (<any>this.$refs.passwordMessageList).push({
          type: 'error',
          message: 'Passwords are not equal'
        });


      try {
        const isValidPasswOld = await VPassword.validate(this.password_old);
        const isValidPasswNew = await VPassword.validate(this.password_new1);

        if (isValidPasswOld && isValidPasswNew) {
          this.inProgressState = 'password';

          AccountStore.Auth.changePassword(this.password_old, this.password_new1).then(() => {
            this.inProgressState = false;
            (<any>this.$root).$refs.globMessages.push({
              type: 'success',
              message: 'Successfully changed!'
            });
          }).catch((err) => this.processServerMessages(err, this.$refs.passwordMessageList));
        }
      } catch (ex) {
        return (<any>this.$refs.passwordMessageList).push({
          type: 'error',
          message: ex.message
        });
      }
    }

  }
})
</script>