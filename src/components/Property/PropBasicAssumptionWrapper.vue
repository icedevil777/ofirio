<template>
  <div class="basic-assumption-wrap"><slot></slot></div>
</template>

<style lang="less" scoped>
.basic-assumption-wrap {
  width: calc(50% - 20px);
  border-radius: @border-radius;
  padding: 30px;
  position: relative;

  @media @mobile {
    width: calc(100% - @mm * 2);
    margin: 0 @mm @mm;
    padding: @mm;
  }

  &::v-deep {
    span.heading {
      display: block;
      font-size: 1.5rem;
      font-weight: 700;
      margin-bottom: 1.25rem;

      @media @mobile { padding: 0; }
    }
    .svg-icon--pencil {
      @s: 20px;

      width: @s;
      height: @s;
      position: absolute;
      top: 30px;
      right: 30px;
      cursor: pointer;

      @media @mobile {
        top: 20px;
        right: 20px;
      }
    }
    .ui-tooltip {
      vertical-align: top;
      margin-right: 5px;
    }
    .fin-table {
      width: 100%;
      border-collapse: separate;

      & + .fin-table {
        margin-top: 40px;

        @media @mobile { margin-top: @mm; }
      }
      tr.divider {
        td {
          border-bottom: 1px solid transparent;
          padding: 0;
        }
        &.stripped td {
          border-bottom-style: dashed;
          border-bottom-color: @col-shadow;
        }
        &.solid {
          td {
            border-bottom-color: @col-text-gray-light;
            padding-bottom: 10px;
          }
          + tr td { padding-top: 20px; }
        }
      }
      tr.strip {
        background: #f9f9f9;
      }
      td {
        padding: 10px;
        white-space: nowrap;
      }
      td.head {
        color: @col-text-gray-darker;
        font-weight: 700;
        font-size: .9rem;
        text-align: right;
        border-bottom: 2px solid #efefef;

        &:first-child { text-align: left; }
      }
      td.title { font-weight: 700; }
      td.title-bigger {
        font-size: 1.125rem;
        vertical-align: middle;

        .svg-icon.svg-icon--smooth-arrow {
          @s: 1rem;
          width: 1rem;
          height: 1rem;
          vertical-align: middle;
          margin: 0 0 0 .5rem;
          cursor: pointer;

          &.rotate { transform: rotate(180deg); }
        }
      }
      td.name { color: @col-text-gray-darker; }
      td.value {
        font-weight: 600;
        text-align: right;

        &.trans-opacity { transition: opacity .3s ease; }
      }
      td.total {
        font-weight: 700;
      }
      td.interim {
        font-weight: 500;
        color: @col-text-gray-darker;
      }
      td.unit {
        padding-left: .5rem;
        font-size: .75rem;
        color: @col-text-gray-darker;
      }
      tr td:first-child { padding-left: 0; }
      tr td:last-child { padding-right: 0; }

      @media @mobile {
        td {
          white-space: normal;
          line-height: 1.15rem;
        }
      }
    }
  }
}
</style>
