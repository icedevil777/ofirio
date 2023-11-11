<template>
<div class="images">
  <div class="main-image">
    <img v-if="mainImage" :src="mainImage" alt="Main photo" @click="() => popupRef ? popupRef.open() : undefined">
    <img v-else src="@/assets/images/common/image-placeholder.png" alt="No Image" class="image-placeholder">
    <slot name="overMainImageSlot"></slot>
  </div>
  <div class="sub-images" v-if="imageList.length > 0">
    <div class="img-wrapper" v-for="(imgUrl, i) of imageList" :key="imgUrl">
      <img :src="imgUrl" alt="Additional photo" @click="() => popupRef ? popupRef.open() : undefined">

      <div class="more-images flex" v-if="i == imageList.length - 1 && images.length > 6">
        <span class="more" @click="() => popupRef ? popupRef.open() : undefined">+{{ images.length - 6 }} photos</span>
      </div>
    </div>
  </div>
</div>
</template>

<script lang="ts">
import { defineComponent, PropType } from 'vue'

export default defineComponent({
  props: {
    main: String,
    images: {
      required: true,
      type: Array as PropType<Array<string>>,
      default: []
    },
    popupRef: Object
  },
  computed: {
    mainImage():string {
      return this.main ? this.main : this.images[0];
    },
    imageList():string[] {
      return this.images.filter(i => i != this.mainImage).slice(0, 5);
    }
  }
})
</script>


<style lang="less" scoped>
.images {
  border-radius: @border-radius;
  overflow: hidden;

  img {
    display: block;
    object-fit: cover;
    cursor: pointer;
  }
  .main-image {
    width: 100%;
    position: relative;
    height: 0;
    padding-top: 65%;

    img {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;

      &.image-placeholder {
        object-fit: contain;
        padding: 25% 0;
        background: @col-gray-light;
        cursor: default;
      }
    }
  }
  .sub-images {
    @ih: 80px;

    height: @ih;
    position: relative;
    margin-top: 10px;
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    grid-template-rows: 1fr;
    gap: 0 10px;
    
    .img-wrapper {
      height: inherit;
      position: relative;

      img {
        height: 100%;
        width: 100%;
      }
    }
    .more-images {
      position: absolute;
      top: 0;
      right: 0;
      width: 100%;
      height: 100%;
      align-content: center;
      align-items: center;
      justify-content: center;

      span.more {
        @h: 2rem;
        @p: 10px;

        display: block;
        padding: @p;
        cursor: pointer;
        background: @col-bg;
        border-radius: @border-radius;
        box-shadow: @shadow @col-shadow;
        font-size: .75rem;
        height: @h;
        line-height: @h - @p;
      }
    }
  }
}
</style>