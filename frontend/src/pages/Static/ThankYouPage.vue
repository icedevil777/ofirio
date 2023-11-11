<template>
  <div class="title-block wrapper">
    <UIcon name="checkmark-in-circle" />
    <span class="title">Thank You!</span>
    <span class="text">Email us at <a href="mailto:help@ofirio.com" class="ui-href ui-href-underline">help@ofirio.com</a> with any questions, suggestions, or feedback.</span>
  </div>
  <div class="questionnaire-block wrapper" v-if="Account.Subscriptions.quizDTO && quizShow">
    <span class="title">We'd love to get to know you better:</span>
    <div class="content">
      <div class="progress">
        <span class="done">{{ currentStep + 1 }}</span>
        <span class="goal">/{{ Account.Subscriptions.quizDTO.quiz.length }}</span>
        <div class="progress-bar">
          <div class="progress-bar-done" :style="{ width: `${ (currentStep + 1) * 100 / Account.Subscriptions.quizDTO.quiz.length }%` }"></div>
        </div>
      </div>
      <span class="question">{{ Account.Subscriptions.quizDTO.quiz[currentStep].question }}</span>
      <div class="answers">
        <template v-for="(ans, i) of Account.Subscriptions.quizDTO.quiz[currentStep].answers" :key="ans">
          <URadio v-model="radioModel" required name="quiz-radio-gr" :value="i">{{ ans.value }}</URadio>
        </template>
      </div>
      <textarea placeholder="Message" v-model="customMessage" v-if="radioModel != null && Account.Subscriptions.quizDTO.quiz[currentStep].answers[radioModel].type == 'textarea'"></textarea>
      <UButton class="ui-btn ui-btn-green" @click="goNextQuestion">{{ currentStep + 1 == Account.Subscriptions.quizDTO.quiz.length ? 'Submit' : 'Next' }}</UButton>
    </div>
  </div>
  <div class="enjoy-the-product-block wrapper" v-show="!quizShow">
    <router-link
      :to="{ name: 'search', params: { typeOptions: 'state_id=FL'} }"
    >
      <UButton class="ui-btn ui-btn-green">Find a property</UButton>
    </router-link>
  </div>
  <OFRC_FindInvestment wavePosition="top"/>
  <UFooter />
</template>

<style lang="less" scoped>
  span { display: block; }
  .title-block {
    margin-top: 70px;
    text-align: center;

    .svg-icon {
      width: 60px;
      height: 60px;
      fill: @col-green;
    }
    .title {
      font-size: 2.625rem;
      font-weight: 800;
      margin: 30px 0 40px 0;
    }
    .text {
      color: @col-text-gray-dark;
      margin-top: 22px;
    }
  }
  .questionnaire-block {
    text-align: center;
    margin: 70px auto;

    .title {
      font-size: 1.625rem;
      font-weight: 800;
    }
    .content {
      max-width: 400px;
      margin: 30px auto 10px;

      .progress {
        position: relative;
        padding: 6px 0;
        text-align: end;
        @h: 3px;
        @progress-w: 20%;

        span {
          display: inline;
          font-weight: 700;
        }
        .done {
          font-size: 1.125rem;
        }
        .goal {
          font-size: 0.75rem;
          color: @col-text-gray-darker;
        }
        .progress-bar {
          position: absolute;
          width: 100%;
          height: @h;
          bottom: 0;
          left: 0;
          border-radius: @border-radius;
          background: @col-gray-light;

          .progress-bar-done {
            position: absolute;
            width: @progress-w;
            height: @h;
            bottom: 0;
            left: 0;
            border-radius: @border-radius;
            background: @col-green;
          }
        }
      }
      .question {
        font-size: 1.25rem;
        font-weight: 700;
        margin-top: 32px;
      }
      .answers {
        margin-top: 26px;
        div {
          display: block;
          color: @col-text-gray-dark;
        }
      }
      textarea {
        margin-top: 14px;
        width: 100%;
        resize: none;
        display: block;
        font-family: inherit;
        font-size: 1rem;
        border: 1px solid @col-gray-light;
        border-radius: @border-radius;
        outline: 0;
        padding: 20px 16px 20px 16px;
      }
      .ui-btn {
        margin-top: 26px;
        padding: 12px 0;
        width: 100%;
      }
    }
  }
  .enjoy-the-product-block {
    margin: 30px auto 70px;
    text-align: center;

    .ui-btn { padding: 12px 120px; }
  }
  @media @mobile {
    .wrapper { padding: 0 20px; }
    .title-block, 
    .questionnaire-block, 
    .enjoy-the-product-block { padding: 0 20px; }
    .title-block {
      margin: 50px auto 0;

      .svg-icon {
        width: 50px;
        height: 50px;
      }
      .title {
        font-size: 1.85rem;
      }
      .text {
        font-size: 1.15rem;
        line-height: 1.6rem;
      }
    }
    .questionnaire-block {
      .title {
        font-size: 1.5rem;
        line-height: 1.7rem;
      }
      .content {
        .question { font-size: 1.28rem; }
        &::v-deep .ui-radio {
          label { font-size: 1.15rem; }
        }
      }
    }
    .enjoy-the-product-block {
      margin: 30px auto 50px;

      .ui-btn {
        padding: 12px 0;
        width: 100%;
      }
    }
  }
</style>

<script lang="ts">

import {defineComponent} from 'vue';
import UButton from '@/components/ui/UButton.vue';
import URadio from '@/components/ui/URadioInput.vue';
import UFooter from '@/components/static/footer.vue';
import OFRC_FindInvestment from '@/components/OFRC/FindInvestment.vue';

import AccountStore from '@/models/Account';
import paymentPrice from '@/models/Account/payments/paymentPrice';

export default defineComponent({
  components:{
    UButton,
    URadio,
    UFooter,
    OFRC_FindInvestment,
  },
  computed: {
    Account() {
      return AccountStore;
    }
  },
  data() {
    return {
      currentStep: 0,
      customMessage: '',
      radioModel: null as number | null,
      block: false,
      quizShow: true
    }
  },
  methods: {
    goNextQuestion() {
      if (this.block)
        return;

      if (!this.Account.Subscriptions.quizDTO || !this.Account.Subscriptions.quizAnswersDTO || this.radioModel == undefined)
        return;

      const step = this.Account.Subscriptions.quizDTO.quiz[this.currentStep];
      const answer = step.answers[this.radioModel];
      const confirmedAnswer = answer.type == 'textarea' ? this.customMessage : answer.value;

      this.Account.Subscriptions.quizAnswersDTO[step.name] = confirmedAnswer;

      if (this.currentStep + 1 == this.Account.Subscriptions.quizDTO.quiz.length) {
        this.block = true;
        this.Account.Subscriptions.saveQuiz()
        .catch((ex: TServerDefaultResponse) => {
          console.log(ex);
          for (let m of ex.server_messages)
            (<any>this.$root).$refs.globMessages.push({ type: m.level, message: m.message });
        })
        .finally(() => {
          this.block = false;
          this.quizShow = false;
          window.scrollTo({ top: 0, behavior: 'smooth' });
        });
      } else {
        this.currentStep++;
        this.radioModel = null;
        this.customMessage = '';
      }
    }
  },
  mounted() {
    const params = <any>this.$route.params;
    
    if (params.tid) {
      const planByPid = paymentPrice.find(p => p.code == params.pid);
      if (planByPid != undefined) {
        window.dataLayer = window.dataLayer || [];
        window.dataLayer.push({
          event: 'eec.purchase',
          ecommerce: {
            purchase: {
              actionField: {
                id: params.tid,
                revenue: params.revenue
              },
              products: [{
                id: planByPid.code.toString(),
                name: 'Premium ' + planByPid.name,
                quantity: 1,
                price: (planByPid.priceMonthly * planByPid.monthCount).toString()
              }]
            }
          }
        });
      }
      this.$router.push({ name: 'static-payment-success' });
    }

    this.Account.Subscriptions.loadQuiz();
  }
})
</script>