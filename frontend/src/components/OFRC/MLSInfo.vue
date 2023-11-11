<template>
  <div v-if="mls == 'all' || mls == 'miami'" class="mls-info">
    <span v-if="mls == 'all'" class="mls-name">Miami Association of Realtors (Miami Gateway MLS)</span>
    <img src="@/assets/images/common/miami-mls-logo.png" class="mls-logo" alt="Miami Realtors MLS logo">
    <p class="ui-text-justify">
      &copy; {{ currentYear }} Miami Association of REALTORS®. All rights reserved. The data relating to real estate on this website comes in part from the Internet Data Exchange program of the MLS of the Miami Association of REALTORS®. All information is deemed reliable but not guaranteed by the MLS and should be independently verified. The MLS, this broker and their affiliates provide all content therein “AS IS” and without any warranty, express or implied. This data is not verified for authenticity or accuracy and may not reflect all real estate activity in the market. Data displayed may be a portion of and not a complete set of all listings published in the MLS. The information included in this listing is provided exclusively for consumers’ personal, non-commercial use and may not be used for any purpose other than to identify prospective properties consumers may be interested in purchasing. This property is offered without respect to any protected classes in accordance with the law. Data displayed may be a portion of, and not a complete set of all listings published in the MLS.<br>
      <template v-if="mlsDate.miami">Last updated on: {{ $format['dateTime'](mlsDate.miami) }}.</template> 
      If you have any questions regarding the accuracy of this data, please contact us at <a href="mailto:help@ofirio.com" class="ui-href ui-href-underline">help@ofirio.com</a>.
    </p>
  </div>
  <div v-if="mls == 'all' || mls == 'stellar'" class="mls-info">
    <span v-if="mls == 'all'" class="mls-name">Greater Tampa Association of Realtors (StellarMLS)</span>
    <img src="@/assets/images/common/stellar-mls-logo.png" class="mls-logo" alt="Stellar MLS logo">
    <p class="ui-text-justify">
      The real estate listing data marked with this icon comes from the IDX program of the Stellar MLS system. All information provided is deemed reliable but is not guaranteed and should be independently verified. Listings displayed on this website may be subject to prior sale or removal from sale; availability of any listing should always be independently verified. Data displayed may be a portion of and not a complete set of all listings published in the MLS. Information is provided exclusively for consumers' personal, non-commercial use and may not be used for any purpose other than to identify prospective properties consumers may be interested in purchasing; all other use is strictly prohibited and may violate relevant federal and state law. Real estate listings held by brokerage firms other than Ofirio LLC are marked with the listing broker’s name and detailed information about such listings includes the name of the listing brokers. Copyright {{ currentYear }} My Florida Regional Multiple Listing Service DBA Stellar MLS. All rights reserved.<br>
      <template v-if="mlsDate.stellar">Last updated on: {{ $format['dateTime'](mlsDate.stellar) }}.</template> 
      If you have any questions regarding the accuracy of this data, please contact us at <a href="mailto:help@ofirio.com" class="ui-href ui-href-underline">help@ofirio.com</a>.
    </p>
  </div>
  <div v-if="mls == 'all' || mls == 'broward'" class="mls-info">
    <span v-if="mls == 'all'" class="mls-name">Broward, Palm Beach, St. Lucie Realtors (BeachesMLS)</span>
    <img src="@/assets/images/common/beaches-mls-logo.png" class="mls-logo" alt="Beaches MLS logo">
    <p class="ui-text-justify">
      All listings featuring the BMLS logo are provided by Beaches MLS, Inc. Beaches MLS, Inc, Ofirio LLC, and their affiliates provide all content therein “AS IS” and without any warranty, express or implied. This data is not verified for authenticity or accuracy and may not reflect all real estate activity in the market. Data displayed may be a portion of and not a complete set of all listings published in the MLS. This information should be independently verified if any person intends to engage in a transaction in reliance upon it. Information is provided exclusively for consumers' personal, non-commercial use and may not be used for any purpose other than to identify prospective properties consumers may be interested in purchasing. Real estate listings held by brokerage firms other than Ofirio LLC are marked with the listing broker’s name and detailed information about such listings includes the name of the listing brokers. The data relating to real estate on this website comes in part from the Internet Data Exchange program of the MLS. Copyright {{ currentYear }} Beaches Multiple Listing Service, Inc. All rights reserved.<br>
      <template v-if="mlsDate.broward">Last updated on: {{ $format['dateTime'](mlsDate.broward) }}.</template> 
      If you have any questions regarding the accuracy of this data, please contact us at <a href="mailto:help@ofirio.com" class="ui-href ui-href-underline">help@ofirio.com</a>.
    </p>
  </div>
  <div v-if="mls == 'all' || mls == 'matrix'" class="mls-info">
    <span v-if="mls == 'all'" class="mls-name">Naples Area Board of Realtors (SWFLA MLS, Bonita-Estero MLS, and Royal Palm Coast MLS)</span>
    <p class="ui-text-justify">
      The source of this real property information is the copyrighted and proprietary database compilation of the constituent organizations of the Southwest Florida MLS. Copyright {{ currentYear }} the Southwest Florida MLS organizations. All rights reserved. The MLS, Ofirio LLC, and their affiliates provide all content therein “AS IS” and without any warranty, express or implied. This data is not verified for authenticity or accuracy and may not reflect all real estate activity in the market. Data displayed may be a portion of and not a complete set of all listings published in the MLS. This information should be independently verified if any person intends to engage in a transaction in reliance upon it. Information is provided exclusively for consumers' personal, non-commercial use and may not be used for any purpose other than to identify prospective properties consumers may be interested in purchasing. Real estate listings held by brokerage firms other than Ofirio LLC are marked with the listing broker’s name and detailed information about such listings includes the name of the listing brokers. The data relating to real estate on this website comes in part from the Internet Data Exchange program of the MLS.<br>
      <template v-if="mlsDate.matrix">Last updated on: {{ $format['dateTime'](mlsDate.matrix) }}.</template> 
      If you have any questions regarding the accuracy of this data, please contact us at <a href="mailto:help@ofirio.com" class="ui-href ui-href-underline">help@ofirio.com</a>.
    </p>
  </div>
  <div v-if="mls == 'all' || mls == 'real'" class="mls-info">
    <span v-if="mls == 'all'" class="mls-name">RealMLS (NEFMLS)</span>
    <p class="ui-text-justify">
      The Northeast Florida Multiple Listing Service, Inc., Ofirio LLC, and their affiliates provide all content therein “AS IS” and without any warranty, express or implied. This data is not verified for authenticity or accuracy and may not reflect all real estate activity in the market. Data displayed may be a portion of and not a complete set of all listings published in the MLS. This information should be independently verified if any person intends to engage in a transaction in reliance upon it. Information is provided exclusively for consumers' personal, non-commercial use and may not be used for any purpose other than to identify prospective properties consumers may be interested in purchasing. Real estate listings held by brokerage firms other than Ofirio LLC are marked with the listing broker’s name and detailed information about such listings includes the name of the listing brokers. The data relating to real estate for sale on this website comes in part from the Internet Data Exchange (IDX) program of the Northeast Florida Multiple Listing Service, Inc. Copyright {{ currentYear }} Northeast Florida Multiple Listing Service, Inc. All rights reserved.<br>
      <template v-if="mlsDate.real">Last updated on: {{ $format['dateTime'](mlsDate.real) }}.</template> 
      If you have any questions regarding the accuracy of this data, please contact us at <a href="mailto:help@ofirio.com" class="ui-href ui-href-underline">help@ofirio.com</a>.
    </p>
  </div>
</template>

<script lang="ts">
import {defineComponent} from 'vue';

export default defineComponent({
  props: {
    mls: { default: 'all', type: String },
    mlsDate: { required: true, type: [Object, String] }
  },
  computed: {
    currentYear() {
      return new Date().getFullYear();
    }
  }
})
</script>

<style lang="less" scoped>
  .mls-logo {
    width: 150px;
    margin: 25px 0;
  }
</style>