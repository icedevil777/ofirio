<template>
  <UPageHeader>
    <h1 class="title">About Us</h1>
    <p class="text hide-mobile">We are on a mission to help smart investors invest smarter, save time, and grow their wealth quickly</p>
  </UPageHeader>
  <div class="how-it-started flex wrapper">
    <span class="title hide-desktop">How It All Started</span>
    <div class="grid-container">
      <div class="top-image"><img class="image-item" src="../../assets/images/static/about-us/house-roof-view.png"></div>
      <div class="bottom-image-1"><img class="image-item" src="../../assets/images/static/about-us/house-sunset.png"></div>
      <div class="bottom-image-2"><img class="image-item" src="../../assets/images/static/about-us/four-houses-panorama.png"></div>
    </div>
    <div class="content">
      <span class="title hide-mobile">How It All Started</span>
      <span class="text">
        Our journey began back in 2014. We were a group of friends and real estate investors who wanted to do well with our properties, acquiring and renting them out. We had no idea that this ambition would later grow to become Ofiro. As we invested in real estate ourselves, we ran into a big problem: we realized just how extremely time consuming and complicated it was to find a good deal. We were using several separate tools and keeping track of all of the research with spreadsheets. We knew there was a better way! As the saying goes, “if you want it done right, you gotta do it yourself” - and so we built the most comprehensive set of real estate investment tools that are backed by real-time data and artificial intelligence - everything we desperately wished we had during all those years of research. Now we bring these tools to you, to help you save your time, invest smarter, and grow your wealth quicker. Everything we do is a labor of love - by real estate people for real estate people.
      </span>
    </div>
  </div>
  <UDivider />
  <USuccessStories />
  <UGetStarted />
  <OFRC_FindInvestment wavePosition="top"/>
  <Ufooter />
</template>

<script lang="ts">
import {defineComponent} from 'vue';
import UPageHeader from '@/components/ui/UPageHeader.vue'
import UDivider from '@/components/ui/UDivider.vue';
import UButton from '@/components/ui/UButton.vue';
import Ufooter from '@/components/static/footer.vue';
import OFRC_FindInvestment from '@/components/OFRC/FindInvestment.vue';
import UGetStarted from '@/components/static/get-started.vue';
import USuccessStories from '@/components/static/success-stories.vue';

export default defineComponent({
  components:{
    UPageHeader,
    UDivider,
    UButton,
    Ufooter,
    OFRC_FindInvestment,
    UGetStarted,
    USuccessStories,
  }
})
</script>

<style lang="less" scoped>
  .static-page-header { background-image: url("../../assets/images/static/about-us/header-bg.png"); }
  span { display: block;}
  .ui-divider { 
    margin: 90px 0;
    @media @mobile { margin: 50px 0; }
  }
  .how-it-started {
    margin: 60px auto 90px auto;
    justify-content: space-between;

    .grid-container {
      width: 43%;
      display: grid;
      grid-template-columns: 1fr 1fr;
      grid-template-rows: 1fr 1fr;
      gap: 20px 20px;
      grid-template-areas:
        "top-image top-image"
        "bottom-image-1 bottom-image-2";
    }
    .top-image {
      grid-area: top-image;
      img { width: 100%; }
    }
    .bottom-image-1 {
      grid-area: bottom-image-1;
      img { width: 100%; }
    }
    .bottom-image-2 {
      grid-area: bottom-image-2;
      img { width: 100%; }
    }
    .content { width: 43%; }
    .text {
      font-size: 1.125rem;
      line-height: 1.75rem;
      font-weight: 400;
      color: @col-text-gray-dark;
      margin-top: 24px;
    }
    .title {
      font-size: 2.25rem;
      font-weight: 800;
      text-align: center;
      margin-bottom: 40px;
    }
    @media @mobile {
      flex-direction: column;
      padding: 0 25px;
      margin: 36px auto 50px auto;

      .grid-container, .content { width: 100%; }
      .title {
        font-size: 1.85rem;
        margin-bottom: 30px;
      }
      .text { font-size: 1.15rem; }
    }
  }
</style>