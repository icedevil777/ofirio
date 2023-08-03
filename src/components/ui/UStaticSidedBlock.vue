<template>
  <div class="wrapper-wide" :class="{ 'title-left': titleSide == 'left', 'title-right': titleSide == 'right' }">
    <div class="wrapper flex">
      <div class="title-block">
        <slot name="side" />
      </div>
      <div class="image-block">
        <slot name="image" />
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import UButton from '@/components/ui/UButton.vue';

export default defineComponent({
  props: {
    titleSide: { type: String, required: true}  
  },
  components: {
    UButton
  },
})
</script>

<style lang="less" scoped>
  .wrapper-wide {
    border-radius: @border-radius;
    padding: 60px 0;
    margin-bottom: 150px;
    position: relative;

    &.title-left {
      background: @col-disabled;
      .image-block {
        top: 42px;
        left: 55%;

        @media @mobile { left: 60%; }
      }
    }
    &.title-right {
      background: #E5F8F2;
      .wrapper { justify-content: flex-end; }
      .image-block {
        top: 42px;
        right: 55%;

        @media @mobile { right: 60%; }
      }
      @media @mobile { background: @col-bg; }
    }
    @media @mobile {
      max-width: 100%;
      border-radius: 0;
      padding: 50px 20px;
      margin: 0;
      overflow: hidden;

      &.title-left, &.title-right {
        .image-block { top: calc(50% - 250px); }
      }
    }
  }
  .wrapper {
    &::v-deep {
      .title-block {
        width: 45%;
        text-align: left;
    
        .points {
          margin-top: 30px;

          .points-item {
            margin-top: 16px;
            display: flex;
    
            > span { margin-left: 18px; }
            @media @mobile {
              margin-top: 20px; 
              > span { margin-left: 12px; }
            }
          }
          .svg-icon {
            width: 15px;
            height: 15px;
            fill: @col-green;
            flex-shrink: 0;
          }
          .text {
            font-size: 1rem;
            font-weight: 400;
            color: @col-text-gray-dark;
            margin: 0;
          }
        }
        .ui-button { display: inline-block }
        .ui-btn {
          padding: 16px 78px;
          margin-top: 36px;
        }
        .ui-btn-text {
          font-size: 1.15rem;
          font-weight: 800;
          margin-top: 30px;
        }

        @media @mobile {
          width: 60%;
        }
      }
      .image-block {
        position: absolute;
        
        img { height: 520px; }
      }
    }
  }





  // .how-ofirio-works-wrapper {
  //   overflow: hidden;
  //   position: relative;
  // }
  // .how-ofirio-works {
  //   border-radius: @border-radius;
  //   padding: 60px 0;
  //   margin-bottom: 150px;

  //   &.title-left {
  //     background: @col-disabled;
  //     .image-block {
  //       top: 42px;
  //       left: 55%;
  //     }
  //   }
  //   &.title-right {
  //     background: #E5F8F2;
  //     .wrapper { justify-content: flex-end; }
  //     .image-block {
  //       top: 42px;
  //       right: 55%;
  //     }
  //   }
  //   .title-block {
  //     width: 45%;
  //     text-align: left;

  //     .points {
  //       margin-top: 30px;
  //       .points-item {
  //         margin-top: 16px;
  //         display: flex;

  //         div {
  //           margin-left: 18px;
  //         }
  //       }
  //       .svg-icon {
  //         width: 15px;
  //         height: 15px;
  //         fill: @col-green;
  //         flex-shrink: 0;
  //       }
  //       .text {
  //         font-size: 1rem;
  //         font-weight: 400;
  //         color: @col-text-gray-dark;
  //         margin: 0;
  //       }
  //     }
  //     .ui-button { display: inline-block }
  //     .ui-btn {
  //       padding: 16px 78px;
  //       margin-top: 36px;
  //     }
  //     .ui-btn-text {
  //       font-size: 1.15rem;
  //       font-weight: 800;
  //       margin-top: 30px;
  //     }
  //   }
  //   .image-block {
  //     position: absolute;
      
  //     img { height: 520px; }
  //   }

  //   @media @mobile {
  //     max-width: 100%;
  //     border-radius: 0;
  //     padding: 50px 20px;
  //     margin: 0;

  //     .title-block {
  //       width: 60%;
  //     }
  //     &.title-left {
  //       .image-block {
  //         top: calc(50% - 250px);
  //         left: 60%;
  //       }
  //     }
  //     &.title-right {
  //       background: none;
  //       .image-block {
  //         top: calc(50% - 250px);
  //         right: 60%;
  //       }
  //     }
  //     .title-block {
  //       .points {
  //         .points-item {
  //           margin-top: 20px;
  //           > div { margin-left: 12px; }
  //         }
  //       }
  //     }
  //   }
  // }
</style>