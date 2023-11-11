<template>
  <UAutocomplete
    class="header-search-component"
    icon="magnifier"
    :searchFunction="searchFunction"
    :debounce="0"
    :mobileOriented="$attrs.mobileOriented"
    placeholder="Search by city, state, zip code, or address"
    @selected="onSelect"
    @setSaved="setSaved"
    ref="search"
  >
    <template v-slot:prepend="{ active }" v-if="$isMobile.value">
      <UIcon name="bold-arrow" class="back-arrow" :class="{ active }" @click="() => $refs.search.$refs.input.blur()" />
    </template>
    <template v-slot:suggestionRow="{ row, select, labelBy }">
      <div class="suggestion-row flex" @click="select(row)">
        <span class="type">{{ row.item.type }}</span>
        <span class="label">{{ row.item[labelBy] }}</span>
      </div>
    </template>
    <template v-slot:nothingFoundNotEmpty><div></div></template>
    <template v-slot:appendResultBox="{ select }">
      <div class="suggestion-row flex" @click="select(null)">
        <span class="type">Search On Map</span>
        <span class="label">{{ getCurrentSearchValue() }}</span>
      </div>
    </template>
    <template v-for="(_, name) in $slots" v-slot:[name]="slotData" :key="name"><slot :name="name" v-bind="slotData" /></template>
  </UAutocomplete>
</template>

<style lang="less" scoped>
@bg: #f6f6f6;
@col-br: #e5e5e5;
@h: 50px;

.header-search-component ::v-deep {
  .input-wrapper {
    background: @bg;
    box-shadow: none;
    height: @h;

    @media @mobile { height: 40px; }

    .back-arrow {
      @s: 16px;

      width: @s;
      min-width: @s;
      height: @s;
      min-height: @s;
      margin-right: 10px;
      display: none;
      transform: rotate(270deg);

      &.active { display: block; }
    }
  }
  .suggestion-list {
    padding-top: @h;

    @media @mobile {
      padding-top: 40px;
      padding-left: 15px + 16px + 10px;
    }

    .suggestion-row {
      justify-content: flex-start;
      align-items: center;

      .type {
        margin-right: 10px;
        font-weight: 600;
        color: @col-text-gray;
        font-size: .75rem;
        text-transform: uppercase;
      }
    }
  }
}
</style>

<script lang="ts">
import { defineComponent } from 'vue';

import { TSearchSuggestion } from '@/models/Search/api';
import { autoCompleteQuery, toObject, toUrl, getRectQuery } from '@/models/Search';
import UAutocomplete, { TAutoCompleteSuggestion } from '../ui/UAutocomplete.vue';

const localStorageName = 'ofirio-saved-searches';

export default defineComponent({
  props: {
    syncWith: Object
  },
  components: {
    UAutocomplete
  },
  data() {
    return {
      lastQueryTime: 0
    }
  },
  methods: {
    getCurrentSearchValue() {
      const ref = (<any>this.$refs.search)
      if (!ref)
        return '';

      return ref.getSearchvalue();
    },
    setCurrentSearchValue(value: string) {
      const ref = (<any>this.$refs.search)
      if (!ref)
        return;

      ref.setValue(value);
    },
    async searchFunction(str: string) {
      const res = await autoCompleteQuery(str);
      return res.map(e => ({ item: e }));
    },
    onSelect(row: TSearchSuggestion | null) {
      const req = this.getCurrentSearchValue();

      if (this.syncWith)
        this.syncWith.setCurrentSearchValue(req);

      if (row == null) {
        const queryTime = Date.now();
        this.lastQueryTime = queryTime;
        return getRectQuery(req).then((res) => {
          if (this.lastQueryTime != queryTime)
            return;

          let typeOptions = toUrl(Object.assign({}, res == false ? { geo_rect: '24.9493,-125.0011,49.5904,-65.9326' } : res, { label: undefined, type: undefined }));
          const params = this.$route.name == 'search' ? { ...this.$route.params, typeOptions } : { typeOptions };
          window.localStorage.setItem('ofirio-from-search', 'true');
          this.$router.push({ name: 'search', params });
          
          if (res == false)
            (<any>this.$root).$refs.globMessages.push({ type: 'warning', message: 'We could not find this area. Please check your spelling or enter a valid ZIP code.' }, 8000);
        });
      }

      else if (row.type == 'address' && row.prop_id)
        this.$router.push({ name: 'property', params: { id: row.prop_id }});

      else {
        let typeOptions = toUrl(Object.assign({}, row, { label: undefined, type: undefined }));
        const params = this.$route.name == 'search' ? { ...this.$route.params, typeOptions } : { typeOptions };
        this.$router.push({ name: 'search', params });
      }
    },
    setSaved(items: TAutoCompleteSuggestion<TSearchSuggestion>) {
      localStorage.setItem(localStorageName, JSON.stringify(items));
      (<any>this.$root).$refs.header.$refs.headerSearch.loadSaved();
    },
    loadSaved() {
      const searchRef = <any>this.$refs.search;
      const saved = localStorage.getItem(localStorageName);
      if (saved)
        searchRef.setLatestSearches(<Array<TAutoCompleteSuggestion<TSearchSuggestion>>>JSON.parse(saved));
    },
    loadSearchStringFromURL() {
      const searchRef = <any>this.$refs.search;
      
      if (this.$route.name == 'search' && searchRef.getSearchvalue().length == 0) {
        const query = toObject((<any>this.$route.params).typeOptions);
        searchRef.setValue([
          query.zip,
          query.city,
          query.county,
          query.state_id
        ].filter(q => q != undefined).join(', '));
      }
    },
  },
  mounted() {
    this.loadSaved();

    let watchOnLoadedOnce = this.$watch('$route', (newVal: any) => {
      if (newVal == undefined)
        return;

      watchOnLoadedOnce();
      this.loadSearchStringFromURL();
    });
  }
});
</script>