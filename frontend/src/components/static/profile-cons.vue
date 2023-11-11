<template>
  <div class="info flex">
    <div class="descriptions">
      <div class="text-block flex">
        <UIcon name="clock-backward" />
        <p>
          <span class="text-heading">Save time</span>
          Save months of research and find the best deals in seconds
        </p>
      </div>
      <div class="text-block flex">
        <UIcon name="house-dollar" />
        <p>
          <span class="text-heading">Invest smarter</span>
          Use AI Powered tools to search by CAP Rate, Cash on Cash Return, and much more
        </p>
      </div>
      <div class="text-block flex">
        <UIcon name="stocks-increase-wide" />
        <p>
          <span class="text-heading">Build Wealth</span>
          Reach your financial goals quickly with advanced wealth generation forecasts
        </p>
      </div>
    </div>
    <div class="secure-area">
      <UIcon name="lock-circle" /> Secure area
    </div>
  </div>
</template>

<style lang="less" scoped>
.info {
  padding: 30px;
  flex-direction: column;
  justify-content: space-between;
  align-items: flex-start;
  align-content: space-between;
  background: #f0f0f0;
  max-width: 315px;
  
  .descriptions {    
    .text-block {
      @first-row-height: 28px;

      justify-content: flex-start;
      align-content: flex-start;
      align-items: flex-start;
      margin-bottom: 30px;

      &::v-deep .svg-icon {
        width: @first-row-height;
        min-width: @first-row-height;
        height: @first-row-height;
        min-height: @first-row-height;
        margin-right: 15px;
        fill: @col-green;
      }
      p {
        color: @col-text-gray-darker;
        font-size: 0.875rem;
        line-height: 18px;
      }
      .text-heading {
        display: block;
        line-height: @first-row-height;
        margin-bottom: 8px;
        color: @col-text-gray-dark;
        font-weight: 800;
        font-size: 1rem;
      }
    }
  }
  .secure-area {
    @h: 18px;
    @col: #767676;
    
    color: @col;
    line-height: @h;
    font-size: 0.75rem;

    &::v-deep .svg-icon {
      fill: @col;
      stroke: @col;
      width: @h;
      height: @h;
      margin-right: @h/2;
      vertical-align: middle;
    }
    @media @mobile {
      display: none;
    }
  }
  @media @mobile {
    width: 100%;
    padding: 20px;
    max-width: none;
  }
}
</style>