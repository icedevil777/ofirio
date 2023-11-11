<template>
<div class="search-page">
  <div class="search-header flex padded">
    <div class="mobile-mm"></div>
    <div class="cash-type flex" v-if="!$isMobile.value">
      <URadio value="cash" name="payment_type" v-model="customization.values.priceMode">Cash</URadio>
      <UDrop>
        <template v-slot:label>
          <URadio value="mortgage" name="payment_type" v-model="customization.values.priceMode"></URadio>
          <span class="udrop-label" :class="{'udrop-label-selected': customization.values.priceMode == 'mortgage'}">Mortgage</span>
          <UIcon name="smooth-arrow" />
        </template>
        <template v-slot:content="{ props }">
          <UDropAdjustment @apply="recalcMortgage(), props.close()" @reset="resetParam(['down_payment', 'loan_type'])">
            <span class="label">Downpayment (%)</span>
            <USelect v-model="customization.values.down_payment" :options="down_payment_types" label-by="label" close-on-select/>
            <span class="label">Loan Term</span>
            <USelect v-model="customization.values.loan_type" :options="loan_types" label-by="label" close-on-select/>
            <span class="label">Interest (%)</span>
            <span class="interest-rate">{{ $format['%'](customization.values.interest_rate) }}</span>
          </UDropAdjustment>
        </template>
      </UDrop>
    </div>
    <div class="filters flex">
      <UDrop class="cap-coc-drop" v-if="!$isMobile.value">
        <template v-slot:label>
          <span
            class="modified"
            v-show="customization.defaults.coc_rate != customization.values.coc_rate"
          ></span>
          Cash on Cash
          <UIcon name="smooth-arrow" />
        </template>
        <template v-slot:content="{ props }">
          <UDropAdjustment @apply="refresh(), props.close()" @reset="resetParam('coc_rate')">
            <span class="label">Cash on Cash</span>
            <USlider v-model="customization.values.coc_rate" @mousedown="!Account.Restrictions.canUseCustomization() && props.close()" v-bind="DataModel['slider__coc_return']" />
            <UTextInput @enter="refresh(), props.close()" v-model="customization.values.coc_rate" v-bind="DataModel['coc_return']" :debounce="1000" :formatter="$format['%Int']" subtype="percent" validationMessageShow></UTextInput>
          </UDropAdjustment>
        </template>
      </UDrop>
      <UDrop class="cap-coc-drop" v-if="!$isMobile.value">
        <template v-slot:label>
          <span
            class="modified"
            v-show="customization.defaults.cap_rate != customization.values.cap_rate"
          ></span>
          Cap Rate
          <UIcon name="smooth-arrow" />
        </template>
        <template v-slot:content="{ props }">
          <UDropAdjustment @apply="refresh(), props.close()" @reset="resetParam('cap_rate')">
            <span class="label">Cap Rate</span>
            <USlider v-model="customization.values.cap_rate" @mousedown="!Account.Restrictions.canUseCustomization() && props.close()" v-bind="DataModel['slider__cap_rate']" />
            <UTextInput @enter="refresh(), props.close()" v-model="customization.values.cap_rate" v-bind="DataModel['cap_rate']" :debounce="1000" :formatter="$format['%Int']" subtype="percent" validationMessageShow></UTextInput>
          </UDropAdjustment>
        </template>
      </UDrop>
      <UDrop class="filter-price-drop" v-if="!$isMobile.value">
        <template v-slot:label>
          <span
            class="modified"
            v-show="customization.defaults.price[0] != customization.values.price[0] || customization.defaults.price[1] != customization.values.price[1]"
          ></span>
          Price
          <UIcon name="smooth-arrow" />
        </template>
        <template v-slot:content="{ props }">
          <UDropAdjustment @apply="refresh(), props.close()" @reset="resetParam('price')">
            <USlider v-model="customization.values.price" :min="customization.defaults.price[0]" :max="customization.defaults.price[1]" :step="1000" :tooltips="false" />
            <div class="flex input-to-input">
              <UTextInput @enter="refresh(), props.close()" vertical v-model="customization.values.price[0]" :debounce="1000" prepend="Min Price" prefix="$" type="number" :step="1000" :min="customization.defaults.price[0]" :max="customization.defaults.price[1]" :formatter="$format['usdInt']" />
              <span>To</span>
              <UTextInput :replacers="[undefined, $format['usdInt'](customization.defaults.price[1]) + '+']" @enter="refresh(), props.close()" vertical v-model="customization.values.price[1]" :debounce="1000" prepend="Max Price" prefix="$" type="number" :step="1000" :min="customization.defaults.price[0]" :max="customization.defaults.price[1]" :formatter="$format['usdInt']" />
            </div>
          </UDropAdjustment>
        </template>
      </UDrop>
      <UButton class="ui-btn ui-btn-bordered-gray flex filters-button" :class="{ 'applied': customizationDiff.length > 0 }" @click="$refs.customizationPopup.open()">
        <UIcon name="adjustments" />
        <span class="filters-text" v-show="!$isMobile.value || ($isMobile.value && (!Account.Auth.isLoggedIn || customizationDiff.length == 0))">Filters</span>
        <span class="ui-counter" v-text="customizationDiff.length" v-show="customizationDiff.length > 0 && Account.Auth.isLoggedIn"></span>
      </UButton>
      
    </div>
    <div class="chip-list">
      <DiffChips :resetter="resetParam" :customizationDiff="customizationDiffChips" :customization="customization" />
    </div>
    <div class="mobile-mm"></div>
  </div>
  <div class="search-results flex">
    <div class="list padded" v-show="!$isMobile.value || mobileViewMode == 'list'">
      <div class="search-info flex">
        <UPreloader mode="searchResults" :activation="!firstExtended" :width="50">
          <div class="search-results-info flex">
            <span>{{ $format['number'](searchResults?.value?.search?.total) }} properties found</span>
            <UButton class="ui-btn-text-gray hide-mobile" @click="resetParam('all')">Reset</UButton>
          </div>
        </UPreloader>
        <div class="search-results-options flex">
          <div class="search-sort-options flex">
            <span class="hide-mobile">Sort By:</span>
            <USelectDrop mHeader="Sort By" :label="sortMode.label" :options="sortModes" v-model="sortMode" @update:modelValue="refresh()">
              <template v-slot:content="{ props, select }">
                <div class="radio-select">
                  <URadioChip v-model="sortType" name="sort-mode-asc" value="asc">Ascending</URadioChip>
                  <URadioChip v-model="sortType" name="sort-mode-desc" value="desc">Descending</URadioChip>
                </div>
                <div class="option flex" v-for="o of sortModes" :key="o" :class="{ active: o == sortMode }" @click="select(o), props.close()">
                  <UIcon name="bold-arrow" :class="sortType"/>
                  {{ o.label }}
                </div>
              </template>
            </USelectDrop>
          </div>
          <div class="search-results-viewmode flex">
            <UButton class="ui-btn-text-gray" @click="viewMode = 'list'"><UIcon :class="{ active: viewMode == 'list' }" name="list" /></UButton>
            <UButton class="ui-btn-text-gray" @click="viewMode = 'grid'"><UIcon :class="{ active: viewMode == 'grid' }" name="grid" /></UButton>
          </div>
        </div>
      </div>
      <UDivider/>
      <div class="container" :class="['container-' + viewMode]">
        <div class="no-results" v-show="searchResults?.value?.search?.items?.length != undefined && searchResults?.value?.search.items.length < 1">
          <div class="square">
            <UIcon name="no-results-color" />
          </div>
          <span class="headline">No results found.</span>
          <span class="description">Adjust the filters or expand your search to see results</span>
        </div>
        <template v-for="p of searchResults?.value?.search.items || 20" :key="p">
          <UPreloader mode="propertyCard" :activation="!firstExtended">
            <Property--Card :valueMode="customization.values.priceMode" :mode="viewMode == 'grid' ? 'card' : 'line'" :property="p" :financialProps="financialData"/>
          </UPreloader>
          <UDivider/>
        </template>
      </div>
      <UPagination v-if="searchResults?.value?.search" v-show="searchResults?.value?.search?.items?.length != undefined && searchResults?.value?.search.items.length > 0" v-model="pagination" :dataCount="searchResults?.value?.search.total" :chunkSize="20" ref="paginator"/>
    </div>
    <div class="map" :class="{ mobileActive: $isMobile.value && mobileViewMode == 'map' }">

      <GoogleMap
        class="google-map"
        :api-key="GAPI_KEY"
        :center="{ lat: 39.5, lng: -98.35 }"
        :zoom="3"
        :mapTypeControl="true"
        :mapTypeControlOptions="{
          style: $isMobile.value ? 2 : 1
        }"
        :streetViewControl="true"
        streetViewControlPosition="LEFT_BOTTOM"
        :fullscreenControl="false"
        :zoomControl="true"
        :minZoom="4"
        :zoomControlPosition="$isMobile.value ? 'BOTTOM_RIGHT' : 'TOP_RIGHT'"
        gestureHandling="greedy"
        @dragend="onMapDragEnd"
        @zoom_changed="onMapZoomChange"
        ref="mapRef"
      >
        <CustomControl position="TOP_RIGHT">
          <div class="flex drawing-btn-container">
            <UButton class="ui-btn ui-btn-white flex drawing-btn" @click.stop="toggleDrawingMode('clear')" v-show="searchRegions.length > 0 && !drawMode"><UIcon name="cross" /> Clear the map</UButton>
            <UButton class="ui-btn ui-btn-green flex drawing-btn" @click.stop="toggleDrawingMode('draw')" v-show="searchRegions.length == 0 && !drawMode"><UIcon name="pencil-drawing" />Draw on the map</UButton>
            <UButton class="ui-btn ui-btn-green flex drawing-btn" @click.stop="toggleDrawingMode('enddraw')" v-show="drawMode"><UIcon name="checked" />Apply areas</UButton>
            <UButton class="ui-btn ui-btn-white flex drawing-btn" @click.stop="toggleDrawingMode('cancel')" v-show="drawMode">Cancel</UButton>
          </div>
        </CustomControl>
        <InfoWindowWrapper ref="mapInfoWindow" />

        <Polygon :options="poly" v-for="poly of searchRegions" :key="poly" />
        
        <Marker v-for="marker of mapMarkers" :key="marker" :options="marker" @click="marker.__onclick()" />

      </GoogleMap>
      <UDrop v-if="$isMobile.value" :mHeader="mapInfoWindowMobileHeader" ref="mapInfoWindowMobileDrop" label="test">
        <template v-slot:content>
          <InfoWindowWrapper ref="mapInfoWindowMobile" dontRemove />
        </template>
      </UDrop>
    </div>
    <div class="mobileViewModeToggle flex" v-if="$isMobile.value">
      <UButton class="ui-btn ui-btn-blue flex" @click="toggleMobileViewMode">
        <UIcon name="list-with-checkboxes" v-show="mobileViewMode == 'map'" />
        <UIcon name="map-with-marker" v-show="mobileViewMode != 'map'" />
        {{ mobileViewMode == 'map' ? 'List' : 'Map' }}
      </UButton>
    </div>
  </div>
  <Footer />
</div>
<UPopup ref="customizationPopup" class="popup-customization">
  <div class="content">
    <div class="header ui-grid-triple-spread">
      <div>
        <UButton class="ui-btn-text-gray" @click="resetParam('all')">Reset</UButton>
      </div>
      <div>
        <span class="title ui-text-boldest">More Parameters</span>
      </div>
      <div>
        <UIcon name="cross" @click="$refs.customizationPopup.close()"/>
      </div>
    </div>
    <div class="filters padded">
      <UCollapsible class="financing-collapsible" label="Financing" opened>
        <div class="collapsible-pad collapsible-pad-nm">
          <div><URadio value="cash" name="payment_type_popup" v-model="customization.values.priceMode">Cash</URadio></div>
          <div class="rich-radio">
            <URadio value="mortgage" name="payment_type_popup" v-model="customization.values.priceMode">
              <span class="flex">
                <span class="label">Mortgage</span>
                <span class="ui-href" @click="$refs['customsPopupFinancingDrop'].open()">Edit</span>
              </span>
            </URadio>
            <span class="desc">Downpayment: {{ $format['%Int'](customization.values.down_payment.value) }} | Interest: {{ $format['%'](customization.values.interest_rate) }} | Terms: {{ customization.values.loan_type.value }} yrs</span>
          </div>
          <UDrop ref="customsPopupFinancingDrop" mHeader="Financing">
            <template v-slot:label></template>
            <template v-slot:content="{ props }">
              <UDropAdjustment @apply="customization.values.priceMode = 'mortgage', props.close()" @reset="resetParam(['down_payment', 'loan_type'])">
                <span class="label">Downpayment (%)</span>
                <USelect v-model="customization.values.down_payment" :options="down_payment_types" label-by="label" close-on-select :maxHeight="$isMobile.value ? 120 : 300"/>
                <span class="label">Loan Type</span>
                <USelect v-model="customization.values.loan_type" :options="loan_types" label-by="label" close-on-select :maxHeight="$isMobile.value ? 100 : 300"/>
                <span class="label">Interest (%)</span>
                <span class="interest-rate">{{ $format['%'](customization.values.interest_rate) }}</span>
              </UDropAdjustment>
            </template>
          </UDrop>
        </div>
      </UCollapsible>
      <UCollapsible class="opprotunity-type-collapsible" label="Opportunity Type" opened>
        <div class="checkbox-list">
          <UCheckboxInput v-model="customization.values.is_rehab">Rehab Opportunity</UCheckboxInput>
          <UCheckboxInput v-model="customization.values.is_good_deal">Good Deal</UCheckboxInput>
          <UCheckboxInput v-model="customization.values.is_55_plus">55+ Community</UCheckboxInput>
          <UCheckboxInput v-model="customization.values.is_cash_only">Cash Only</UCheckboxInput>
          <UDivider />
          <UCheckboxInput v-model="customization.values.hide_is_rehab">Exclude Rehab</UCheckboxInput>
          <UCheckboxInput v-model="customization.values.hide_is_55_plus">Exclude 55+ Community</UCheckboxInput>
          <UCheckboxInput v-model="customization.values.hide_is_cash_only">Exclude Cash Only</UCheckboxInput>
        </div>
      </UCollapsible>
      <UCollapsible label="Price" opened>
        <div class="collapsible-pad">
          <USlider v-model="customization.values.price" :min="customization.defaults.price[0]" :max="customization.defaults.price[1]" :step="1000" :tooltips="false" />
          <div class="flex input-to-input">
            <UTextInput vertical v-model="customization.values.price[0]" :debounce="1000" prepend="Min Price" prefix="$" type="number" :step="1000" :min="customization.defaults.price[0]" :max="customization.defaults.price[1]" :formatter="$format['usdInt']" />
            <span>To</span>
            <UTextInput vertical v-model="customization.values.price[1]" :replacers="[undefined, $format['usdInt'](customization.defaults.price[1]) + '+']" :debounce="1000" prepend="Max Price" prefix="$" type="number" :step="1000" :min="customization.defaults.price[0]" :max="customization.defaults.price[1]" :formatter="$format['usdInt']" />
          </div>
        </div>
      </UCollapsible>
      <UCollapsible class="property-type-collapsible" label="Property Type" opened>
        <div class="flex collapsible-pad">
          <UCheckboxChip v-model="customization.values.property_type" name="property-type-popup" value="house-duplex"><UIcon name="house" />Single Family</UCheckboxChip>
          <UCheckboxChip v-model="customization.values.property_type" name="property-type-popup" value="condo-apt"><UIcon name="house-condo" />Condo &amp; Apts.</UCheckboxChip>
        </div>
      </UCollapsible>
      <UCollapsible label="Cash on Cash" opened>
        <div class="collapsible-pad">
          <USlider v-model="customization.values.coc_rate" @mousedown="!Account.Restrictions.canUseCustomization() && props.close()" v-bind="DataModel['slider__coc_return']" />
          <UTextInput v-model="customization.values.coc_rate" v-bind="DataModel['coc_return']" :debounce="1000" :formatter="$format['%Int']" subtype="percent" validationMessageShow keepSpace></UTextInput>
        </div>
      </UCollapsible>
      <UCollapsible label="Cap Rate" opened>
        <div class="collapsible-pad">
          <USlider v-model="customization.values.cap_rate" @mousedown="!Account.Restrictions.canUseCustomization() && props.close()" v-bind="DataModel['slider__cap_rate']" />
          <UTextInput v-model="customization.values.cap_rate" v-bind="DataModel['cap_rate']" :debounce="1000" :formatter="$format['%Int']" subtype="percent" validationMessageShow keepSpace></UTextInput>
        </div>
      </UCollapsible>
      <UCollapsible label="Est. Rent" opened>
        <div class="collapsible-pad">
          <USlider v-model="customization.values.predicted_rent_min" @mousedown="!Account.Restrictions.canUseCustomization() && props.close()" v-bind="{ ...DataModel['cash_flow'], ...DataModel['slider__cash_flow']}" />
          <UTextInput v-model="customization.values.predicted_rent_min" v-bind="DataModel['cash_flow']" :debounce="1000" :formatter="$format['usdInt']" validationMessageShow keepSpace></UTextInput>
        </div>
      </UCollapsible>
      <UCollapsible class="property-beds-collapsible" label="Beds" opened>
        <div class="flex input-to-input collapsible-pad">
          <UIncremental v-model="customization.values.beds[0]" v-bind="DataModel['beds']" label="Min"/>
          <span>To</span>
          <UIncremental v-model="customization.values.beds[1]" v-bind="DataModel['beds']" label="Max"/>
        </div>
      </UCollapsible>
      <UCollapsible label="Baths" opened>
        <div class="collapsible-pad">
          <UIncremental v-model="customization.values.baths" v-bind="DataModel['baths']" />
        </div>
      </UCollapsible>
      <UCollapsible label="Year Built" opened>
        <div class="collapsible-pad">
          <USlider v-model="customization.values.years" :min="customization.defaults.years[0]" :max="customization.defaults.years[1]" :step="1" :tooltips="false" />
          <div class="flex input-to-input">
            <UTextInput vertical v-model="customization.values.years[0]" :debounce="1000" prepend="Min" type="number" :step="1" :min="customization.defaults.years[0]" :max="customization.defaults.years[1]"/>
            <span>To</span>
            <UTextInput vertical v-model="customization.values.years[1]" :debounce="1000" prepend="Max" type="number" :step="1" :min="customization.defaults.years[0]" :max="customization.defaults.years[1]"/>
          </div>
        </div>
      </UCollapsible>
      <UCollapsible label="Living Area Size" opened>
        <div class="collapsible-pad">
          <USlider v-model="customization.values.buildingSize" :min="customization.defaults.buildingSize[0]" :max="customization.defaults.buildingSize[1]" :step="1" :tooltips="false" />
          <div class="flex input-to-input">
            <UTextInput vertical v-model="customization.values.buildingSize[0]" :debounce="1000" prepend="Min" type="number" :step="1" :min="customization.defaults.buildingSize[0]" :max="customization.defaults.buildingSize[1]" :formatter="$format['number']"/>
            <span>To</span>
            <UTextInput vertical v-model="customization.values.buildingSize[1]" :replacers="[undefined, $format['number'](customization.defaults.buildingSize[1]) + '+']" :debounce="1000" prepend="Max" type="number" :step="1" :min="customization.defaults.buildingSize[0]" :max="customization.defaults.buildingSize[1]" :formatter="$format['number']"/>
          </div>
        </div>
      </UCollapsible>
      <UCollapsible label="Property Status" opened>
        <div class="checkbox-list">
          <UCheckboxInput v-model="customization.values.status_for_sale">For Sale</UCheckboxInput>
          <UCheckboxInput v-model="customization.values.status_pending">Pending</UCheckboxInput>
          <UCheckboxInput v-model="customization.values.status_sold">Sold</UCheckboxInput>
        </div>
      </UCollapsible>
    </div>
    <div class="footer flex">
      <UButton class="ui-btn ui-btn-green" @click="() => { refresh(); $refs.customizationPopup.close() }">Apply</UButton>
    </div>
  </div>
</UPopup>
</template>

<style lang="less" scoped>
@sh: 55px;

.ui-radio {
  padding: 0;

  &::v-deep {
    span:before { left: 0; }
    span:after { left: 6px; }
  }
}
.ui-drop-adjustment {
  min-width: 300px;
  padding: 20px;

  .label { margin-bottom: 10px; }
  .ui-input, .vue-select { margin-bottom: 20px; }
  .vue-select { width: 100%; }
}
.input-to-input {
  justify-content: space-between;
  align-items: center;

  .ui-input::v-deep .prepend {
    font-size: .75rem;
  }
  span {
    font-size: .65rem;
    color: @col-text-gray-dark;
    text-transform: uppercase;
    padding: 0 8px;
    user-select: none;
  }
}
.search-header {
  position: fixed;
  top: @header-height;
  left: 0;
  width: 100%;
  height: @sh;
  background: @col-bg;
  box-shadow: @shadow @col-shadow;
  z-index: 2;
  padding-top: 7px;
  padding-bottom: 8px;
  justify-content: flex-start;
  align-items: center;
  align-content: center;

  @media @mobile {
    position: static;
    box-shadow: none;
    overflow-x: auto;
    padding-left: 0;
    padding-right: 0;
  }

  > div { flex-shrink: 0; }
  span.modified {
    @s: 8px;

    width: @s;
    height: @s;
    border-radius: 50%;
    background: @col-blue;
    margin-right: 8px;
  }
  > .cash-type {
    margin-right: 20px;

    > .ui-radio { margin-right: 15px; }
    .ui-drop::v-deep {
      .udrop-label { font-size: 0.875rem; }
      .udrop-label-selected { font-weight: 700; }
      .ui-drop-label {
        box-shadow: none;
        padding: 0;
        background: transparent;
      }
    }
    .interest-rate { font-weight: 600; }
  }
  > .filters {
    .ui-drop + .ui-drop,
    .ui-drop + .ui-btn,
    .ui-btn + .ui-btn { margin-left: 10px; }
    .ui-btn {
      justify-content: flex-start;
      align-items: center;
      align-content: center;

      @media @mobile {
        height: 30px;
        border-radius: 15px;
      }
      .svg-icon {
        @s: 20px;

        width: @s;
        height: @s;
        margin-right: 8 px;
      }
    }
    .ui-drop {
      .ui-slider {
        margin-left: auto;
        margin-right: auto;
        width: calc(100% - 24px);
      }
    }
    .cap-coc-drop .label { font-weight: 700; }
    .filters-button {
      &.applied {
        background: @col-blue;
        color: @col-text-light;
      }
      span.filters-text { margin: 0 5px; }
      .ui-counter {
        margin-left: 5px;
        background: @col-bg;
        color: @col-blue;
      }
      @media @mobile { padding: 0 12px; }
    }
  }
  > .chip-list {
    flex: 1 1;
    margin-left: 20px;
    white-space: nowrap;
    justify-content: flex-start;
    align-items: center;
    position: relative;
    overflow: hidden;

    @media @mobile { margin-left: 5px; }
  }
}
.search-results {
  @minh: calc(100*var(--vh) - @header-height - @sh);

  padding-top: @sh;
  min-height: @minh;
  position: relative;
  justify-content: flex-start;
  align-content: flex-start;
  align-items: flex-start;

  @media @mobile {
    padding-top: 0;
    display: block;
  }

  > .list {
    background: @col-bg;
    box-shadow: @shadow @col-shadow;
    min-height: @minh;
    width: 50vw;
    max-width: 680px;
    z-index: 1;

    @media @mobile {
      width: 100%;
      max-width: none;
      box-shadow: none;
      padding: 0;
    }

    .search-info {
      justify-content: space-between;
      align-items: center;
      align-content: center;
      padding-top: 20px;

      @media @mobile { padding: 0 @mm; }
      .search-results-info {
        justify-content: flex-start;
        align-items: center;
        align-content: center;

        span, .ui-button { font-size: .9375rem; }
        .ui-button {
          margin-left: 15px;
          padding: 0;
        }
      }
      .search-sort-options {
        font-size: .9375rem;
        justify-content: flex-end;
        align-items: center;
        color: @col-text-gray-darker;
        
        span { margin-right: 5px; }
        &::v-deep {
          .ui-drop-container {
            min-width: 240px;
            padding: 12px 20px;
            z-index: 10;

            > .scroll-container {
              .radio-select {
                border-bottom: 1px solid @col-gray-light;

                > .ui-radio-chip {
                  width: 50%;
                  font-size: 0.9375rem;
                  font-weight: 700;
                  background: transparent;
                  box-shadow: none;
                  color: @col-text-dark;
                  padding: 0 10px 35px;
                  margin: 0;
                  border-radius: 0;

                  &.selected { border-bottom: 2px solid @col-text-dark; }
  
                }
                @media @mobile {
                  padding-top: 10px;

                  > .ui-radio-chip {
                    font-size: 1.1rem;
                    padding: 0 0 40px;
                  }
                }
              }
              > .option {
                padding: 0;
                justify-content: flex-start;
                align-items: center;
                white-space: nowrap;
                color: @col-text-dark;
                cursor: pointer;
                font-size: .9375rem;

                &.active {
                  font-weight: 700;
                  color: @col-blue;
                }
                &:hover { background: transparent; }
                .svg-icon {
                  @s: 15px;

                  width: @s;
                  height: @s;
                  margin-right: 12px;

                  &.desc { transform: rotate(180deg); }
                }
              }
            }
          }
          .ui-drop-label {
            box-shadow: none;
            padding: 0;
            font-weight: 700;
            color: @col-text-dark;
            background: transparent;
          }
        }
      }
      .search-results-viewmode {
        justify-content: flex-end;
        align-items: center;
        margin-left: 15px;

        .svg-icon {
          @s: 1.5rem;

          width: @s;
          height: @s;

          &.active { fill: @col-text-dark; }
        }
        .ui-button { padding: 0; }
        .ui-button + .ui-button { margin-left: 10px; }
      }
    }
    > .ui-divider {
      margin: 20px auto;

      @media @mobile { width: calc(100% - 2*@mm); }
    }
    .container {
      .no-results {
        margin-bottom: 20px;

        .square {
          @s: 45%;

          width: @s;
          height: 0;
          position: relative;
          padding-bottom: @s;
          margin: 0 auto;

          .svg-icon {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
          }
        }
        .svg-icon, .headline, .description { display: block; }
        .headline, .description {
          color: @col-text-gray-darker;
          text-align: center;
          line-height: 1.25rem;
        }
        .headline {
          font-weight: 700;
          font-size: 1.125rem;
          margin-bottom: 1rem;
        }
      }
      &.container-grid {
        display: grid;
        gap: 20px;
        grid-template-rows: 1fr;
        grid-template-columns: 1fr 1fr;

        @media @mobile {
          grid-template-columns: 1fr;
          gap: 0;
        }
        @media @desktop {
          .ui-divider { display: none; }
        }
      }
    }
    .ui-pagination {
      margin: 40px auto;

      @media @mobile { margin: 0 auto @mm; }
    }
  }
  .map {
    position: sticky;
    top: @header-height + @sh;
    height: @minh;
    width: 50vw;
    flex: 1;

    @media @mobile {
      position: absolute;
      top: 0;
      left: 0;
      visibility: hidden;
      opacity: 0;
      width: 100%;
      height: calc(100*var(--vh) - @sh - @header-height-mobile);

      &.mobileActive {
        position: static;
        visibility: visible;
        opacity: 1;

        + .mobileViewModeToggle {
          margin-bottom: 0;
          padding-bottom: @mm;
        }
      }
    }
    > .google-map {
      position: absolute;
      top: 0;
      left: 0;
      height: 100%;
      width: 100%;

      &::v-deep > div {
        width: 100%;
        height: 100%;

        .gm-style-iw.gm-style-iw-c {
          padding-top: 30px;

          > button {
            @p: 2px;

            top: @p !important;
            right: @p !important;

            > img {
              @s: 26px;

              width: @s !important;
              height: @s !important;
              margin: 0 !important;
            }
          }
        }
        .gm-style .gm-style-iw-t::after { top: -2px; }
        .ofrc-map-marker-group, .ofrc-map-marker-property, .ofrc-map-marker-cluster {
          font-feature-settings: 'pnum' on, 'lnum' on;
        }
        .ofrc-map-marker-cluster {
          @s: 32px;

          width: @s;
          min-width: @s;
          height: @s;
          min-height: @s;
          line-height: @s;
          text-align: center;
          border-radius: 50%;
          background-color: @col-blue;
          color: @col-text-light;
          box-shadow: 0 0 0 5px rgba(100, 84, 195, 0.2);
        }
        .ofrc-map-marker-group, .ofrc-map-marker-property {
          padding: 5px 10px;
          border-radius: @border-radius;
          background-color: @col-blue;
          color: @col-text-light;
          box-shadow: 0 0 0 3px rgba(100, 84, 195, 0.2);
        }
        .ofrc-map-marker-property {
          padding: 5px 7px;
          box-shadow: none;
        }
        .drawing-btn-container {
          margin-top: 10px;

          @media @mobile { margin-right: 10px; }

          .drawing-btn {
            margin-left: 10px;
            justify-content: flex-start;
            align-items: center;
            align-content: center;
            font-weight: 500;
            font-size: 14px;
            padding: 7px 10px;

            .svg-icon {
              @s: 18px;

              width: @s;
              height: @s;
              margin-right: 10px;
            }
          }
        }
      }
    }
    &::v-deep .ui-drop-label { display: none }
  }
  .mobileViewModeToggle {
    position: sticky;
    bottom: @mm;
    padding-bottom: @mm;
    justify-content: center;
    align-items: center;

    > .ui-btn {
      justify-content: center;
      align-content: center;
      align-items: center;
      background: @col-text-dark;

      .svg-icon {
        @s: 24px;

        width: @s;
        height: @s;
        margin-right: 5px;
      }
    }
  }
}
.popup-customization {
  > .content {
    @rh: 50px;
  
    width: 100%;
    max-width: 555px;

    @media @mobile { border-radius: 0 }

    > .header {
      justify-content: center;
      align-items: center;
      white-space: nowrap;
      padding: 15px 20px;
      border-bottom: 1px solid @col-gray;
      height: @rh;

      .svg-icon--cross {
        @s: 1rem;

        width: 1rem;
        height: 1rem;
        cursor: pointer;
        fill: @col-text-gray-darker;
      }
    }
    > .footer {
      border-top: 1px solid @col-gray;
      justify-content: center;
      align-items: center;
      padding: 0 20px;
      height: @rh + 10px;

      .ui-btn {
        height: 40px;
        width: 40%;
        max-width: 20rem;
      }
    }
    .filters {
      max-height: calc(100*var(--vh) - 4*@rh);
      overflow-y: auto;
      padding-left: 60px;
      padding-right: 60px;

      @media @mobile {
        max-height: calc(100*var(--vh) - 2*@rh - 10px);
        padding-left: @mm/2;
        padding-right: @mm/2;
      }
      .ui-collapsible {
        & + .ui-collapsible { border-top: 1px solid @col-gray; }
        .collapsible-pad {
          padding: 10px 0 20px;

          @media @mobile { padding: 24px @mm/2 @mm + 5px; }
          &.collapsible-pad-nm {
            margin-top: -15px;

            @media @mobile { margin-top: -24px; }
          }
        }
        .checkbox-list {

          @media @mobile { padding: 0 @mm/2; }

          .ui-checkbox {
            padding: 0;
            display: block;

            &::v-deep label.flex > span:before,
            &::v-deep label.flex > span:after { left: 0; }
          }
        }
        &::v-deep > .header .flex {
          height: 50px;
          padding-block: 10px;

          @media @mobile { padding: 0 @mm/2; }
        }
        &::v-deep > .header .flex .svg-icon--smooth-arrow {
          @s: 14px;

          width: @s;
          height: @s;
        }
        .ui-slider { margin-bottom: 30px; }
      }
      .financing-collapsible {
        .ui-drop { z-index: 2; }
        .ui-drop::v-deep {
          .ui-drop-label { display: none; }
          .interest-rate { font-weight: 600; }
          .ui-drop-container {
            top: 30px;

            @media @mobile { top: auto; }
          }
        }
        .rich-radio {
          span.flex {
            align-items: center;
            justify-content: flex-start;

            span.ui-href {
              margin-left: 15px;
              font-weight: 700;
              color: @col-text-gray-dark;
            }
          }
        }
        span.desc {
          display: block;
          padding-left: 36px;
          font-size: .875rem;
          color: @col-text-gray-darker;
        }
      }
      .opprotunity-type-collapsible {
        .ui-divider { margin: 5px 0; }
      }
      .property-type-collapsible {
        .collapsible-pad {

          @media @mobile { margin-top: -20px; }
          .ui-checkbox-chip {
            flex: 1;
            height: auto;
            background: transparent;
            border-radius: @border-radius;
            color: @col-text-dark;

            &.selected { color: @col-blue; }
            .svg-icon {
              @s: 30px;

              display: block;
              margin: 10px auto 5px;
              width: @s;
              height: @s;
            }
          }
        }
      }
      @media @desktop {
        .ui-collapsible.opened::v-deep > .container { overflow: visible; }
      }
    }
  }
}
</style>

<style>@import '~swiper/components/navigation/navigation.min.css';</style>

<script lang="ts">
// @ts-nocheck
// FIX FOR VUE LINTER BUGS WTF?!

import { defineComponent, readonly, ref, toRaw, watch } from 'vue';

import URadio from '@/components/ui/URadioInput.vue';
import UCheckboxChip from '@/components/ui/UCheckboxChip.vue';
import URadioChip from '@/components/ui/URadioChip.vue';
import UCheckboxInput from '@/components/ui/UCheckboxInput.vue';
import UIncremental from '@/components/ui/UIncremental.vue';
import UButton from '@/components/ui/UButton.vue';
import USelect from '@/components/ui/USelect.vue';
import USelectDrop from '@/components/ui/USelectDrop.vue';
import UPagination from '@/components/ui/UPagination.vue';
import UDivider from '@/components/ui/UDivider.vue';
import UDrop from '@/components/ui/UDrop.vue';
import UCollapsible from '@/components/ui/UCollapsible.vue';
import UPopup from '@/components/ui/UPopup.vue';
import UDropAdjustment from '@/components/ui/UDropAdjustment.vue';
import USlider from '@/components/ui/USlider.vue';
import UTextInput from '@/components/ui/UTextInput.vue';
import Footer from '@/components/static/footer.vue';
import Property__Card from '@/components/Property/Card.vue';
import InfoWindowWrapper from '@/components/Property/InfoWindowWrapper.vue';
import DiffChips from '@/components/Search/DiffChips.vue'
import UPreloader from '@/components/ui/UPreloader.vue';

import { GoogleMap, CustomControl, Polygon, Marker } from 'vue3-google-map';

import SearchModel, { HiddenSearchResult, SearchResult, TSearchRoute } from '@/models/Search';
import { TSearchRequest__Filters, TSearchRequest__Sort } from '@/models/Search/api';
import envModel from '@/models/env.model';
import { debounce } from 'ts-debounce';
import AccountStore from '@/models/Account';

import DataModel from '@/models/Property/finance/dataModel'

import SwiperCore, { Navigation } from 'swiper';
import { Swiper, SwiperSlide } from 'swiper/vue';

SwiperCore.use([ Navigation ]);


const SI_SYMBOL = ['', 'K', 'M', 'G', 'T', 'P', 'E'];

function abbreviateNumber(number){

    // what tier? (determines SI symbol)
    const tier = Math.log10(Math.abs(number)) / 3 | 0;

    // if zero, we don't need a suffix
    if (tier == 0) return number;

    // get suffix and determine scale
    const suffix = SI_SYMBOL[tier];
    const scale = Math.pow(10, tier * 3);

    // scale the number
    const scaled = number / scale;

    // format number and add suffix
    const fixed = scaled.toFixed(1);
    return (fixed[fixed.length - 1] == '0' ? scaled.toFixed(0) : fixed) + suffix;
}

const sortModes = [
  {
    label: 'Default',
    name: 'default_sort'
  },

  {
    label: 'Newest',
    name: 'list_date'
  },

  {
    label: 'Updated',
    name: 'update_date'
  },

  {
    label: 'Price',
    name: 'price'
  },

  {
    label: 'Estimated Rent',
    name: 'predicted_rent'
  },

  {
    label: 'Year Built',
    name: 'year_built'
  },

  {
    label: 'Cap Rate',
    name: 'cap_rate'
  },

  {
    label: 'Cash on Cash',
    name: 'cash_on_cash'
  },
  {
    label: 'Total Return',
    name: 'total_return'
  },
];

const loan_types = [
  { label: '15 years', value: 15 },
  { label: '30 years', value: 30 },
];
const down_payment_types = [
  { label: '20%', value: 0.2 },
  { label: '30%', value: 0.3 },
  { label: '40%', value: 0.4 },
  { label: '50%', value: 0.5 },
];

type TCustomParams = {
  priceMode: 'cash' | 'mortgage',
  price: [number, number],
  down_payment: number,
  loan_type: { label: string, value: number },
  interest_rate: number,
  cap_rate: number,
  coc_rate: number,
  monthly_rent: number,
  property_type: Array<string>,
  predicted_rent_min: number,
  beds: [number, number],
  baths: number,
  years: [number, number],
  buildingSize: [number, number],
  status_for_sale: boolean,
  status_pending: boolean,
  status_sold: boolean,
  is_55_plus: boolean,
  is_rehab: boolean,
  is_cash_only: boolean,
  is_good_deal: boolean,
  hide_is_55_plus: boolean,
  hide_is_rehab: boolean,
  hide_is_cash_only: boolean

  [key:string]: any
}

const rok2020 = 1606690800000;

function createPolygon(paths:any, __isCustom: boolean = false) {

  if (__isCustom) {
    const ps = paths.getArray();
    if (ps[0].lng() != ps[ps.length - 1].lng() || ps[0].lat() != ps[ps.length - 1].lat())
      ps.push(ps[0]);
  }

  return {
    paths,
    strokeColor: '#01D092',
    strokeOpacity: 1,
    strokeWeight: 2,
    fillColor: '#01D092',
    fillOpacity: 0.05,
    __isCustom,
    __creationTime: Math.round( (Date.now() - rok2020) * (Math.random() * 100) )
  }
}

export default defineComponent({
  components: {
    URadio,
    URadioChip,
    UCheckboxChip,
    DiffChips,
    UIncremental,
    UButton,
    USelect,
    USelectDrop,
    UPagination,
    UDivider,
    UDrop,
    UDropAdjustment,
    UCheckboxInput,
    UCollapsible,
    UPopup,
    USlider,
    UTextInput,
    UPreloader,
    Footer,
    'Property--Card': Property__Card,
    GoogleMap,
    CustomControl,
    InfoWindowWrapper,
    Polygon,
    Marker,
    Swiper,
    SwiperSlide
  },
  computed: {
    Account() {
      return AccountStore;
    },
    searchResults() {
      return SearchModel.searchResults;
    },
    customizationDiff() {
      let diffs = [];

      // @ts-ignore Vue TS support bug
      for (let k in this.customization.defaults)
        // @ts-ignore Vue TS support bug
        if (k != 'property_type' && JSON.stringify(this.customization.defaults[k]) != JSON.stringify(this.customization.values[k]))
          diffs.push(k);
        else if (k == 'property_type') {
          if (![0, 2].includes(this.customization.values.property_type.length))
            diffs.push(k)
        }

      return diffs;
    },
    GAPI_KEY() {
      return envModel.VUE_APP_API_GOOGLE_MAP_TOKEN;
    },
    DataModel() {
      return DataModel;
    },
    financialData() {
      return {
        priceMode: this.customization.values.priceMode,
        down_payment: this.customization.values.down_payment.value,
        loan_type: this.customization.values.loan_type.value,
        interest_rate: this.customization.values.interest_rate
      }
    }
  },
  data() {
    let data = {
      viewMode: 'list',

      customization: {
        defaults: {
          priceMode: 'cash',
          price: [10000, 1000000],
          down_payment: readonly(down_payment_types[0]),
          loan_type: readonly(loan_types[1]),
          interest_rate: 0.033,
          cap_rate: 0,
          coc_rate: 0,
          monthly_rent: 1500,
          property_type: [],
          predicted_rent_min: 0,
          beds: [0, 10],
          baths: 0,
          years: [1800, 2021],
          buildingSize: [0, 10000],
          status_for_sale: true,
          status_pending: false,
          status_sold: false,
          is_55_plus: false,
          is_rehab: false,
          is_cash_only: false,
          is_good_deal: false,
          hide_is_55_plus: false,
          hide_is_rehab: false,
          hide_is_cash_only: false
        } as TCustomParams,
        values: {} as TCustomParams
      },
      customizationDiffChips: [] as any,

      sortType: 'desc',
      sortModes,
      sortMode: sortModes[0],
      sortModeDefault: sortModes[0],
      loan_types: loan_types,
      down_payment_types: down_payment_types,

      pagination: [0, 10],
      mapMarkers: [] as Array<any>,
      mapExtendQueued: 0,
      requestLock: false,
      mapRequestLock: false,
      mapInfoWindow: null as any,
      mobileViewMode: 'list',
      firstExtended: false,

      searchRegions: [] as any,
      drawMode: false,

      mapZoom: undefined,
      viewport: undefined,
      mapInfoWindowMobileHeader: 'Property'
    };

    data.customization.values = JSON.parse(JSON.stringify(data.customization.defaults));
    data.customization.values.loan_type = loan_types[1];
    data.customization.values.down_payment = down_payment_types[0];

    return data;
  },
  watch: {
    mapZoom(newVal: any, oldVal: any) {
      if (this.firstExtended && oldVal != undefined) {
        this.searchRegions.length > 0 && this.searchRegions[0].__creationTime++;
        this.refresh(false, true);
      }
    },
    viewport(newVal: any, oldVal: any) {
      if (this.firstExtended && oldVal != undefined) {
        this.searchRegions.length > 0 && this.searchRegions[0].__creationTime++;
        this.refresh(false, true);
      }
    },
    '$route.params'(to:TSearchRoute, from:TSearchRoute) {
      if (this.$route.name != 'search')
        return;

      const diffs = [
        JSON.stringify(to.typeOptions) == JSON.stringify(from.typeOptions),
        JSON.stringify(to.options) == JSON.stringify(from.options)
      ];

      if (!diffs[0] && !JSON.stringify(to.typeOptions).includes('geo_rect'))
        this.firstExtended = false;

      const fromSearch = window.localStorage.getItem('ofirio-from-search');
      if (fromSearch) {
        this.searchRegions = [];
        this.firstExtended = false;
      }
      this.requestSearch(to, 0, diffs.includes(false));

      if (this.pagination[0] != 0) {
        this.requestLock = true;
        (<any>this.$refs).paginator.setPage(1);
      }
    },
    pagination(to: any, from: any) {
      if (to[0] == from[0])
        return;

      window.scrollTo(0,0);

      if (this.requestLock) {
        this.requestLock = false;
        return;
      }

      this.requestSearch(<TSearchRoute>this.$route.params, to[0], to[0] == 0);
    },
    'customization.values.priceMode'(to: string, from: string) {
      if (to != this.customization.defaults.priceMode) {
        if (AccountStore.Auth.inited && !AccountStore.Auth.isLoggedIn) {
          (<any>this.$root)['ev-popup-login-open']('register');
          setTimeout(() => { this.customization.values.priceMode = this.customization.defaults.priceMode; }, 0);
          return;
        }

        if (AccountStore.Auth.inited && AccountStore.Auth.isLoggedIn && AccountStore.Basis.dto && !AccountStore.Basis.isPremium) {
          (<any>this.$root).$refs.popupUpgrade.open();
          setTimeout(() => { this.customization.values.priceMode = this.customization.defaults.priceMode; }, 0);
          return;
        }

        if (AccountStore.Auth.inited && AccountStore.Auth.isLoggedIn && !AccountStore.Basis.dto.verified) {
          (<any>this.$root)['ev-popup-login-open']('email-validation');
          setTimeout(() => { this.customization.values.priceMode = this.customization.defaults.priceMode; }, 0);
          return;
        }
      }
      
      if (this.mapInfoWindow && this.mapInfoWindow.close)
        this.mapInfoWindow.close();

      if ((<any>this.$refs).mapInfoWindowMobileDrop && (<any>this.$refs).mapInfoWindowMobileDrop.close)
        (<any>this.$refs).mapInfoWindowMobileDrop.close();

      if (to == 'mortgage')
        this.recalcMortgage();
      else if (to == 'cash' && AccountStore.Basis.isPremium)
        this.resetParam(['down_payment', 'loan_type']);
    },
    'customization.values.beds': {
      handler: function (newVal: [number, number], oldVal: [number, number]) {
        if (newVal[0] > newVal[1])
          newVal[0] = newVal[1];
      },
      deep: true
    },
    'sortType'() {
      this.refresh(false);
    },
    'customization.values.hide_is_rehab'(to: boolean) {
      if (to)
        this.customization.values.is_rehab = false;
    },
    'customization.values.is_rehab'(to: boolean) {
      if (to)
        this.customization.values.hide_is_rehab = false;
    },
    'customization.values.hide_is_55_plus'(to: boolean) {
      if (to)
        this.customization.values.is_55_plus = false;
    },
    'customization.values.is_55_plus'(to: boolean) {
      if (to)
        this.customization.values.hide_is_55_plus = false;
    },
    'customization.values.hide_is_cash_only'(to: boolean) {
      if (to)
        this.customization.values.is_cash_only = false;
    },
    'customization.values.is_cash_only'(to: boolean) {
      if (to)
        this.customization.values.hide_is_cash_only = false;
    }
  },
  methods: {
    onMapDragEnd() {
      this.viewport = (<any>this.$refs.mapRef).map.getBounds().toUrlValue();
    },
    onMapZoomChange(force: boolean = false) {
      if (!this.firstExtended && !force)
        return;
      this.mapZoom = (<any>this.$refs.mapRef).map.getZoom();
    },
    async requestSearch(path: string, start: boolean = 0, mapToBeQueried: boolean = false) {
      const mapBlock = document.querySelector('.search-results .map >.google-map');

      SearchModel.findProperties(path, start, mapToBeQueried, { map: this.$refs.mapRef.map, searchRegions: this.searchRegions, noMapParams: !this.firstExtended, cssBoundary: mapBlock ? mapBlock.getBoundingClientRect() : undefined }).then(() => {
        if (this.customization.values.priceMode == 'mortgage')
          this.recalcMortgage();
      });

      this.setCustomizationFromUrlParams();
    },
    async refresh(forceUseRegion: boolean = false, mapChanged: boolean = false) {
      if ((this.sortMode.name == 'predicted_rent' || this.sortMode.name == 'cap_rate' || this.sortMode.name == 'cash_on_cash' || this.sortMode.name == 'total_return') && !AccountStore.Restrictions.canUseCustomization()) {
        this.sortMode = this.sortModes[0];
        return;
      }

      if (this.drawMode)
        return;

      let options = {
        prop_type2: this.customization.values.property_type.length > 1 || this.customization.values.property_type.length == 0 ? undefined : this.customization.values.property_type[0],
        beds_min: this.customization.values.beds[0],
        beds_max: this.customization.values.beds[1],
        baths_min: this.customization.values.baths,
        year_built_min: this.customization.values.years[0],
        year_built_max: this.customization.values.years[1],
        build_size_min: this.customization.defaults.buildingSize[0] == this.customization.values.buildingSize[0] ? undefined : this.customization.values.buildingSize[0],
        build_size_max: this.customization.defaults.buildingSize[1] == this.customization.values.buildingSize[1] ? undefined : this.customization.values.buildingSize[1],
        price_min: this.customization.defaults.price[0] == this.customization.values.price[0] ? undefined : this.customization.values.price[0],
        price_max: this.customization.defaults.price[1] == this.customization.values.price[1] ? undefined : this.customization.values.price[1],
        status_for_sale: this.customization.values.status_for_sale,
        status_pending: this.customization.values.status_pending,
        status_sold: this.customization.values.status_sold,
        is_55_plus: this.customization.values.is_55_plus,
        is_rehab: this.customization.values.is_rehab,
        is_cash_only: this.customization.values.is_cash_only,
        is_good_deal: this.customization.values.is_good_deal,

        hide_is_55_plus: this.customization.values.hide_is_55_plus,
        hide_is_rehab: this.customization.values.hide_is_rehab,
        hide_is_cash_only: this.customization.values.hide_is_cash_only,
        cash_on_cash_min: this.customization.values.coc_rate,
        cap_rate_min: this.customization.values.cap_rate,
        predicted_rent_min: Math.round(this.customization.values.predicted_rent_min),
      }

      if (this.customization.values.priceMode == 'mortgage') {
        options.financing_years = this.customization.values.loan_type.value;
        options.down_payment = this.customization.values.down_payment.value;
      }

      let params = {
        options: SearchModel.toUrl(options),
        sort: SearchModel.toUrl({
          sort_field: this.sortMode.name,
          sort_direction: this.sortType
        })
      };

      const defaultToGeoChangeIf = !this.mapRequestLock && this.firstExtended;
      const geoSearchNeeded = this.searchRegions.some((r:any) => r.__isCustom) || this.searchRegions.length == 0;
      
      if (defaultToGeoChangeIf && (forceUseRegion || geoSearchNeeded || this.$route.params.typeOptions.includes('geo_rect') )) {
        const mapRef = <any>this.$refs.mapRef;
        const geoRectValue = this.searchRegions.length > 0 ? this.searchRegions.reduce((pv: any, cv: any) => pv + cv.__creationTime, 0).toString().slice(-6) : mapRef.map.getBounds().toUrlValue();
        params.typeOptions = SearchModel.toUrl({ geo_rect: geoRectValue });
      }

      if (mapChanged && ( forceUseRegion || (!params.typeOptions || !params.typeOptions.includes('geo_rect')))) {
        this.requestSearch(<TSearchRoute>this.$route.params, 0, true);
        if (this.pagination[0] != 0) {
          this.requestLock = true;
          (<any>this.$refs).paginator.setPage(1);
        }

      }
      else {
        await this.$router.push({ name: 'search', params });
        this.customizationDiffChips = this.customizationDiff;
      }
    },
    async recalcMortgage() {
      const isDifferentFromDefaults = this.customizationDiff.includes('down_payment') || this.customizationDiff.includes('loan_type');

      if (!AccountStore.Basis.isPremium) {
        if (this.customizationDiff.includes('priceMode') || isDifferentFromDefaults) {
          this.resetParam(['priceMode', 'down_payment', 'loan_type'], 'norefresh');

          if (!AccountStore.Auth.isLoggedIn)
            return (<any>this.$root)['ev-popup-login-open']('register');
          else
            return (<any>this.$root).$refs.popupUpgrade.open();
        }
      }

      this.customization.values.priceMode = 'mortgage';

      if (this.mapInfoWindow && this.mapInfoWindow.close)
        this.mapInfoWindow.close();

      if ((<any>this.$refs).mapInfoWindowMobileDrop && (<any>this.$refs).mapInfoWindowMobileDrop.close)
        (<any>this.$refs).mapInfoWindowMobileDrop.close();

      this.refresh();
    },
    resetParam(param:string | Array<string>, refreshMode: string = 'refresh') {
      let anyChanged = false;
      const reset = (attr: string) => {
        if (attr == 'loan_type') {
          const index = loan_types.findIndex(e => e.value == this.customization.defaults.loan_type.value);
          this.customization.values.loan_type = loan_types[index];
        }
        else if (attr == 'down_payment') {
          const index = down_payment_types.findIndex(e => e.value == this.customization.defaults.down_payment.value);
          this.customization.values.down_payment = down_payment_types[index];
        }
        else
          this.customization.values[attr] = JSON.parse(JSON.stringify(this.customization.defaults[attr]));
        anyChanged = true;
      }

      if (param == 'all')
        param = Object.keys(this.customization.defaults);
      
      if (Array.isArray(param)) {
        for (let k of param)
          reset(k);
      } else
        reset(param);

      if ((anyChanged && refreshMode == 'refresh') || refreshMode == 'force')
        this.refresh();
    },
    setCustomizationFromUrlParams() {
      try {
        localStorage.setItem('ofirio-saved-after-login-url', JSON.stringify({ name: 'search', params: this.$route.params }));
      } catch (ex) {}

      if (this.$route.params.options) {
        const urlOptionParams = <Required<TSearchRequest__Filters>><any>SearchModel.toObject(<string>this.$route.params.options);
        const urlSortParams = <Required<TSearchRequest__Sort>><any>SearchModel.toObject(<string>this.$route.params.sort);

        if (urlOptionParams.prop_type2 != undefined)
          this.customization.values.property_type = [ urlOptionParams.prop_type2 ];
        this.customization.values.cap_rate = urlOptionParams.cap_rate_min;
        this.customization.values.coc_rate = urlOptionParams.cash_on_cash_min;
        this.customization.values.predicted_rent_min = urlOptionParams.predicted_rent_min;
        this.customization.values.beds[0] = urlOptionParams.beds_min;
        this.customization.values.beds[1] = urlOptionParams.beds_max;
        this.customization.values.baths = urlOptionParams.baths_min;
        this.customization.values.years[0] = urlOptionParams.year_built_min;
        this.customization.values.years[1] = urlOptionParams.year_built_max;
        this.customization.values.buildingSize[0] = urlOptionParams.build_size_min;
        this.customization.values.buildingSize[1] = urlOptionParams.build_size_max;
        this.customization.values.price[0] = urlOptionParams.price_min;
        this.customization.values.price[1] = urlOptionParams.price_max;
        this.customization.values.status_for_sale = urlOptionParams.status_for_sale;
        this.customization.values.status_pending = urlOptionParams.status_pending;
        this.customization.values.status_sold = urlOptionParams.status_sold;
        this.customization.values.is_55_plus = urlOptionParams.is_55_plus;
        this.customization.values.is_rehab = urlOptionParams.is_rehab;
        this.customization.values.is_cash_only = urlOptionParams.is_cash_only;
        this.customization.values.is_good_deal = urlOptionParams.is_good_deal;
        this.customization.values.hide_is_55_plus = urlOptionParams.hide_is_55_plus;
        this.customization.values.hide_is_rehab = urlOptionParams.hide_is_rehab;
        this.customization.values.hide_is_cash_only = urlOptionParams.hide_is_cash_only;

        for (let sm of this.sortModes)
          if (sm.name == urlSortParams.sort_field) {
            this.sortMode = sm;
            this.sortType = urlSortParams.sort_direction == 'desc' ? 'desc' : 'asc';
          }
      }
    },
    extentMapToMarkersTimer() {
      const localTime = Date.now();
      this.mapExtendQueued = localTime;
      
      const mapRef = <any>this.$refs.mapRef;

      if (mapRef?.ready)
        return this.processMapMarkers();
      
      let watchOnce = watch(() => mapRef?.ready, (status: boolean) => {
        if (status == true && this.mapExtendQueued == localTime) {
          this.processMapMarkers();
          watchOnce();
        }
      });
    },
    processMapMarkers() {

      if (this.drawMode)
        return;

      const mapRef = <any>this.$refs.mapRef;

      const searchResults = toRaw(this.searchResults.value);
      const boundRegion = new mapRef.api.LatLngBounds();

      if ((this.searchRegions.length == 0 || !this.$route.params.typeOptions.includes('geo_rect')) && searchResults?.geo_shape) {
        this.searchRegions = [];

        if (searchResults.geo_shape.boundary.type == 'MultiPolygon')
          for (let polygonCoords of searchResults.geo_shape.boundary.coordinates)
            this.searchRegions.push(createPolygon(polygonCoords[0].map(coord => {
              boundRegion.extend({lat: coord[1], lng: coord[0]});
              return {
                lat: coord[1],
                lng: coord[0]
              }
            })));
        else
          this.searchRegions.push(createPolygon(searchResults.geo_shape.boundary.coordinates[0].map(coord => {
            boundRegion.extend({lat: coord[1], lng: coord[0]});
            return {
              lat: coord[1],
              lng: coord[0]
            }
          })));
      }

      const markersArr = [];
      if (searchResults?.map?.features) {
        for (let marker of searchResults.map.features) {
          if (marker.type == 'Feature' && marker.properties.FeatureType == 'Cluster') {
            markersArr.push({
              optimized: true,
              position: {
                lat: marker.geometry.coordinates[1],
                lng: marker.geometry.coordinates[0],
              },
              icon: '/mapMarkerIcons/map-icon-transparent.svg',
              label: {
                className: 'ofrc-map-marker-cluster',
                text: marker.properties.count < 1000 ? marker.properties.count.toString() : abbreviateNumber(marker.properties.count),
                fontSize: '12',
                fontFamily: '\'Raleway\', Arial, sans-serif',
                fontWeight: '800',
                color: 'white'
              },
              __onclick: () => {
                mapRef.map.fitBounds({
                  east: marker.properties.geo_bounds[1],
                  north: marker.properties.geo_bounds[0],
                  south: marker.properties.geo_bounds[2],
                  west: marker.properties.geo_bounds[3]
                });
              }
            });
          } else if (marker.type == 'Feature' && marker.properties.prop_id != undefined) {
            markersArr.push({
              optimized: true,
              position: {
                lat: marker.geometry.coordinates[1],
                lng: marker.geometry.coordinates[0],
              },
              icon: '/mapMarkerIcons/map-icon-transparent.svg',
              label: {
                className: 'ofrc-map-marker-property',
                text: marker.properties.cap_rate ? this.$format['%'](marker.properties.cap_rate) : '$' + abbreviateNumber(marker.properties.price),
                fontSize: '12',
                fontFamily: '\'Raleway\', Arial, sans-serif',
                fontWeight: '800',
                color: 'white'
              },
              __onclick: () => {
                if (this.$isMobile.value) {
                  (<any>this.$refs).mapInfoWindowMobile.setProperties([Object.assign({}, marker.properties, { financialData: this.financialData })]);
                  (<any>this.$refs).mapInfoWindowMobileDrop.open();
                  this.mapInfoWindowMobileHeader = 'Property';
                } else {
                  (<any>this.$refs).mapInfoWindow.setProperties([Object.assign({}, marker.properties, { financialData: this.financialData })]);
                  this.mapInfoWindow.setPosition({
                    lat: marker.geometry.coordinates[1],
                    lng: marker.geometry.coordinates[0]
                  });
                  this.mapInfoWindow.open({ map: mapRef.map });
                }
              }
            });
          } else if (marker.type == 'FeatureCollection' && marker.features.length > 0) {
            markersArr.push({
              optimized: true,
              position: {
                lat: marker.features[0].geometry.coordinates[1],
                lng: marker.features[0].geometry.coordinates[0],
              },
              icon: '/mapMarkerIcons/map-icon-transparent.svg',
              label: {
                className: 'ofrc-map-marker-group',
                text: marker.features.length + ' listings',
                fontSize: '12',
                fontFamily: '\'Raleway\', Arial, sans-serif',
                fontWeight: '800',
                color: 'white'
              },
              __onclick: () => {
                const markers = marker.features.map((m:any) => Object.assign({}, m.properties, { financialData: this.financialData }));
                if (this.$isMobile.value) {
                  (<any>this.$refs).mapInfoWindowMobile.setProperties(markers);
                  (<any>this.$refs).mapInfoWindowMobileDrop.open();
                  this.mapInfoWindowMobileHeader = `${markers.length} Properties`;
                } else {
                  (<any>this.$refs).mapInfoWindow.setProperties(markers);
                  this.mapInfoWindow.setPosition({
                    lat: marker.features[0].geometry.coordinates[1],
                    lng: marker.features[0].geometry.coordinates[0]
                  });
                  this.mapInfoWindow.open({ map: mapRef.map });
                }
              }
            });
          }
        }
      }

      if (markersArr.length == 0 && !searchResults?.geo_shape) {
        if (!this.$route.params.typeOptions.includes('geo_rect')) {
          return SearchModel.getRectQuery((<any>this.$root).$refs.header.$refs.headerSearch.getCurrentSearchValue()).then((res) => {

            let typeOptions = SearchModel.toUrl(Object.assign({}, res == false ? { geo_rect: '24.9493,-125.0011,49.5904,-65.9326' } : res, { label: undefined, type: undefined }));
            const params = this.$route.name == 'search' ? { ...this.$route.params, typeOptions } : { typeOptions };
            window.localStorage.setItem('ofirio-from-search', 'true');
            this.mapRequestLock = false;
            this.$router.push({ name: 'search', params });
            
            if (res == false)
              (<any>this.$root).$refs.globMessages.push({ type: 'warning', message: 'We could not find this area. Please check your spelling or enter a valid ZIP code.' }, 8000);
          });
        } else {
          const parsedRect = <any>SearchModel.toObject(this.$route.params.typeOptions);
          const [lat1, lng1, lat2, lng2] = parsedRect.geo_rect.split(',').map((val: any) => parseFloat(val));
          boundRegion.extend({ lat: lat1, lng: lng1 });
          boundRegion.extend({ lat: lat2, lng: lng2 });
          this.mapRequestLock = true;
          mapRef.map.fitBounds(boundRegion);
          mapRef.api.event.addListenerOnce(mapRef.map, 'idle', () => {
            this.mapRequestLock = false;
            this.firstExtended = true;
          });
        }
      }

      const fromSearch = window.localStorage.getItem('ofirio-from-search');
      if (!this.firstExtended || fromSearch) {

        if (searchResults.geo_shape || markersArr.length > 0) {
          for (let m of markersArr)
            boundRegion.extend({ lat: m.position.lat, lng: m.position.lng });
          
          this.mapRequestLock = true;
          mapRef.map.fitBounds(boundRegion);
          mapRef.api.event.addListenerOnce(mapRef.map, 'idle', () => {
            this.mapRequestLock = false;
            this.firstExtended = true;
          });
        } else {
          this.mapRequestLock = false;
          this.firstExtended = true;
        }
      }

      try {
        window.localStorage.removeItem('ofirio-from-search')
      } catch (ex) {}

      this.mapMarkers = markersArr;
    },
    toggleMobileViewMode() {
      this.mobileViewMode = this.mobileViewMode == 'list' ? 'map' : 'list';
      window.scrollTo(0, 0);
    },
    toggleDrawingMode(mode: string) {
      if (mode == 'clear') {
        this.searchRegions = [];
        this.refresh(true);

      } else if (mode == 'draw') {
        this.mapMarkers = [];
        this.searchRegions = [];
        this.drawMode = true;
        document.documentElement.classList.toggle('no-scroll', true);

      } else if (mode == 'cancel' || mode == 'enddraw') {
        if (mode == 'cancel')
          this.searchRegions = [];
        this.drawMode = false;
        document.documentElement.classList.toggle('no-scroll', false);
        this.refresh(true, mode == 'cancel');
      }
/*
      this.drawMode = forceValue == undefined ? !this.drawMode : forceValue;

      if (this.drawMode) {
        this.mapMarkers = [];
        this.searchRegions = [];

      } else {
        this.refresh(true);
      }*/
    },
    async onInit() {
      await this.requestSearch(<TSearchRoute>this.$route.params, 0, true);
      
      let scrollTop:number | typeof NaN = parseFloat(<string>document.body.getAttribute('data-scroll-top'));
      document.body.removeAttribute('data-scroll-top');

      if (!Number.isNaN(scrollTop))
        this.$nextTick(() => {
          window.scrollTo({ top: scrollTop, behavior: 'smooth' });
        });

      this.onMapDragEnd();
      this.onMapZoomChange(true);
    }
  },
  async mounted() {
    localStorage.removeItem('ofirio-saved-after-login-data-after-login');
    localStorage.removeItem('ofirio-saved-after-login-active');
    localStorage.removeItem('ofirio-saved-after-login-url');

    const mapRef = <any>this.$refs.mapRef;
    let watchOnce = watch(() => mapRef?.ready, (status: boolean) => {
      if (status == true) {
        watchOnce();

        const GMApi = mapRef.api;
        const rawMap = toRaw(mapRef.map);

        this.mapInfoWindow = new GMApi.InfoWindow({
          content: (<any>this.$refs).mapInfoWindow.$el
        });

        GMApi.event.addDomListener(mapRef.map.getDiv(), 'pointerdown', (e:any) => {

          if (!this.drawMode)
            return;
          
          if (this.$isMobile.value)
            e.preventDefault();

          let domEvTarget = e.target;
          while (domEvTarget != document.body)
            if (domEvTarget.getAttribute('aria-label') == 'Map')
              break;
            else
              domEvTarget = domEvTarget?.parentElement;

          if (domEvTarget == document.body)
            return;

          const oldOptions = toRaw({
            draggable: toRaw(mapRef.map.draggable),
            zoomControl: toRaw(mapRef.map.zoomControl),
            scrollwheel: toRaw(mapRef.map.scrollwheel),
            disableDoubleClickZoom: toRaw(mapRef.map.disableDoubleClickZoom)
          });
          mapRef.map.setOptions({
            draggable: false,
            zoomControl: false,
            scrollwheel: false,
            disableDoubleClickZoom: false
           });

          let poly = new GMApi.Polyline({
            map: mapRef.map,
            clickable: false
          });

          //move-listener
          var move = GMApi.event.addListener(mapRef.map, 'mousemove', (e:any) => {
            // e.domEvent.stopPropagation();
            poly.getPath().push(e.latLng);

            if (this.$isMobile.value)
              e.domEvent.preventDefault();
          });

          //mouseup-listener
          var once = GMApi.event.addDomListener(mapRef.map.getDiv(), this.$isMobile.value ? 'touchend' : 'pointerup', (e:any) => {
            GMApi.event.removeListener(move);
            GMApi.event.removeListener(once);

              var path = poly.getPath();
              poly.setMap(null);

              this.searchRegions.push(createPolygon(path, true));
              mapRef.map.setOptions(oldOptions);
          });
        });

        GMApi.event.addListenerOnce(mapRef.map, 'idle', () => {
          this.onInit();
        });
      }
    });

    this.setCustomizationFromUrlParams();


    watch(() => AccountStore.Auth.isLoggedIn, (state:boolean) => {
      if (state === true)
        this.refresh();
    });
    watch(() => SearchModel.searchResults.value, (newState:any) => {
      this.extentMapToMarkersTimer();
    }, { deep: true });
  }
})
</script>