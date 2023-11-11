<template>
  <div class="wrapper" v-if="false">
    <span class="page-title">Blog</span>
    {{ Account.Basis.dto.subscription }}
    <div class="unlock">
      <UnlockAnalytics style="width: 150px" />
    </div>
    <div class="unlock">
      <UnlockAnalytics style="width: 150px; height: 200px;">Another text</UnlockAnalytics>
    </div>
    <div class="unlock">
      <UnlockAnalytics mode="simple">Another text</UnlockAnalytics>
    </div>
    <UButton class="ui-btn ui-btn-green" @click="$root.$refs.popupUpgrade.open">Upgrade</UButton>
    <UButton class="ui-btn ui-btn-green" @click="$root.$refs.popupCallUs.open">Call us</UButton>
    <UButton class="ui-btn ui-btn-green" @click="$root.$refs.globMessages.push({ message: '1 2 3 Test Ofirio Global Message'})">Glob message</UButton>
    <UButton class="ui-btn ui-btn-green" @click="() => $root['ev-popup-login-open']('email-validation')">email validation required</UButton>
    <UButton class="ui-btn ui-btn-green" @click="changePaymentMethod">change payment method</UButton>
<br>
<br>
<br>
<br>
<br>
<br>
{{ modelBoolean.rawValue }}
<UCheckboxChipEgg :egg="modelBoolean">Toggle</UCheckboxChipEgg>

<br>
<br>
{{ modelArray.rawValue }}
<UCheckboxChipEgg :egg="modelArray" value="1">Asapad 1</UCheckboxChipEgg>
<UCheckboxChipEgg :egg="modelArray" value="2">Asapad 2</UCheckboxChipEgg>
<UCheckboxChipEgg :egg="modelArray" value="3">Asapad 3</UCheckboxChipEgg>
<br>
<br>
<br>
<br>
{{ modelInc.value }}
<UIncrementalEgg :egg="modelInc" label="Label" prepend="Prepend" prefix="$$" postfix="%%" postpend="Postpend" />
<br>
<br>
{{ modelBoolean.value }}
<UToggleEgg :egg="modelBoolean" />
<br>
<br>
{{ modelString.value }}
<URadioChipEgg :egg="modelString" value="1">Asapad 1</URadioChipEgg>
<URadioChipEgg :egg="modelString" value="2">Asapad 2</URadioChipEgg>
<URadioChipEgg :egg="modelString" value="3">Asapad 3</URadioChipEgg>
<br>
<br>
<br>
{{ modelBoolean.rawValue }}
<UCheckboxInputEgg :egg="modelBoolean">Toggle</UCheckboxInputEgg>

<br>
<br>
{{ modelArray.rawValue }}
<UCheckboxInputEgg :egg="modelArray" value="1">Asapad 1</UCheckboxInputEgg>
<UCheckboxInputEgg :egg="modelArray" value="2">Asapad 2</UCheckboxInputEgg>
<UCheckboxInputEgg :egg="modelArray" value="3">Asapad 3</UCheckboxInputEgg>
<br>
<br>
<URadioInputEgg :egg="modelString" value="1">Asapad 1</URadioInputEgg>
<URadioInputEgg :egg="modelString" value="2">Asapad 2</URadioInputEgg>
<URadioInputEgg :egg="modelString" value="3">Asapad 3</URadioInputEgg>
<br>
<br>

<USelectDropEgg :egg="modelEnum" :label="modelEnum.rawValue?.label || 'Select baths'" mHeader="Look Back">
  <template v-slot:item="{ option }">{{ option.label }}</template>
</USelectDropEgg>
<br>
<br>
<UFloatingTextareaEgg :egg="model" label="Label for input" />
<br>
<br>

<UTextInputEgg :egg="model" prepend="Prepend" prefix="$$" postfix="%%" postpend="Postpend" jitter="blur" placeholder="Test Placeholder" />
<br>
<UTextInputEgg :egg="model" prepend="Prepend" prefix="$$" postfix="%%" postpend="Postpend" jitter="debounce" />
<br>
<UTextInputEgg :egg="model" prepend="Prepend" prefix="$$" postfix="%%" postpend="Postpend" flexible jitter="throttle" />
<br>
<UTextInputEgg :egg="model" prepend="Prepend" prefix="$$" postfix="%%" postpend="Postpend" flexible jitter="reactive" />
<br>
<br>
<br>
<UTextInputEgg :egg="model" prepend="Prepend" prefix="$$" postfix="%%" postpend="Postpend" flexible/>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
    <UButton class="ui-btn ui-btn-green" :busy="promise">Click here</UButton>
    <UButton class="ui-btn ui-btn-blue" :busy="promise">Click here</UButton>
    <UButton class="ui-btn ui-btn-bordered" :busy="promise">Click here</UButton>
    <UButton class="ui-btn ui-btn-bordered-green" :busy="promise">Click here</UButton>
    <UButton class="ui-btn ui-btn-bordered-blue" :busy="promise">Click here</UButton>
    <UButton class="ui-btn ui-btn-bordered-gray" :busy="promise">Click here</UButton>
<br>
<UPreloader mode="simple" :activation="promise || true" :width="50"/>
<!-- <UTextInputEgg :egg="model" /> -->
<br>
<br>
<UButton class="ui-btn ui-btn-green" @click="genPromise">GenPromise</UButton>
<UButton class="ui-btn ui-btn-green" @click="res">Resolve</UButton>
<UButton class="ui-btn ui-btn-green" @click="rej">Reject</UButton>
<UButton class="ui-btn ui-btn-green" @click="boolean = !boolean">Change Bool (-> {{ !boolean }})</UButton>
<br>
    <div class="blog-block flex" v-if="false">
      <div class="blog-main-item flex">
        <div class="padded">
          <span class="date">February 21, 2020</span>
          <span class="title">The Most Important Indicator for Short-term Rental Property Managers</span>
          <UButton class="ui-btn-text">Read more</UButton>
        </div>
        <div class="image-block">
          <div>
            <img class="blog-image" src="../../assets/images/static/blog/family-holding-laptop.png">
          </div>
        </div>
      </div>
      <div class="blog-item">
        <img class="blog-image" src="https://via.placeholder.com/100">
        <span class="date">February 21, 2020</span>
        <span class="title">The Most Important Indicator for Short-term Rental Property Managers</span>
        <UButton class="ui-btn-text">Read more</UButton>
      </div>
      <div class="blog-item">
        <img class="blog-image" src="https://via.placeholder.com/100">
        <span class="date">February 21, 2020</span>
        <span class="title">How to safely deal with the crisis? Deep cleaning is a great start</span>
        <UButton class="ui-btn-text">Read more</UButton>
      </div>
      <div class="blog-item">
        <img class="blog-image" src="https://via.placeholder.com/100">
        <span class="date">February 21, 2020</span>
        <span class="title">The Real Cost of Delivering First Class Results</span>
        <UButton class="ui-btn-text">Read more</UButton>
      </div>
      <div class="blog-item">
        <img class="blog-image" src="https://via.placeholder.com/100">
        <span class="date">February 21, 2020</span>
        <span class="title">The Real Cost of Delivering First Class Results</span>
        <UButton class="ui-btn-text">Read more</UButton>
      </div>
      <div class="blog-item">
        <img class="blog-image" src="https://via.placeholder.com/100">
        <span class="date">February 21, 2020</span>
        <span class="title">The Real Cost of Delivering First Class Results</span>
        <UButton class="ui-btn-text">Read more</UButton>
      </div>
      <div class="blog-item">
        <img class="blog-image" src="https://via.placeholder.com/100">
        <span class="date">February 21, 2020</span>
        <span class="title">The Real Cost of Delivering First Class Results</span>
        <UButton class="ui-btn-text">Read more</UButton>
      </div>
    </div>
    <UPagination v-model="paginationModel" :chunkSize="20" :dataCount="231" :startPage="1" />

  </div>



  <UButton class="ui-btn ui-btn-green" @click="rndm">Randomize</UButton>
  <UButton class="ui-btn ui-btn-green" @click="rndmRentAnalyzer">Randomize Rent Analyzer</UButton>

  <br>
  {{ listM }}
<br>
  <div class="wrapper" style="padding: 10vh 10vw; width: 100%; min-height: 700px; position: relative;">
    <MapComponent>
      <!-- <SimpleMarker v-for="a of listM" :key="a" :lat="a.lat" :lng="a.lng"/> -->

      <!-- <PropertyMarker v-for="a of listM" :key="a" :data="a.data" :lat="a.lat" :lng="a.lng"/> -->

      <RentAnalyzerMarker v-for="a of listM" :key="a" :data="a.data" :lat="a.lat" :lng="a.lng" :type="a.type"/>
      <MapCircle :data="{}" :lat="rntLat" :lng="rntLng" :radius="circleRadius"/>
      <!-- <PictureMarker :data="{}" :lat="rntLat" :lng="rntLng" icon="map-icon-home.svg" :markerOptions="{ icon: {url: '/mapMarkerIcons/map-icon-home.svg',anchor: {x: 15, y: 15}} }"/> -->
      <PictureMarker :data="{}" :lat="rntLat" :lng="rntLng" icon="map-icon-home.svg"/>

    </MapComponent>
  </div>
  <Ufooter />
</template>
<style lang="less" scoped>
  span { display: block; }
  .unlock {
    position: relative;
    @s: 300px;
    width: @s;
    height: @s;
    // border-radius: @border-radius;
    border: 2px solid #000;
  }
  .page-title {
    font-size: 2.625rem;
    font-weight: 800;
    text-align: center;
    margin: 40px 0;

    @media @mobile {
      font-size: 1.85rem;
      margin: 30px 0;
    }
  }
  .blog-block {
    justify-content: space-between;

    &.flex {
      flex-wrap: wrap;
    }
    > div {
      margin-bottom: 40px;

      .title {
        font-weight: 800;
      }
      .date {
        font-weight: 700;
      }
      .ui-btn-text {
        font-weight: 800;
        text-transform: uppercase;
      }
    }
    .blog-main-item {
      position: relative;
      border-radius: @border-radius;
      background: @col-text-dark;
      justify-content: space-between;

      .image-block {
        position: absolute;
        right: 0;
        height: 100%;

        .blog-image {
          border-radius: 0 @border-radius @border-radius 0;
          height: 100%;
        }
        > div {
          position: relative;
          height: 100%;

          &::after {
            content: "";
            position: absolute;
            background: linear-gradient(270deg, rgba(34, 34, 34, 0) 0%, @col-text-dark 100%);
            width: 20%;
            height: 100%;
            left: 0;
            top: 0;
          }
        }
      }
      .date {
        color: @col-text-gray-darker;
      }
      .title {
        font-size: 2.25rem;
        line-height: 2.5rem;
        margin-top: 20px;
        color: @col-text-light;
      }
      .ui-btn-text {
        margin-top: 20px;
      }
      .padded {
        padding: 70px 0 70px 100px;
        width: 55%;
        z-index: 1;
      }
    }
    .blog-item {
      max-width: 350px;

      .blog-image {
        width: 100%;
        height: 200px;
        border-radius: @border-radius;
      }
      .date {
        color: @col-text-gray-darker;
        margin-top: 24px;
      }
      .title {
        font-size: 1.375rem;
        line-height: 1.5rem;
        margin-top: 16px;
      }
      .ui-btn-text {
        margin-top: 16px;
      }
    }

    @media @mobile {
      display: block;
      padding: 0 25px;

      .blog-main-item {
        display: block;
        position: relative;

        .image-block {
          position: absolute;
          top: 0;
          height: inherit;

          .blog-image { border-radius: @border-radius @border-radius 0 0; }
          > div {
            &::after {
              position: absolute;
              width: 100%;
              height: 30%;
              top: 70%;
              background: linear-gradient(180deg, rgba(34, 34, 34, 0) 0%, @col-text-dark 100%);
            }
          }
        }
        .blog-image {
          object-fit: cover;
          border-radius: @border-radius @border-radius 0 0;
          width: 100%;
        }
        .date {
          font-size: 1rem;
        }
        .title {
          font-size: 1.7rem;
          line-height: 2rem;
          margin-top: 15px;
          color: @col-text-light;
        }
        .ui-btn-text {
          margin-top: 15px;
        }
        .padded {
          width: 100%;
          position: relative;
          z-index: 1;
          padding: 200px 30px 30px 30px;
        }
      }
    }
  }
  .ui-pagination { margin: 0 auto 40px; }
</style>
<script lang="ts">
import { defineComponent } from 'vue';

import UPagination from '@/components/ui/UPagination.vue';
import UButton from '@/components/ui/UButton.vue';
import Ufooter from '@/components/static/footer.vue';
import UTextInput from '@/components/ui/UTextInput.vue';
import UPreloader from '@/components/ui/UPreloader.vue';

import UTextInputEgg from '@/components/ui/UTextInputEgg.vue';
import UFloatingTextareaEgg from '@/components/ui/UFloatingTextareaEgg.vue';
import USelectDropEgg from '@/components/ui/USelectDropEgg.vue';
import URadioChipEgg from '@/components/ui/URadioChipEgg.vue';
import URadioInputEgg from '@/components/ui/URadioInputEgg.vue';
import UToggleEgg from '@/components/ui/UToggleEgg.vue';
import UIncrementalEgg from '@/components/ui/UIncrementalEgg.vue';
import UCheckboxInputEgg from '@/components/ui/UCheckboxInputEgg.vue';
import UCheckboxChipEgg from '@/components/ui/UCheckboxChipEgg.vue';

import UnlockAnalytics from '@/components/OFRC/UnlockAnalytics.vue';

import AccountStore from '@/models/Account';

import { Model } from '@/models/Henhouse/TestModel.model';

import MapComponent from '@/components/OFRC/MapComponent/MapComponent.vue'
import SimpleMarker from '@/components/OFRC/MapComponent/SimpleMarker.vue'
import PropertyMarker from '@/components/OFRC/MapComponent/PropertyMarker.vue'
import RentAnalyzerMarker from '@/components/OFRC/MapComponent/RentAnalyzerMarker.vue'
import MapCircle from '@/components/OFRC/MapComponent/MapCircle.vue'
import PictureMarker from '@/components/OFRC/MapComponent/PictureMarker.vue'

export default defineComponent({
  components:{
    UPagination,
    UButton,
    Ufooter,
    UTextInput,
    UPreloader,

    UTextInputEgg,
    UFloatingTextareaEgg,
    USelectDropEgg,
    URadioChipEgg,
    URadioInputEgg,
    UToggleEgg,
    UIncrementalEgg,
    UCheckboxInputEgg,
    UCheckboxChipEgg,

    UnlockAnalytics,
    MapComponent,
    SimpleMarker,
    PropertyMarker,
    RentAnalyzerMarker,
    MapCircle,
    PictureMarker
  },
  data() {
    return {
      paginationModel: [0, 10],
      model: Model.building_size,
      modelEnum: Model.baths,
      modelString: Model.str,
      modelBoolean: Model.bool,
      modelArray: Model.arr,
      modelInc: Model.inc,
      inpt: '123',
      promise: undefined as Promise<any> | undefined,
      res: (V:any) => {},
      rej: () => {},
      boolean: true,
      listM: [] as any,
      circleRadius: 10,
      rntLat: 47.116386,
      rntLng: -101.299591,
    }
  },
  computed: {
    Account() {
      return AccountStore;
    }
  },
  methods: {
    genPromise() {
      this.promise = new Promise((res, rej) => {
        this.res = res;
        this.rej = rej;
      });
    },
    changePaymentMethod() {
      this.Account.Subscriptions.changePaymentMethod();
    },
    rndm() {
      this.listM = Array(12).fill(!1).map(e => {
        return {
          lat: 47.116386 + (-3 + Math.random() * 6),
          lng: -101.299591 + (-3 + Math.random() * 6),
          data: {}
        }
      });
    },
    rndmRentAnalyzer() {
      const markers = ['lower', 'moderate', 'higher'];
      this.listM = Array(20).fill(!1).map(e => {
        return {
          lat: 47.116386 + (-3 + Math.random() * 6),
          lng: -101.299591 + (-3 + Math.random() * 6),
          type: markers[Math.floor(Math.random()*markers.length)],
          data: {}
        }
      });
      // this.circleRadius = Math.floor(Math.random() * 20) + 5;
      // this.rntLat = 47.116386 + (-3 + Math.random() * 6);
      // this.rntLng = -101.299591 + (-3 + Math.random() * 6);
    }
  },
  mounted() {
    Model.building_size.setDefault(123);
    Model.building_size.reset();
  }
})
</script>