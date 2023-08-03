<template>
  <div class="success-stories wrapper" data-nosnippet>
    <div class="title-block">
      <span class="title">Investors Success Stories</span>
      <span class="text">Was founded with the purpose to maximize your return on investment.</span>
    </div>
    <div class="stories-block flex">
      <swiper
        :slides-per-view="1"
        :space-between="30"
        :loop="true"
        :navigation="{
          nextEl: '.swiper-next',
          prevEl: '.swiper-prev',
        }"
        :breakpoints="{
          [mobileWidth]: {
            slidesPerView: 3,
          }
        }"
      >
        <swiper-slide>
          <div class="story-item padded">
            <div class="client flex">
              <img class="client-photo" src="../../assets/images/static/common/investor-profile-photo-1.png" alt="investor-profile-photo">
              <div class="client-info flex">
                <span class="name">Janak B.</span>
                <span class="role">INVESTOR</span>
                <div class="rating">
                  <UIcon name="star" />
                  <UIcon name="star" />
                  <UIcon name="star" />
                  <UIcon name="star" />
                  <UIcon name="star" />
                </div>
              </div>
            </div>
            <span class="text">
              I wish Ofirio were around sooner! It would’ve made years of investing so much easier. I used to use heaps of tools to find properties to invest in and keep track of my findings in a spreadsheet. With Ofirio, everything is just a click away. It’s simple and efficient.
            </span>
          </div>
        </swiper-slide>
        <swiper-slide>
          <div class="story-item padded">
            <div class="client flex">
              <img class="client-photo" src="../../assets/images/static/common/investor-profile-photo-2.png" alt="investor-profile-photo">
              <div class="client-info flex">
                <span class="name">Helen N.</span>
                <span class="role">INVESTOR</span>
                <div class="rating">
                  <UIcon name="star" />
                  <UIcon name="star" />
                  <UIcon name="star" />
                  <UIcon name="star" />
                  <UIcon name="star" />
                </div>
              </div>
            </div>
            <span class="text">
              I don't usually leave reviews, but after using Ofirio I had to let everyone know how brilliant it is! I found so many great deals, and I couldn't believe that I can search for properties by cap rate and even cash on cash return. I highly recommend Ofirio for making well thought through investments.
            </span>
          </div>
        </swiper-slide>
        <swiper-slide>
          <div class="story-item padded">
            <div class="client flex">
              <img class="client-photo" src="../../assets/images/static/common/investor-profile-photo-3.png" alt="investor-profile-photo">
              <div class="client-info flex">
                <span class="name">Rebecca M.</span>
                <span class="role">INVESTOR</span>
                <div class="rating">
                  <UIcon name="star" />
                  <UIcon name="star" />
                  <UIcon name="star" />
                  <UIcon name="star" />
                  <UIcon name="star" />
                </div>
              </div>
            </div>
            <span class="text">
              It’s a pleasure to use Ofirio! The concept is so simple and the execution is flawless! Ofirio let’s me search for properties based on how good the deal is - how brilliant! this is possibly the hardest part of real estate investing, actually finding a good deal. I will happily pay 10 times what they are charging.
            </span>
          </div>
        </swiper-slide>
        <swiper-slide>
          <div class="story-item padded">
            <div class="client flex">
              <img class="client-photo" src="../../assets/images/static/common/investor-profile-photo-4.png" alt="investor-profile-photo">
              <div class="client-info flex">
                <span class="name">Kim W.</span>
                <span class="role">INVESTOR</span>
                <div class="rating">
                  <UIcon name="star" />
                  <UIcon name="star" />
                  <UIcon name="star" />
                  <UIcon name="star" />
                  <UIcon name="star" />
                </div>
              </div>
            </div>
            <span class="text">
              Now this is a full package! i’m really happy with the overall experience and especially with the results. I double checked their numbers for myself and i’m excited that everything matches up! They earned a loyal customer - I recommend Ofirio to anyone looking to invest into real estate, especially for renting.
            </span>
          </div>
        </swiper-slide>
        <swiper-slide>
          <div class="story-item padded">
            <div class="client flex">
              <img class="client-photo" src="../../assets/images/static/common/investor-profile-photo-5.png" alt="investor-profile-photo">
              <div class="client-info flex">
                <span class="name">Steven A.</span>
                <span class="role">INVESTOR</span>
                <div class="rating">
                  <UIcon name="star" />
                  <UIcon name="star" />
                  <UIcon name="star" />
                  <UIcon name="star" />
                  <UIcon name="star" />
                </div>
              </div>
            </div>
            <span class="text">
              Ofirio is simple to use - I love that! The design is really nice and polished. I am new to real estate and I appreciate that they don’t only provide the tools, but also teach you how to use their tools and how to build wealth. Ofirio makes what can be a very complicated process very simple.
            </span>
          </div>
        </swiper-slide>
      </swiper>
      <UButton class="ui-btn ui-btn-iconic ui-btn-circle swiper-prev"><UIcon name="smooth-arrow"/></UButton>
      <UButton class="ui-btn ui-btn-iconic ui-btn-circle swiper-next"><UIcon name="smooth-arrow"/></UButton>
    </div>
  </div>
</template>
<style lang="less" scoped>
  
  .success-stories {
    &.wrapper { margin: 90px auto; }
    span { display: block; }
    .title-block {
      text-align: center;

      .title {
        font-size: 2.25rem;
        font-weight: 800;
      }
      .text {
        font-size: 1.125rem;
        font-weight: 600;
        color: @col-text-gray-dark;
        margin-top: 24px;
      }
    }
    .stories-block {
      margin-top: 50px;
      justify-content: center;
      position: relative;

      .swiper-container { padding: 15px 20px; }
      .ui-btn {
        @s: 40px;
        position: absolute;
        top: calc(50% - @s/2);
        background: @col-bg;
        z-index: 1;

        &.ui-btn-circle{
          width: @s;
          height: @s;
        }
        &.swiper-prev {
          left: 0;
          .svg-icon { transform: rotate(-90deg); }
        }
        &.swiper-next {
          right: 0;
          .svg-icon { transform: rotate(90deg); }
        }
      }

      .story-item {
        border-radius: @border-radius;
        box-shadow: 0px 0px 15px @col-shadow;
        min-width: 340px;
        padding: 20px 30px;
        height: 100%;

        .client-photo {
          border-radius: 50%;
          width: 70px;
          height: 70px;
        }
        .client-info {
          margin-left: 20px;
          flex-direction: column;
          justify-content: space-between;
          @icon-s: 18px;

          .name {
            font-weight: 700;
            line-height: 1.5rem;
          }
          .role {
            color: @col-text-gray-darker;
            font-size: 0.875rem;
            font-weight: 700;
            line-height: 1.5rem;
            text-transform: uppercase;
          }
          .svg-icon {
            width: @icon-s;
            height: @icon-s;
            fill: @col-green;
          }
        }
        .text {
          margin-top: 20px;
          font-weight: 400;
          line-height: 1.5rem;
          color: @col-text-gray-dark;
        }
      }
    }
    @media @mobile {
      flex-direction: column;
      padding: 0 20px;
      margin: 50px auto;

      .stories-block {
        .story-item {
          min-width: 240px;

          .client-photo {
            width: 60px;
            height: 60px;
          }
          .client-info {
            .svg-icon {
              width: 12px;
              height: 12px;
            }
          }
        }
      }
    }
  }
</style>

<script lang="ts">
import { defineComponent } from 'vue'
import UButton from '@/components/ui/UButton.vue';
import SwiperCore, { Navigation } from 'swiper';
import { Swiper, SwiperSlide } from 'swiper/vue';
import 'swiper/swiper.less';
import 'swiper/components/navigation/navigation.less';
SwiperCore.use([Navigation]);
import envModel from '@/models/env.model';

export default defineComponent({
  components: {
    UButton,
    Swiper,
    SwiperSlide,
  },
  computed: {
    mobileWidth() {
      return envModel.VUE_APP_MOBILE_WIDTH;
    }
  }
})
</script>