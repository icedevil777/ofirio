<template>
  <div class="search-component" :class="{ active: focused, 'mobile-fullscreen': mobileOriented }" data-nosnippet>
    <div class="input-wrapper flex" @click="() => { $refs.input.focus(); focus() }">
      <slot name="prepend" :active="focused"></slot>
      <input
        type="search"
        autocomplete="autocomplete-search"
        ref="input"
        v-model="searchString"
        @focus="focus"
        @blur="onBlur"
        @input="onInput"
        @keyup.enter="useFirst"
        :placeholder="placeholder"
        data-hj-allow
      >
      <slot name="postpend" :active="focused" :useFirst="useFirst">
        <UIcon v-if="icon" :name="icon" @click="useFirst" />
      </slot>
    </div>
    <div class="suggestion-list">
      <slot v-if="touched" name="prependResultBox" :select="select"></slot>
      <template v-if="touched == false && latestSearches.length > 0">
        <div class="notice flex">
          <span class="ui-text-bold">Latest searches</span>
          <UButton class="ui-btn-text-gray" @click="clearLatestSearches">Clear</UButton>
        </div>
        <template v-for="s of latestSearches" :key="s">
          <slot name="historyRow" :row="s" :select="select" :labelBy="labelBy">
            <div class="suggestion-row"  v-text="s.item[labelBy]" @click="select(s)"></div>
          </slot>
        </template>
      </template>
      <template v-else-if="suggestions.length > 0">
        <template v-for="s of suggestions" :key="s">
          <slot name="suggestionRow" :row="s" :select="select" :labelBy="labelBy">
            <div class="suggestion-row"  v-text="s.item[labelBy]" @click="select(s)"></div>
          </slot>
        </template>
      </template>
      <template v-else-if="queryInProgress">
        <slot name="searchInProgress">
          <div class="notice flex">
            <span class="ui-text-bold">Searching...</span>
          </div>
        </slot>
      </template>
      <template v-else>
        <template v-if="searchString?.length > 2">
          <slot name="nothingFoundNotEmpty" :select="select">
            <div class="notice flex">
              <span class="ui-text-bold">Nothing found</span>
            </div>
          </slot>
        </template>
        <template v-else>
          <slot name="nothingFoundEmpty">
            <div class="notice flex">
              <span>Please type at least 3 characters</span>
            </div>
          </slot>
        </template>
        
      </template>
      <slot v-if="touched" name="appendResultBox" :select="select"></slot>
    </div>
  </div>
</template>

<style lang="less" scoped>
.search-component {
  @h: 45px;
  @bg: #f6f6f6;
  @col-br: #e5e5e5;

  position: relative;

  @media @mobile {
    &.active.mobile-fullscreen {
      position: fixed;
      left: 0;
      top: 0;
      width: 100%;
      height: 100%;
      background: @col-bg;
      padding-top: 5px;
      z-index: 1000;
    }
  }
  .input-wrapper {
    width: 100%;
    height: @h;
    padding: 15px;
    border-radius: @border-radius;
    box-shadow: 0 0 0 1px @col-gray-light;
    justify-content: flex-start;
    align-items: center;
    border-bottom: 1px solid transparent;
    position: relative;
    z-index: 2;

    .svg-icon {
      @s: 1rem;

      margin: 0 0 0 15px;
      width: @s;
      height: @s;

      &.svg-icon--magnifier {
        fill: transparent;
        stroke: @col-text-dark;
        stroke-width: 2;
        cursor: pointer;
      }
    }
    > input {
      flex: 1;
      border: none;
      background: transparent;
      font-weight: 600;
      line-height: 1.375rem;
      max-width: 100%;

      &:focus { outline: none; }
      &::placeholder {
        font-weight: 500;
        color: @col-text-gray-dark;
      }

      /* clears the 'X' from Internet Explorer */
      &::-ms-clear,
      &::-ms-reveal {
        display: none;
        width: 0;
        height: 0; 
      }

      /* clears the 'X' from Chrome */
      &::-webkit-search-decoration,
      &::-webkit-search-cancel-button,
      &::-webkit-search-results-button,
      &::-webkit-search-results-decoration {
        display: none; 
      }
    }
  }
  &.active .input-wrapper {
    background: transparent;
    border-bottom-color: @col-br;
    border-radius: @border-radius @border-radius 0 0;
  }
  .suggestion-list {
    position: absolute;
    z-index: 1;
    top: 0;
    left: 0;
    width: 100%;
    padding: @h 15px 0;
    border-radius: @border-radius;
    background: @col-bg;
    box-shadow: 0px 3px 10px rgba(0, 0, 0, 0.1);
    border: 1px solid transparent;
    font-size: .9375rem;
    visibility: hidden;
    opacity: 0;
    transform: rotateX(45deg);
    transform-origin: top center;
    transition: border-color .1s ease, transform .3s ease, opacity .2s ease, visibility .2s ease;

    @media @mobile {
      box-shadow: none;
      border-bottom: 0;
      max-height: calc(100*var(--vh) - @header-height-mobile);
      overflow-y: auto;
    }
    .notice {
      justify-content: space-between;
      align-content: center;
      align-items: center;
      height: 1.25rem;
      margin-top: 15px;

      .ui-button {
        font-weight: 500;
        text-decoration: underline;
        color: @col-text-gray-darker;
      }
    }
    &::v-deep {

      .suggestion-row {
        height: 1.5rem;
        line-height: 1.5rem;
        margin-top: 15px;
        cursor: pointer;

        &:hover { color: @col-blue; }
      }
      > :first-child { margin-top: 20px; }
      > :last-child { margin-bottom: 15px; }
    }
  }
  &.active .suggestion-list {
    opacity: 1;
    transform: rotateX(0);
    visibility: visible;
    border-color: @col-br;
  }
}
</style>

<script lang="ts">
import { defineComponent } from 'vue';

import UButton from '@/components/ui/UButton.vue';
import { debounce } from 'ts-debounce';

const localStorageName = 'ofirio-saved-searches';

export type TAutoCompleteSuggestion<T> = {
  item: T,
  prefixName?: string
}

export default defineComponent({
  components: {
    UButton
  },
  props: {
    searchFunction: { required: true, type: Function },
    debounce: { default: 1000, type: Number },
    inactive: { default: false, type: Boolean },
    mobileOriented: { default: true, type: Boolean },
    labelBy: { default: 'label', type: String },
    placeholder: String,
    icon: String
  },
  emits: [ 'selected', 'setSaved' ],
  data() {
    return {
      debouncedQuery: this.debounce == 0 ? this.query : debounce(<any>this.query, this.debounce),
      lastQuerySendTime: 0,
      queryInProgress: false,
      searchString: '',
      focused: false,
      touched: false,
      suggestions: [] as Array<TAutoCompleteSuggestion<any>>,
      latestSearches: [] as Array<TAutoCompleteSuggestion<any>>
    }
  },
  methods: {
    query(str: string, cb: Function) {
      let localTime = Date.now();
      this.lastQuerySendTime = localTime;
      this.queryInProgress = true;

      this.searchFunction(str).then((res:any) => {
        if (localTime != this.lastQuerySendTime)
          return;

        this.queryInProgress = false;
        cb(res);
      });
    },
    onInput(ev: InputEvent) {
      if (this.inactive)
        return;

      this.focus();
      this.touched = true;
      if (this.debounce > 0)
        this.suggestions = [];

      const target = ev.target as HTMLInputElement;
      const value = <string>target.value;
      
      if (value.length == 0)
        return this.touched = false;

      if (value.length < 3)
        return;

      this.debouncedQuery(value, (res: Array<TAutoCompleteSuggestion<any>>) => {
        this.suggestions = res;
      });
    },
    focus() {
      this.focused = !this.inactive && true;
    },
    onBlur() {
      setTimeout(() => this.focused = false, 100)
    },
    select(row: TAutoCompleteSuggestion<any> | null) {
      this.touched = false;

      if (row != null) {
        this.searchString = row.item[this.labelBy];

        if (this.latestSearches.every(s => s.item[this.labelBy] != row.item[this.labelBy])) {
          this.latestSearches.splice(0, 0, row);
          if (this.latestSearches.length > 3)
            this.latestSearches.pop();
        }
      }

      this.$emit('setSaved', this.latestSearches);
      this.$emit('selected', row == null ? null : row.item);
    },
    useFirst() {
      const list = this.touched == false && this.latestSearches.length > 0 ? this.latestSearches : this.suggestions;
      const isUsingLastList = list == this.latestSearches;

      if (this.queryInProgress)
        return;
      
      if (list.length < 1)
        if (this.searchString?.length < 3)
          return;
        else {
          (<any>this.$refs).input.blur();
          return this.select(null);
        }
      
      if (!this.focused && isUsingLastList)
        return;

      (<any>this.$refs).input.blur();
      this.select(list[0]);
    },
    clearLatestSearches() {
      this.latestSearches = [];
      this.$emit('setSaved', []);
    },
    setLatestSearches(arr: Array<TAutoCompleteSuggestion<any>>) {
      this.latestSearches = arr;
    },
    setValue(str: string) {
      this.searchString = str;
    },
    getSearchvalue() {
      return this.searchString.toString();
    }
  }
});
</script>