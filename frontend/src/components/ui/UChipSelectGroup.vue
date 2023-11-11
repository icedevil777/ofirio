<template>
  <div class="ui-chip-select-group flex">
    <slot></slot>
  </div>
</template>

<style lang="less" scoped>
.ui-chip-select-group {
  @h: 50px;
  @p: 5px;

  border: 1px solid @col-gray-light;
  height: @h;
  border-radius: @h/2;
  justify-content: center;
  align-items: center;
  align-content: center;
  padding: @p;

  &::v-deep .ui-radio-chip {
    white-space: nowrap;
    height: @h - 2*@p;
    line-height: @h - 2*@p;
    border-radius: @h/2 - @p;
    min-width: 140px;
    box-shadow: none;
    font-weight: 700;
    color: @col-text-gray-dark;
    padding: 0 20px;
    position: relative;
    font-size: 0.875rem;

    &:before {
      content: '';
      position: absolute;
      top: 0;
      left: -5px;
      display: block;
      height: @h - 4*@p;
      top: @p;
      width: 1px;
      background: transparent;
    }
    &:hover { background: @col-disabled; }
    &:hover + .ui-radio-chip:before { background: transparent; }
    & + .ui-radio-chip:before { background: @col-gray-light; }
    &.selected {
      background: @col-text-dark;
      color: @col-text-light;

      &:before, & + .ui-radio-chip:before { background: transparent; }
    }
  }
}
</style>