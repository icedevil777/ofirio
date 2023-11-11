<template>
<div class="property wrapper">
  <UPreloader v-if="$isMobile.value && !customizationReady" mode="breadcrumbs" :activation="true" />
  <UBreadcrumbs v-else-if="$isMobile.value && Property.Basis.dto?.address">
    <router-link class="ui-href-gray" to="/">Home</router-link>
    <router-link class="ui-href-gray" :to="{ name: 'search', params: { typeOptions: toUrl({ state_id: Property.Basis.dto?.address.state_code }) } }" v-text="Property.Basis.dto?.address.state" v-if="Property.Basis.dto?.address.state"></router-link>
    <router-link class="ui-href-gray" :to="{ name: 'search', params: { typeOptions: toUrl({ state_id: Property.Basis.dto?.address.state_code, county: Property.Basis.dto?.address.county }) } }" v-text="Property.Basis.dto?.address.county" v-if="Property.Basis.dto?.address.county"></router-link>
    <router-link class="ui-href-gray" :to="{ name: 'search', params: { typeOptions: toUrl({ state_id: Property.Basis.dto?.address.state_code, county: Property.Basis.dto?.address.county, city: Property.Basis.dto?.address.city }) } }" v-text="Property.Basis.dto?.address.city" v-if="Property.Basis.dto?.address.city"></router-link>
    <router-link class="ui-href-gray" :to="{ name: 'property', params: { id: $route.params.id } }" v-text="Property.Basis.dto?.address.line" v-if="Property.Basis.dto?.address.line"></router-link>
  </UBreadcrumbs>
  <UDivider class="hide-desktop" />
  <div class="top-bar" ref="headerBar">
    <div class="heading-row" :class="{ 'sticked': headerRowState >= 1, 'sticked-full': headerRowState >= 2, scrollingUp: scrollingDown > 100 }">
      <div class="wrapper flex header-bar">
        <UPreloader v-if="!customizationReady" mode="propertyAddress" :activation="!customizationReady" :width="50" />
        <div v-else class="address flex">
          <UCopyToCb :text="fullPropertyAddress">
            <template v-slot="{ props }">
              <span class="street" title="Click to copy" @click="props.copyToClipboard" v-text="Property.Basis.dto?.address.line"></span>
              <span class="location" title="Click to copy" @click="props.copyToClipboard">{{ Property.Basis.dto?.address.city }}, {{ Property.Basis.dto?.address.state }} {{ Property.Basis.dto?.address.zip }}</span>
            </template>
          </UCopyToCb>
          <StatusLabel :label="Property.Basis.dto?.status" />
        </div>
        <div class="small-props flex">
          <USmallProp label="List price" :value="$format['usdInt'](Property.Basis.dto?.data.price)" />
          <USmallProp class="hide-mobile-sticked" label="Beds" :value="$format['number'](Property.Basis.dto?.data.beds)" />
          <USmallProp class="hide-mobile-sticked" label="Baths" :value="$format['number'](Property.Basis.dto?.data.baths)" />
          <div v-if="!Account.Basis.isPremium" class="hidden">
            <UnlockAnalytics mode="simple">Unlock</UnlockAnalytics>
            <span>Cash On Cash</span>
          </div>
          <USmallProp v-else label="Cash On Cash" colorScheme="cap-coc" :value="Property.Finance.dto?.performance.cash_on_cash_year1" :formatter="$format['%']" />
          <div v-if="!Account.Basis.isPremium" class="hidden">
            <UnlockAnalytics mode="simple">Unlock</UnlockAnalytics>
            <span>Cap Rate</span>
          </div>
          <USmallProp v-else label="Cap Rate" colorScheme="cap-coc" :value="Property.Finance.dto?.performance.cap_rate_year1" :formatter="$format['%']" />
        </div>
        <div class="prop-actions flex">
          <div class="mobile-mm"></div>
          <router-link v-if="Property.Basis.dto && Account.Basis.isPremium" :target="!$isMobile.value ? '_blank' : ''" :to="{
            name: 'rent-estimator',
            params: {
              address: fullPropertyAddress,
              options: toUrl({
                prop_id: Property.Basis.getId(),
                beds: Property.Basis.dto.data.beds,
                baths: Property.Basis.dto.data.baths,
                propType: Property.Basis.dto.data.prop_type2,
                building_size: Property.Basis.dto.data.building_size
              })
            }
          }">
            <UButton class="ui-btn-text-gray"><UIcon name="stacked-plots" />{{ $isMobile.value ? 'Rent Estimator' : 'Rent Est.' }}</UButton>
          </router-link>
          <UButton class="ui-btn-text-gray" v-else @click="Account.Restrictions.canUseCustomization() && true"><UIcon name="stacked-plots" />{{ $isMobile.value ? 'Rent Estimator' : 'Rent Est.' }}</UButton>
          <UButton class="ui-btn-text-gray" :class="{ disabled: !Property.Basis.dto || !customizationReady }" @click="Account.Restrictions.canUseCustomization() && getReport()"><UIcon name="download" />Report</UButton>
          <FavoriteHeart v-if="Property.Basis.dto && !$isMobile.value" :property="Property.Basis">
            <template v-slot="{ active, toggle }">
              <UButton class="ui-btn-text-gray" @click="toggle()"><UIcon name="heart-save" class="ui-property-favorite-icon" :class="{ active }"/>Save</UButton>
            </template>
          </FavoriteHeart>
          <FavoriteHeart v-if="Property.Basis.dto && $isMobile.value" :property="Property.Basis" />
          <div class="mobile-mm"></div>
        </div>
      </div>
      <UDivider class="wrapper" />
      <div class="wrapper flex tabs">
        <div class="mobile-mm"></div>
        <URadioChip v-model="activeTab" required name="radio-active-tab" value="summary">Summary</URadioChip>
        <URadioChip v-model="activeTab" required name="radio-active-tab" value="financial">Financial</URadioChip>
        <URadioChip v-model="activeTab" required name="radio-active-tab" value="tax-history">Tax History</URadioChip>
        <URadioChip v-model="activeTab" required name="radio-active-tab" value="prop-history">Property History</URadioChip>
        <URadioChip v-if="!Property.Basis.dto?.data?.is_mls" v-model="activeTab" required name="radio-active-tab" value="schools">Schools</URadioChip>
        <div class="mobile-mm"></div>
      </div>
    </div>
  </div>
  <UDivider class="hide-mobile" />
  <UPreloader v-if="!$isMobile.value && !customizationReady" mode="breadcrumbs" :activation="!customizationReady" :width="50"/>
  <UBreadcrumbs v-else-if="!$isMobile.value && Property.Basis.dto?.address">
    <router-link class="ui-href-gray" to="/">Home</router-link>
    <router-link class="ui-href-gray" :to="{ name: 'search', params: { typeOptions: toUrl({ state_id: Property.Basis.dto?.address.state_code }) } }" v-text="Property.Basis.dto?.address.state" v-if="Property.Basis.dto?.address.state"></router-link>
    <router-link class="ui-href-gray" :to="{ name: 'search', params: { typeOptions: toUrl({ state_id: Property.Basis.dto?.address.state_code, county: Property.Basis.dto?.address.county }) } }" v-text="Property.Basis.dto?.address.county" v-if="Property.Basis.dto?.address.county"></router-link>
    <router-link class="ui-href-gray" :to="{ name: 'search', params: { typeOptions: toUrl({ state_id: Property.Basis.dto?.address.state_code, county: Property.Basis.dto?.address.county, city: Property.Basis.dto?.address.city }) } }" v-text="Property.Basis.dto?.address.city" v-if="Property.Basis.dto?.address.city"></router-link>
    <router-link class="ui-href-gray" :to="{ name: 'property', params: { id: $route.params.id } }" v-text="Property.Basis.dto?.address.line" v-if="Property.Basis.dto?.address.line"></router-link>
  </UBreadcrumbs>
  <div class="basic-info flex">
    <UPreloader v-if="!$isMobile.value && !customizationReady" mode="propertyImages" :activation="!customizationReady" :width="55"/>
    <UImagesPreview
      :images="Property.Basis.dto?.photos"
      :popupRef="$refs.imagesPopup"
      v-else-if="!$isMobile.value"
    >
      <template v-slot:overMainImageSlot>
        <div class="label-block flex">
          <StatusLabel :label="badge" v-for="badge of Property.Basis.dto?.badges" :key="badge"/>
          <StatusLabel label="55plus" v-if="Property.Basis.dto?.is_55_plus" />
          <StatusLabel label="rehab" v-if="Property.Basis.dto?.is_rehab" />
          <StatusLabel label="cash_only" v-if="Property.Basis.dto?.is_cash_only" />
        </div>
      </template>
    </UImagesPreview>
    <UPreloader v-if="$isMobile.value && !customizationReady" mode="propertyImages" :activation="true" />
    <div class="images-mobile" v-else-if="$isMobile.value">
      <swiper v-if="Property.Basis.dto && Property.Basis.dto?.photos.length > 0" :loop="true" :pagination="{ clickable: true, dynamicBullets: true }">
        <swiper-slide tag="img" alt="Additional photo" v-for="imgUrl of Property.Basis.dto?.photos" :key="imgUrl" :src="imgUrl" @click="() => $refs.imagesPopup.open()"></swiper-slide>
      </swiper>
      <img v-else src="@/assets/images/common/image-placeholder.png" alt="No Image" class="image-placeholder">
      <div class="label-block flex">
        <StatusLabel :label="badge" v-for="badge of Property.Basis.dto?.badges" :key="badge"/>
        <StatusLabel label="55plus" v-if="Property.Basis.dto?.is_55_plus" />
        <StatusLabel label="rehab" v-if="Property.Basis.dto?.is_rehab" />
        <StatusLabel label="cash_only" v-if="Property.Basis.dto?.is_cash_only" />
      </div>
      <FavoriteHeart v-if="Property.Basis.dto" :property="Property.Basis" />
    </div>
    <div class="info">
      <UPreloader v-if="!customizationReady" mode="charsRow" :activation="true" />
      <div v-else class="chars-row flex">
        <div class="char">
          <span class="title">List Price</span>
          <span class="value">{{ $format['usdInt'](Property.Basis.dto?.data.price) }}</span>
        </div>
        <div class="char">
          <span class="title">Beds</span>
          <span class="value">{{ $format['number'](Property.Basis.dto?.data.beds) }}</span>
        </div>
        <div class="char">
          <span class="title">Baths</span>
          <span class="value">{{ $format['number'](Property.Basis.dto?.data.baths) }}</span>
        </div>
        <div class="char">
          <span class="title">Sq Ft</span>
          <span class="value">{{ $format['number'](Property.Basis.dto?.data.building_size) }}</span>
        </div>
        <div class="char hide-mobile-small">
          <span class="title hide-desktop">$/ft²</span>
          <span class="title hide-mobile">Price/ft²</span>
          <span class="value">{{ $format['usdInt'](Property.Basis.dto?.data.price_per_sqft) }}</span>
        </div>
      </div>
      <div class="fifty-five-community" v-if="customizationReady && Property.Basis.dto?.is_55_plus">
        <UCollapsible opened>
          <template v-slot:header>
            <div class="flex">
              <span>
                <UIcon name="fifty-five-community"/>
                55+ Community
              </span>
              <UIcon name="smooth-arrow"/>
            </div>
          </template>
          <template v-slot:default>
            <span>
              This property is located in a 55+ community and there may be additional fees and restrictions. Confirm the details with the community
            </span>
          </template>
        </UCollapsible>
      </div>
      <div class="fifty-five-community" v-if="customizationReady && Property.Basis.dto?.is_cash_only">
        <UCollapsible opened>
          <template v-slot:header>
            <div class="flex">
              <span>
                <UIcon name="fifty-five-community"/>
                Cash Only
              </span>
              <UIcon name="smooth-arrow"/>
            </div>
          </template>
          <template v-slot:default>
            <span>
              This property can only be purchased with cash.<br>Financing options are not available.
            </span>
          </template>
        </UCollapsible>
      </div>
      <SmallPropsTable>
        <tr>
          <td>
            <div class="char">
              <UPreloader mode="smallPropsTable" :activation="!customizationReady">
                <UnlockAnalytics v-if="!Account.Basis.isPremium" mode="simple">Unlock</UnlockAnalytics>
                <span v-else class="value">{{ $format['usdInt'](Property.Finance.dto?.main_results.rental_income) }}</span>
              </UPreloader>
              <span class="title"><UTooltip mode="top" :icon="$isMobile.value ? 'none' : undefined" :text="TooltipTexts['rental_income']"/>{{ $isMobile.value ? 'Rent. Income' : 'Rental Income' }} </span>
            </div>
          </td>
          <td>
            <div class="char">
              <UPreloader mode="smallPropsTable" :activation="!customizationReady">
                <UnlockAnalytics v-if="!Account.Basis.isPremium" mode="simple">Unlock</UnlockAnalytics>
                <span v-else class="value">{{ $format['usdInt'](Property.Finance.dto?.main_results.expenses) }}</span>
              </UPreloader>
              <span class="title"><UTooltip mode="top" :icon="$isMobile.value ? 'none' : undefined" :text="TooltipTexts['expenses']"/>Expenses</span>
            </div>
          </td>
          <td>
            <div class="char">
              <UPreloader mode="smallPropsTable" :activation="!customizationReady">
                <UnlockAnalytics v-if="!Account.Basis.isPremium" mode="simple">Unlock</UnlockAnalytics>
                <span v-else class="value">{{ $format['usdInt'](Property.Finance.dto?.main_results.cash_flow) }}</span>
              </UPreloader>
              <span class="title"><UTooltip mode="top" :icon="$isMobile.value ? 'none' : undefined" :text="TooltipTexts['cash_flow']"/>Cash Flow</span>
            </div>
          </td>
        </tr>
        <tr>
          <td>
            <div class="char">
              <UPreloader mode="smallPropsTable" :activation="!customizationReady">
                <UnlockAnalytics v-if="!Account.Basis.isPremium" mode="simple">Unlock</UnlockAnalytics>
                <span v-else class="value" v-colorBy:cap-coc="Property.Finance.dto?.main_results.cash_on_cash">{{ $format['%'](Property.Finance.dto?.main_results.cash_on_cash) }}</span>
              </UPreloader>
              <span class="title"><UTooltip mode="top" :icon="$isMobile.value ? 'none' : undefined" :text="TooltipTexts['cash_on_cash']"/>{{ $isMobile.value ? 'Coc' : 'Cash on Cash' }}</span>
            </div>
          </td>
          <td>
            <div class="char">
              <UPreloader mode="smallPropsTable" :activation="!customizationReady">
                <UnlockAnalytics v-if="!Account.Basis.isPremium" mode="simple">Unlock</UnlockAnalytics>
                <span v-else class="value" v-colorBy:cap-coc="Property.Finance.dto?.main_results.cap_rate">{{ $format['%'](Property.Finance.dto?.main_results.cap_rate) }}</span>
              </UPreloader>
              <span class="title"><UTooltip mode="top" :icon="$isMobile.value ? 'none' : undefined" :text="TooltipTexts['cap_rate']"/>CAP Rate</span>
            </div>
          </td>
          <td>
            <div class="char">
              <UPreloader mode="smallPropsTable" :activation="!customizationReady">
                <UnlockAnalytics v-if="!Account.Basis.isPremium" mode="simple">Unlock</UnlockAnalytics>
                <span v-else class="value">{{ $format['%'](Property.Finance.dto?.main_results.total_return) }} </span>
              </UPreloader>
              <span class="title"><UTooltip mode="top" :icon="$isMobile.value ? 'none' : undefined" :text="TooltipTexts['total_return']"/>Total Return</span>
            </div>
          </td>
        </tr>
        <tr>
          <td colspan="3">
            <UButton class="bottom-action flex" @click="() => $refs.customizationPopup.open()" :busy="!customizationReady">
              <UIcon name="calculator"/>
              Edit calculations
            </UButton>
          </td>
        </tr>
      </SmallPropsTable>
      <div class="slider">
        <div class="slider-info flex">
          <span class="title"><UTooltip mode="top" :text="TooltipTexts['purchase_price']"/> Purchase Price</span>
          <UPreloader mode="sliderInfo" :activation="!customizationReady" :width="20">
            <span class="value">{{ $format['usdInt'](customizationParameters.price) }}</span>
          </UPreloader>
        </div>
        <UPreloader mode="slider" :activation="!customizationReady">
          <USlider v-if="customizationParametersPercentiles.price" @mousedown="!Account.Restrictions.canUseCustomization() && true" v-model="customizationParameters.price" v-bind="{ ...DataModel['purchase_price'](Property.Basis.dto?.data.price), ...DataModel['slider__purchase_price']}"/>
        </UPreloader>
      </div>
      <div class="slider">
        <div class="slider-info flex">
          <span class="title"><UTooltip mode="top" :text="TooltipTexts['down_payment']"/> Down Payment</span>
          <UPreloader mode="sliderInfo" :activation="!customizationReady" :width="20">
            <UnlockAnalytics v-if="!Account.Basis.isPremium" mode="simple">Unlock</UnlockAnalytics>
            <span v-else class="value">{{ $format['%Int'](customizationParameters.down_payment) }}</span>
          </UPreloader>
        </div>
        <UPreloader mode="slider" :activation="!customizationReady">
          <USlider v-model="customizationParameters.down_payment" @mousedown="!Account.Restrictions.canUseCustomization() && true" v-bind="{ ...DataModel['down_payment'](Property.Basis.dto), ...DataModel['slider__down_payment']}" />
        </UPreloader>
      </div>
      <div class="slider slider-estimated-rent">
        <div class="slider-info flex">
          <span class="title"><UTooltip mode="top" :text="TooltipTexts['estimated_rent']"/> Estimated Rent</span>
          <img src="@/assets/icons/ai-powered-color.svg" alt="AI Powered">
          <UPreloader mode="sliderInfo" :activation="!customizationReady" :width="20">
            <UnlockAnalytics v-if="!Account.Basis.isPremium" mode="simple">Unlock</UnlockAnalytics>
            <span v-else class="value">{{ $format['usdInt'](customizationParameters.monthly_rent) }}</span>
          </UPreloader>
        </div>
        <UPreloader mode="slider" :activation="!customizationReady">
          <USlider className="monthly-rate-slider" v-model="customizationParameters.monthly_rent" @mousedown="!Account.Restrictions.canUseCustomization() && true" v-bind="{ ...DataModel['estimated_rent'](Property.Basis.dto), ...DataModel['slider__estimated_rent'](Property.Basis.dto) }" showPercentiles />
        </UPreloader>
      </div>
      <div class="estimated-prediction-quality flex">
        <span class="title"><UTooltip mode="top" :text="TooltipTexts['estimated_rent']"/> Rent Prediction Quality</span>
        <span class="bar" :class="{ [ 'quality-' + Property.Basis.dto?.prediction_quality ]: customizationReady }"></span>
        <UPreloader mode="sliderInfo" :activation="!customizationReady" :width="20">
          <UnlockAnalytics v-if="!Account.Basis.isPremium" mode="simple">Unlock</UnlockAnalytics>
          <span v-else class="value" :class="[ 'quality-' + Property.Basis.dto?.prediction_quality ]">{{ Property.Basis.dto?.prediction_quality.charAt(0).toUpperCase() + Property.Basis.dto?.prediction_quality.slice(1) }}</span>
        </UPreloader>
      </div>
    </div>
  </div>
  <UPreloader v-if="!customizationReady" mode="tabs" :activation="true" :width="50" />
  <div v-else class="tabs flex wrapper" ref="tabsBar">
    <div class="mobile-mm"></div>
    <URadioChip v-model="activeTab" required name="radio-active-tab" value="summary">
      <UIcon name="house" /><span class="tab-name">Summary</span>
    </URadioChip>
    <URadioChip v-model="activeTab" required name="radio-active-tab" value="financial">
      <UIcon name="pay-date" /><span class="tab-name">Financial</span>
    </URadioChip>
    <URadioChip v-model="activeTab" required name="radio-active-tab" value="tax-history">
      <UIcon name="money-scissors" /><span class="tab-name">Tax History</span>
    </URadioChip>
    <URadioChip v-model="activeTab" required name="radio-active-tab" value="prop-history">
      <UIcon name="document-time" /><span class="tab-name">Property History</span>
    </URadioChip>
    <URadioChip v-if="!Property.Basis.dto?.data?.is_mls" v-model="activeTab" required name="radio-active-tab" value="schools">
      <UIcon name="school" /><span class="tab-name">Schools</span>
    </URadioChip>
    <div class="mobile-mm"></div>
  </div>
  <div class="tab tab-summary" v-show="activeTab == 'summary'">
    <div class="sided-info flex">
      <div class="text-side">
        <p class="description ui-text-justify" v-text="Property.Basis.dto?.data.description"></p>
        <UButton class="ui-btn ui-btn-bordered-green call-agents" @click="() => { $root.$refs.popupCallUsBody.setProperty(Property); $root.$refs.popupCallUs.open() }">Contact Agents</UButton>
      </div>
      <div class="location">
        <div class="map">
          <GoogleMap
              v-if="Property.Basis.dto?.address"
              class="google-map"
              :api-key="GAPI_KEY"
              :center="{ lat: Property.Basis.dto?.address.lat, lng: Property.Basis.dto?.address.lon }"
              :zoom="17"
              :disableDefaultUI="true"
              :streetViewControl="true"
              :mapTypeControl="true"
              :fullscreenControl="false"
              :zoomControl="true"
              :minZoom="8"
              :zoomControlPosition="'TOP_RIGHT'"
              gestureHandling="greedy"
              ref="mapRef"
            >
              <Marker
                :options="{
                  position: { lat: Property.Basis.dto?.address.lat, lng: Property.Basis.dto?.address.lon },
                  icon: '/mapMarkerIcons/map-icon-property.svg'
                }"
              />
            </GoogleMap>
        </div>
      </div>
    </div>
    <div class="additional-info" v-if="Property.Basis.dto">
      <FeatureBlock>
        <div class="feature-header flex"><UIcon name="house-checkmark" />Summary</div>
        <div class="feature-section">
          <ul class="features-section-list">
            <li>
              <span class="title">Status:</span>
              <span class="value">{{ $format['enumSafe']('EProperty_Status', Property.Basis.dto?.summary.status) }}</span>
            </li>
            <li>
              <span class="title">Bedrooms:</span>
              <span class="value" v-text="Property.Basis.dto?.summary.beds"></span>
            </li>
            <li>
              <span class="title">Bathrooms:</span>
              <span class="value" v-text="Property.Basis.dto?.summary.baths"></span>
            </li>
            <li>
              <span class="title">Property Type:</span>
              <span class="value">{{ $format['enumSafe']('EProperty_Type', Property.Basis.dto?.summary.prop_type) }}</span>
            </li>
            <li>
              <span class="title">Year Built:</span>
              <span class="value" v-text="Property.Basis.dto?.summary.year_built || '-'"></span>
            </li>
            <li v-if="Property.Basis.dto?.summary.last_sold_price != '-' && Property.Basis.dto?.summary.last_sold_date != '-'">
              <span class="title">Last Sold:</span>
              <span class="value">{{ $format['usdInt'](Property.Basis.dto?.summary.last_sold_price) }} on {{ $format['date'](Property.Basis.dto?.summary.last_sold_date) }}</span>
            </li>
            <li>
              <span class="title">Size:</span>
              <span class="value" v-text="Property.Basis.dto?.summary.building_size"></span>
            </li>
            <li>
              <span class="title">Price Per Sqft:</span>
              <span class="value" v-text="$format['usd'](Property.Basis.dto?.summary.price_per_sqft)"></span>
            </li>
            <li>
              <span class="title">Property Taxes/mo:</span>
              <span class="value" v-text="$format['usd'](Property.Basis.dto?.summary.monthly_tax)"></span>
            </li>
            <li>
              <span class="title">Property Insurance/mo:</span>
              <span class="value" v-text="$format['usd'](Property.Basis.dto?.summary.monthly_insurance)"></span>
            </li>
            <li>
              <span class="title">HOA Fees:</span>
              <span class="value" v-text="$format['usd'](Property.Basis.dto?.summary.hoa_fees)"></span>
            </li>
            <li>
              <span class="title">Pool:</span>
              <span class="value" v-text="Property.Basis.dto?.summary.pool"></span>
            </li>
            <li>
              <span class="title">Garage and Parking:</span>
              <span class="value" v-text="Property.Basis.dto?.summary.garage"></span>
            </li>
          </ul>
        </div>
      </FeatureBlock>
      <FeatureBlock v-if="Property.Basis.dto?.public_records">
        <div class="feature-header flex"><UIcon name="clipboard-checkmark" />Public Records</div>
        <div class="feature-section">
          <ul class="features-section-list">
            <li v-for="(value, name) in Property.Basis.dto?.public_records" :key="name">
              <span class="title">{{ name }}:</span>
              <span class="value" v-text="value"></span>
            </li>
          </ul>
        </div>
      </FeatureBlock>
      <template v-for="(fvalue, fname) in Property.Basis.dto.features" :key="fname">
        <FeatureBlock :featureName="fname" :featureValue="fvalue" :icon="featuresBlocksIcons[fname]"/>
      </template>
    </div>
    <MLSInfo :mls="Property.Basis.dto?.data?.mls_type" :mlsDate="{ [Property.Basis.dto?.data?.mls_type]: Property.Basis.dto?.update_onsite }" />
  </div>
  <div class="tab tab-financial" v-show="activeTab == 'financial'">
    <UPreloader v-if="!$isMobile.value" mode="basicAssumptionsTitle" :activation="!customizationReady" :width="20">
      <span class="heading">Basic assumptions</span>
    </UPreloader>
    <UPreloader v-else mode="basicAssumptionsTitle" :activation="!customizationReady">
      <span class="heading">Basic assumptions</span>
    </UPreloader>
    <UPreloader v-if="!customizationReady" mode="basicAssumptionsInputs" :activation="true" />
    <div v-else class="params flex">
      <UDrop mHeader="Purchase Price" :disabled="Account.Basis.isPremium ? false : true">
        <template v-slot:label>
          <div class="param-data">
            <span class="param-name">Purchase Price</span>
            <span class="param-value">{{ $format['usdInt'](customizationParameters.price) }}</span>
          </div>
          <UIcon name="smooth-arrow" />
        </template>
        <template v-slot:content="{ props }">
          <UDropAdjustment v-if="customizationReady" @reset="resetCustomization('price')" @apply="props.close">
            <div class="padder">
              <span class="drop-title hide-mobile">Purchase Price</span>
              <USlider v-if="customizationParametersPercentiles.price" v-model="customizationParameters.price" v-bind="{ ...DataModel['purchase_price'](Property.Basis.dto?.data.price), ...DataModel['slider__purchase_price']}"/>
              <UTextInput @enter="props.close" v-model="customizationParameters.price" v-bind="DataModel['purchase_price'](Property.Basis.dto?.data.price)" :debounce="1000" :formatter="$format['usdInt']" validationMessageShow></UTextInput>
            </div>
          </UDropAdjustment>
        </template>
      </UDrop>
      <UDrop mHeader="Rent" :disabled="Account.Basis.isPremium ? false : true">
        <template v-slot:label>
          <div class="param-data">
            <span class="param-name">Rent</span>
            <UnlockAnalytics v-if="!Account.Basis.isPremium" mode="simple">Unlock</UnlockAnalytics>
            <span v-else class="param-value">{{ $format['usdInt'](customizationParameters.monthly_rent) }}</span>
          </div>
          <UIcon name="smooth-arrow" />
        </template>
        <template v-slot:content="{ props }">
          <UDropAdjustment v-if="customizationReady" @reset="resetCustomization('monthly_rent')" @apply="props.close">
            <div class="padder">
              <span class="drop-title hide-mobile">Monthly Rent</span>
              <USlider className="monthly-rate-slider" v-model="customizationParameters.monthly_rent" v-bind="{ ...DataModel['estimated_rent'](Property.Basis.dto), ...DataModel['slider__estimated_rent'](Property.Basis.dto) }" showPercentiles />
              <UTextInput @enter="props.close" v-model="customizationParameters.monthly_rent" v-bind="DataModel['estimated_rent'](Property.Basis.dto)" :debounce="1000" :formatter="$format['usdInt']" validationMessageShow></UTextInput>
            </div>
          </UDropAdjustment>
        </template>
      </UDrop>
      <UDrop mHeader="Down Payment" :disabled="Account.Basis.isPremium && !Property.Basis.dto?.is_cash_only ? false : true">
        <template v-slot:label>
          <div class="param-data">
            <span class="param-name">Down Payment</span>
            <UnlockAnalytics v-if="!Account.Basis.isPremium" mode="simple">Unlock</UnlockAnalytics>
            <span v-else class="param-value">{{ $format['%Int'](customizationParameters.down_payment) }}</span>
          </div>
          <UIcon name="smooth-arrow" />
        </template>
        <template v-slot:content="{ props }">
          <UDropAdjustment v-if="customizationReady" @reset="resetCustomization('down_payment')" @apply="props.close">
            <div class="padder">
              <span class="drop-title hide-mobile">Down Payment</span>
              <USlider v-model="customizationParameters.down_payment" v-bind="{ ...DataModel['down_payment'](Property.Basis.dto), ...DataModel['slider__down_payment']}"/>
              <UTextInput @enter="props.close" v-model="customizationParameters.down_payment" v-bind="DataModel['down_payment'](Property.Basis.dto)" :debounce="1000" :decimals="0" subtype="percent" :formatter="$format['%Int']" validationMessageShow></UTextInput>
            </div>
          </UDropAdjustment>
        </template>
      </UDrop>
      <UDrop mHeader="Financing Years" :disabled="Account.Basis.isPremium && !Property.Basis.dto?.is_cash_only ? false : true">
        <template v-slot:label>
          <div class="param-data">
            <span class="param-name">Financing Years</span>
            <UnlockAnalytics v-if="!Account.Basis.isPremium" mode="simple">Unlock</UnlockAnalytics>
            <span v-else class="param-value">{{ customizationParameters.financing_years }} years</span>
          </div>
          <UIcon name="smooth-arrow" />
        </template>
        <template v-slot:content="{ props }">
          <UDropAdjustment v-if="customizationReady" @reset="resetCustomization('financing_years')" @apply="props.close">
            <div class="padder">
              <span class="drop-title hide-mobile">Financing Years</span>
              <USlider v-model="customizationParameters.financing_years" v-bind="{ ...DataModel['financing_years'](Property.Basis.dto), ...DataModel['slider__financing_years']}" />
              <UTextInput @enter="props.close" v-model="customizationParameters.financing_years" v-bind="DataModel['financing_years'](Property.Basis.dto)" validationMessageShow></UTextInput>
            </div>
          </UDropAdjustment>
        </template>
      </UDrop>
      <UDrop mHeader="Interest Rate" :disabled="Account.Basis.isPremium && !Property.Basis.dto?.is_cash_only ? false : true">
        <template v-slot:label>
          <div class="param-data">
            <span class="param-name">Interest Rate</span>
            <UnlockAnalytics v-if="!Account.Basis.isPremium" mode="simple">Unlock</UnlockAnalytics>
            <span v-else class="param-value">{{ $format['%'](customizationParameters.interest_rate) }}</span>
          </div>
          <UIcon name="smooth-arrow" />
        </template>
        <template v-slot:content="{ props }">
          <UDropAdjustment v-if="customizationReady" @reset="resetCustomization('interest_rate')" @apply="props.close">
            <div class="padder">
              <span class="drop-title hide-mobile">Interest Rate</span>
              <USlider v-model="customizationParameters.interest_rate" v-bind="{ ...DataModel['interest_rate'](Property.Basis.dto), ...DataModel['slider__interest_rate']}" />
              <UTextInput @enter="props.close" v-model="customizationParameters.interest_rate" v-bind="DataModel['interest_rate'](Property.Basis.dto)" :debounce="1000" subtype="percent" :formatter="$format['%']" validationMessageShow></UTextInput>
            </div>
          </UDropAdjustment>
        </template>
      </UDrop>
      <UButton class="ui-btn ui-btn-bordered-gray flex" @click="$refs.customizationPopup.open()"><UIcon name="adjustments" />More</UButton>
    </div>
    <UPreloader v-if="!customizationReady" mode="finDetails" :activation="true" />
    <div v-else class="flex fin-details">
      <MonthlyCashFlow
        :customizationPopup="$refs.customizationPopup"
        :financeModel="Property.Finance"
        class="side"
      />
      <DetailedAssumptions
        :customizationPopup="$refs.customizationPopup"
        :financeModel="Property.Finance"
        class="side"
      />
      <PerfomanceDashboard
        :customizationPopup="$refs.customizationPopup"
        :financeModel="Property.Finance"
        class="side"
      />
    </div>
    <UPreloader v-if="!customizationReady" mode="proForma" :activation="true" />
    <div v-else class="full-pro-forma">
      <div class="head-row flex">
        <span class="heading">Pro Forma</span>
        <UButton class="ui-btn ui-btn-bordered-gray" @click="$refs.customizationPopup.open()"><UIcon name="adjustments" />Customize</UButton>
      </div>
      <div class="slide-to-more-years hide-desktop">
        <span>Slide to see more years</span>
        <UIcon name="arrow" />
      </div>
      <div class="table-wrapper">
        <table class="fin-table">
          <UnlockAnalytics v-if="!Account.Basis.isPremium">{{ $isMobile.value ? 'Unlock' : 'Unlock Analytics' }}</UnlockAnalytics>
          <tr>
            <td class="head">Parameters</td>
            <td class="head" v-for="year of ProForma.years" :key="year">Year {{ year }}</td>
          </tr>

          <template v-for="(block, i) of ProForma.blocks" :key="block">
            <tr :class="{ strip: (i + 1) % 2 == 0 }">
              <td :colspan="ProForma.years.length + 1"></td>
            </tr>

            <tr :class="[ { strip: (i + 1) % 2 == 0 }, block.titleRow.rowClass]" @click="proFormaRowsOpenStatus[i] = !proFormaRowsOpenStatus[i]">
              <td :class="block.titleRow.titleClass"><UTooltip mode="top" :icon="!block.titleRow.tooltip ? 'empty' : undefined" :text="block.titleRow.tooltip"/> {{ block.titleRow.title }} <UIcon name="smooth-arrow" :class="{ 'rotate': !proFormaRowsOpenStatus[i] }" /></td>
              <td :class="block.titleRow.valuesClass" :style="{ 'opacity': proFormaRowsOpenStatus[i] ? 0 : 1   }" v-for="(value, vi) of Property.Finance.dto?.proforma[block.titleRow.valuesKey]" :key="vi">{{ $format[block.titleRow.format](value) }}</td>
            </tr>
            <transition-group name="slide">

              <tr
                v-for="row of block.collapsibleRows"
                :key="row"
                :class="[ { strip: (i + 1) % 2 == 0 }, row.rowClass]"
                v-show="proFormaRowsOpenStatus[i]"
              >
                <template v-if="row.type == 'row'">
                  <td :class="row.titleClass"><UTooltip mode="top" :icon="!row.tooltip ? 'empty' : undefined" :text="row.tooltip"/> {{ row.title }}</td>
                  <td :class="row.valuesClass" v-for="(value, vi) of Property.Finance.dto?.proforma[row.valuesKey]" :key="vi">{{ $format[row.format](value) }}</td>
                </template>

                <template v-else-if="row.type == 'divider'">
                  <td :colspan="ProForma.years.length + 1"></td>
                </template>

              </tr>

            </transition-group>

            <tr
              v-for="row of block.appendRows"
              :key="row"
              :class="[ { strip: (i + 1) % 2 == 0 }, row.rowClass]"
            >
              <template v-if="row.type == 'row'">
                <td :class="row.titleClass"><UTooltip mode="top" :icon="!row.tooltip ? 'empty' : undefined" :text="row.tooltip"/> {{ row.title }}</td>
                <td :class="row.valuesClass" v-for="(value, vi) of Property.Finance.dto?.proforma[row.valuesKey]" :key="vi">{{ $format[row.format](value) }}</td>
              </template>

              <template v-else-if="row.type == 'divider'">
                <td :colspan="ProForma.years.length + 1"></td>
              </template>

            </tr>

            <tr :class="{ strip: (i + 1) % 2 == 0 }">
              <td :colspan="ProForma.years.length + 1"></td>
            </tr>

          </template>

        </table>
      </div>
    </div>
    <UPreloader v-if="!customizationReady" mode="proForma" :activation="true" />
    <div v-else-if="FinanceAccumulatedWealthPlot" class="property-financial-plots">
      <div class="plot-item flex">
        <div class="side-data">
          <div class="data-row">
            <UnlockAnalytics v-if="!Account.Basis.isPremium" mode="simple">Unlock</UnlockAnalytics>
            <span v-else class="value">{{ $format['usdInt'](Property.Finance.dto?.accumulated_wealth.projected_accummulated_wealth[finance_acw_plot_tooltip_index]) }}</span>
            <div class="description">
              <UTooltip mode="top" :text="TooltipTexts['project_accumulated_wealth']" />
              Projected Accumulated Wealth
            </div>
          </div>
          <div class="data-row">
            <UnlockAnalytics v-if="!Account.Basis.isPremium" mode="simple">Unlock</UnlockAnalytics>
            <span v-else class="value">{{ $format['usdInt'](Property.Finance.dto?.accumulated_wealth.cash_flow_from_operations[finance_acw_plot_tooltip_index]) }}</span>
            <div class="description">
              <UTooltip mode="top" :text="TooltipTexts['project_cash_flow']" />
              Projected Cash Flow
            </div>
          </div>
          <div class="data-row">
            <UnlockAnalytics v-if="!Account.Basis.isPremium" mode="simple">Unlock</UnlockAnalytics>
            <span v-else class="value">{{ $format['usdInt'](Property.Finance.dto?.accumulated_wealth.eqity[finance_acw_plot_tooltip_index]) }}</span>
            <div class="description">
              <UTooltip mode="top" :text="TooltipTexts['project_equity']" />
              Projected Equity
            </div>
          </div>
          <div class="data-row">
            <UnlockAnalytics v-if="!Account.Basis.isPremium" mode="simple">Unlock</UnlockAnalytics>
            <span v-else class="value">{{ $format['usdInt'](Property.Finance.dto?.accumulated_wealth.loan_balance[finance_acw_plot_tooltip_index]) }}</span>
            <div class="description">
              <UTooltip mode="top" :text="TooltipTexts['loan_balance']" />
              Loan Balance
            </div>
          </div>
        </div>
        <div class="ui-plot">
          <div class="ui-plot-title">Projected Accumulated Wealth</div>
          <div class="ui-plot-legend flex">
            <div class="item" v-for="i of FinanceAccumulatedWealthPlot?.data?.datasets?.filter(o => !o.__autoLegendOff)" :key="i">
              <div class="flex">
                <span class="color" :style="{ background: i.borderColor, 'border-color': i.borderColor }"></span>
                <span class="title" v-text="i.label"></span>
              </div>
              <span v-if="Account.Basis.isPremium" class="value">{{ $format['usdInt'](Property.Finance.dto?.accumulated_wealth[i.__attrName][finance_acw_plot_tooltip_index]) }}</span>
            </div>
            <div class="item">
              <div class="flex" v-if="FinanceAccumulatedWealthPlot?.data?.datasets[0]">
                <span class="color" :style="{ 'border-color': FinanceAccumulatedWealthPlot?.data?.datasets[0].borderColor }"></span>
                <span class="title" v-text="FinanceAccumulatedWealthPlot?.data?.datasets[0].label"></span>
              </div>
              <span v-if="Account.Basis.isPremium" class="value">{{ $format['usdInt'](Property.Finance.dto?.accumulated_wealth.loan_balance[finance_acw_plot_tooltip_index]) }}</span>
            </div>
          </div>
          <div class="ui-plot-subdesc">30 years projection</div>
          <UnlockAnalytics v-if="!Account.Basis.isPremium">{{ $isMobile.value ? 'Unlock' : 'Unlock Analytics' }}</UnlockAnalytics>
          <div v-else class="ui-plot-wrapper">
            <vue3-chart-js
              v-if="FinanceAccumulatedWealthPlot && plotsShow"
              v-bind="{ ...FinanceAccumulatedWealthPlot }"
              :height="100"
              ref="finance_acw_chartRef"
            ></vue3-chart-js>
          </div>
        </div>
      </div>
    </div>
  </div>
  <div class="tab tab-tax-history" v-show="activeTab == 'tax-history'">
    <span class="heading" v-if="!Property.Taxes.dto?.tax_history || Property.Taxes.dto.tax_history.length < 1">No Tax History Found</span>
    <span class="heading" v-if="Property.Taxes.dto?.tax_history && Property.Taxes.dto.tax_history.length > 1">Tax History</span>
    <div class="ui-plot" v-if="Property.Taxes.dto?.tax_history && Property.Taxes.dto.tax_history.length > 1">
      <div class="ui-plot-legend">
        <div class="item flex" v-for="i of TaxHistoryPlot?.data?.datasets" :key="i">
          <div class="flex">
            <span class="color" :style="{ background: i.borderColor, 'border-color': i.borderColor }"></span>
            <span class="title" v-text="i.label"></span>
          </div>
        </div>
      </div>
      <div class="ui-plot-wrapper">
        <vue3-chart-js
          v-if="TaxHistoryPlot && plotsShow"
          v-bind="{ ...TaxHistoryPlot }"
          :height="100"
          ref="taxes_chartRef"
        ></vue3-chart-js>
      </div>
    </div>
    <span class="heading" v-if="Property.Taxes.dto?.tax_history && Property.Taxes.dto.tax_history.length > 0">Assessment History</span>
    <div class="table-wrapper">
      <table class="prop-list-table" v-if="Property.Taxes.dto?.tax_history">
        <tr v-for="(row, i) of Property.Taxes.dto?.tax_history" :key="row">
          <td>
            <div class="point"></div>
          </td>
          <td>
            <div class="prop-block">
              <span class="prop-name">Year</span>
              <span class="prop-value" v-text="row.year"></span>
            </div>
          </td>
          <td>
            <div class="prop-block">
              <span class="prop-name">Tax</span>
              <span class="prop-value ui-text-bolder">{{ $format['usdInt'](row.tax) }} <span class="smaller" v-if="i != Property.Taxes.dto.tax_history.length - 1" v-colorBy:invPosNeg="(row.tax - Property.Taxes.dto.tax_history[i+1].tax) / row.tax">({{ $format['%Signed']((row.tax - Property.Taxes.dto.tax_history[i+1].tax) / row.tax) }})</span></span>
            </div>
          </td>
          <td>
            <div class="prop-block">
              <span class="prop-name">Building Assessment</span>
              <span class="prop-value">{{ row.assessment?.building == null ? '-' : $format['usdInt'](row.assessment.building) }}</span>
            </div>
          </td>
          <td class="operation">&plus;</td>
          <td>
            <div class="prop-block">
              <span class="prop-name">Land Assessment</span>
              <span class="prop-value">{{ row.assessment?.land == null ? '-' : $format['usdInt'](row.assessment.land) }}</span>
            </div>
          </td>
          <td class="operation">=</td>
          <td>
            <div class="prop-block">
              <span class="prop-name">Total</span>
              <span class="prop-value">{{ row.assessment?.total == null ? '-' : $format['usdInt'](row.assessment?.total) }}</span>
            </div>
          </td>
        </tr>
      </table>
    </div>
    <div class="disclaimer ui-text-bolder" v-if="Property.Taxes.dto?.tax_history">
      <p>Data provided by Estated</p>
    </div>
  </div>
  <div class="tab tab-property-history" v-show="activeTab == 'prop-history'">
    <span class="heading" v-if="!Property.History.dto?.prop_history || Property.History.dto.prop_history.length < 1">No Property History Found</span>
    <div class="table-wrapper">
      <table class="prop-list-table" v-if="Property.History.dto?.prop_history">
        <tr v-for="row of Property.History.dto?.prop_history" :key="row">
          <td>
            <div class="point"></div>
          </td>
          <td>
            <div class="prop-block">
              <span class="prop-name">Date</span>
              <span class="prop-value">{{ $format['date'](row.date) }}</span>
            </div>
          </td>
          <td>
            <div class="prop-block">
              <span class="prop-name">Event</span>
              <span class="prop-value">{{ row.event_name }}</span>
            </div>
          </td>
          <td>
            <div class="prop-block">
              <span class="prop-name">Price</span>
              <span class="prop-value ui-text-bolder">{{ $format['usdInt'](row.price) }}</span>
            </div>
          </td>
          <td>
            <div class="prop-block">
              <span class="prop-name">Price Changed</span>
              <span class="prop-value" v-colorBy:posNeg="row.price_changed">{{ $format['usdIntSigned'](row.price_changed) }}</span>
            </div>
          </td>
        </tr>
      </table>
    </div>
    <div class="disclaimer ui-text-bolder" v-if="Property.History.dto?.prop_history">
      <p>Data provided by Estated</p>
    </div>
  </div>
  <div class="tab tab-schools" v-show="activeTab == 'schools'" v-if="!Property.Basis.dto?.data?.is_mls">
    <span class="heading" v-if="!Property.Schools.dto?.schools || Property.Schools.dto.schools.length < 1">No Schools Information Found</span>
    <div class="school-filter flex" v-if="Property.Schools.dto?.schools">
      <URadioChip v-model="schoolType" name="table-school-filter" value="all">All</URadioChip>
      <URadioChip v-model="schoolType" name="table-school-filter" value="elementary">Elementary</URadioChip>
      <URadioChip v-model="schoolType" name="table-school-filter" value="middle">Middle</URadioChip>
    </div>
    <div class="table-wrapper">
      <table class="ui-table ui-table--stripped" v-if="Property.Schools.dto?.schools">
        <tr>
          <th>School</th>
          <th>Type</th>
          <th>Grades</th>
          <th>Distance</th>
          <th>Rating</th>
          <th>Parent Rating</th>
        </tr>
        <tr v-for="row of SchoolsFiltered" :key="row">
          <td>{{ row.name }}</td>
          <td>{{ row.funding_type }}</td>
          <td>{{ row.grades?.range?.low + '-' + row.grades?.range?.hight }}</td>
          <td>{{ row.distance_in_miles }}mi</td>
          <td class="rating"><span v-colorBy:tenPointRating="row.ratings.great_schools_rating" v-text="row.ratings.great_schools_rating || '-'"></span>{{ row.ratings.great_schools_rating ? '/10' : '' }}</td>
          <td>
            <UIcon name="star" :class="{ active: star <= row.ratings.parent_rating }" v-for="star of 5" :key="star"/>
          </td>
        </tr>
      </table>
    </div>
    <div class="disclaimer ui-text-bolder" v-if="Property.Schools.dto?.schools">
      <p>Data provided by Estated</p>
    </div>
  </div>
  <div class="disclaimer">
    <p>
      All returns, cash flow, and appreciation estimates are projections. The information contained in this listing has not been verified by Ofirio.<br>All information should be verified by the buyer. Please review our <router-link class="ui-href ui-href-underline ui-href-dark" :to="{ name: 'static-terms-and-conditions' }">Terms of Use</router-link> for more information.<br>All values are rounded to the nearest dollar.
    </p>
  </div>
</div>


<UPopup ref="customizationPopup" class="popup-customization">
  <div class="content">
    <div class="header ui-grid-triple-spread">
      <div>
        <UButton class="ui-btn-text-gray" @click="resetCustomization('all')">Reset</UButton>
      </div>
      <div>
        <span class="title ui-text-boldest">More Parameters</span>
      </div>
      <div>
        <UIcon name="cross" @click="() => $refs.customizationPopup.close()" />
      </div>
    </div>
    <div class="customization-params-sides">
      <div class="collapsible-wrapper">
        <UCollapsible label="Expenses" opened>
          <div class="flex">

            <div class="side">
              <div class="input-group flex">
                <UTooltip :mode="$isMobile.value ? 'top' : 'right'" :text="TooltipTexts['rental_income']" />
                <span class="label">Monthly Rent</span>
                <UnlockAnalytics v-if="!Account.Basis.isPremium" mode="simple">Unlock</UnlockAnalytics>
                <UTextInput v-else v-model="customizationParameters.monthly_rent" v-bind="DataModel['estimated_rent'](Property.Basis.dto)" :debounce="1000" :formatter="$format['usdInt']" validationMessageShow>
                  <template v-slot:validation="{ message }">
                    <teleport v-if="message" :to="$refs['data-customizationPopup-validator-monthly_rent']">
                      <span class="ui-input-validation-error ui-text-right" v-show="message" v-text="message"></span>
                    </teleport>
                  </template>
                </UTextInput>
              </div>
              <div ref="data-customizationPopup-validator-monthly_rent"></div>
              <div class="input-group flex">
                <UTooltip :mode="$isMobile.value ? 'top' : 'right'" :text="TooltipTexts['property_taxes']" />
                <span class="label">Monthly Property Taxes</span>
                <UnlockAnalytics v-if="!Account.Basis.isPremium" mode="simple">Unlock</UnlockAnalytics>
                <UTextInput v-else v-model="customizationParameters.property_taxes" v-bind="DataModel['property_taxes']" :debounce="1000" :formatter="$format['usdInt']" validationMessageShow>
                  <template v-slot:validation="{ message }">
                    <teleport v-if="message" :to="$refs['data-customizationPopup-validator-property_taxes']">
                      <span class="ui-input-validation-error ui-text-right" v-show="message" v-text="message"></span>
                    </teleport>
                  </template>
                </UTextInput>
              </div>
              <div ref="data-customizationPopup-validator-property_taxes"></div>
              <div class="input-group flex">
                <UTooltip :mode="$isMobile.value ? 'top' : 'right'" :text="TooltipTexts['insurance']" />
                <span class="label">Monthly Insurance</span>
                <UnlockAnalytics v-if="!Account.Basis.isPremium" mode="simple">Unlock</UnlockAnalytics>
                <UTextInput v-else v-model="customizationParameters.insurance" v-bind="DataModel['insurance']" :debounce="1000" :formatter="$format['usdInt']" validationMessageShow>
                  <template v-slot:validation="{ message }">
                    <teleport v-if="message" :to="$refs['data-customizationPopup-validator-insurance']">
                      <span class="ui-input-validation-error ui-text-right" v-show="message" v-text="message"></span>
                    </teleport>
                  </template>
                </UTextInput>
              </div>
              <div ref="data-customizationPopup-validator-insurance"></div>
            </div>
            <div class="side">
              <div class="input-group flex">
                <UTooltip :mode="$isMobile.value ? 'top' : 'right'" :text="TooltipTexts['hqa_fees']" />
                <span class="label">Monthly HOA Fees</span>
                <UnlockAnalytics v-if="!Account.Basis.isPremium" mode="simple">Unlock</UnlockAnalytics>
                <UTextInput v-else v-model="customizationParameters.hoa_fees" v-bind="DataModel['homeowner_assoc']" :debounce="1000" :formatter="$format['usdInt']" validationMessageShow>
                  <template v-slot:validation="{ message }">
                    <teleport v-if="message" :to="$refs['data-customizationPopup-validator-homeowner_assoc']">
                      <span class="ui-input-validation-error ui-text-right" v-show="message" v-text="message"></span>
                    </teleport>
                  </template>
                </UTextInput>
              </div>
              <div ref="data-customizationPopup-validator-homeowner_assoc"></div>
              <div class="input-group flex">
                <UTooltip :mode="$isMobile.value ? 'top' : 'right'" :text="TooltipTexts['agent_leasing_fees']" />
                <span class="label">Agent Leasing Fees</span>
                <UnlockAnalytics v-if="!Account.Basis.isPremium" mode="simple">Unlock</UnlockAnalytics>
                <UTextInput v-else v-model="customizationParameters.release_fees_amount" v-bind="DataModel['agent_leasing_fees']" :debounce="1000" :formatter="$format['usdInt']" validationMessageShow>
                  <template v-slot:validation="{ message }">
                    <teleport v-if="message" :to="$refs['data-customizationPopup-validator-agent_leasing_fees']">
                      <span class="ui-input-validation-error ui-text-right" v-show="message" v-text="message"></span>
                    </teleport>
                  </template>
                </UTextInput>
              </div>
              <div ref="data-customizationPopup-validator-agent_leasing_fees"></div>
            </div>

          </div>
        </UCollapsible>
      </div>
      <div class="collapsible-wrapper">
        <UCollapsible label="Price and Market Related Assumptions" opened>
          <div class="flex">
            <div class="side">
              <div class="input-group flex">
                <UTooltip :mode="$isMobile.value ? 'top' : 'right'" :text="TooltipTexts['annual_increase_in_rent']" />
                <span class="label">Annual Increase In Rent</span>
                <UnlockAnalytics v-if="!Account.Basis.isPremium" mode="simple">Unlock</UnlockAnalytics>
                <UTextInput v-else v-model="customizationParameters.annual_increase_rent" v-bind="DataModel['annual_increase_in_rent']" :debounce="1000" subtype="percent" :formatter="$format['%']" validationMessageShow>
                  <template v-slot:validation="{ message }">
                    <teleport v-if="message" :to="$refs['data-customizationPopup-validator-annual_increase_in_rent']">
                      <span class="ui-input-validation-error ui-text-right" v-show="message" v-text="message"></span>
                    </teleport>
                  </template>
                </UTextInput>
              </div>
              <div ref="data-customizationPopup-validator-annual_increase_in_rent"></div>
              <div class="input-group flex">
                <UTooltip :mode="$isMobile.value ? 'top' : 'right'" :text="TooltipTexts['annual_increase_in_property_value']" />
                <span class="label">Annual Increase In Property Value</span>
                <UnlockAnalytics v-if="!Account.Basis.isPremium" mode="simple">Unlock</UnlockAnalytics>
                <UTextInput v-else v-model="customizationParameters.annual_increase_prop" v-bind="DataModel['annual_increase_in_prop_value']" :debounce="1000" subtype="percent" :formatter="$format['%']" validationMessageShow>
                  <template v-slot:validation="{ message }">
                    <teleport v-if="message" :to="$refs['data-customizationPopup-validator-annual_increase_in_prop_value']">
                      <span class="ui-input-validation-error ui-text-right" v-show="message" v-text="message"></span>
                    </teleport>
                  </template>
                </UTextInput>
              </div>
              <div ref="data-customizationPopup-validator-annual_increase_in_prop_value"></div>
            </div>
            <div class="side">
              <div class="input-group flex">
                <UTooltip :mode="$isMobile.value ? 'top' : 'right'" :text="TooltipTexts['general_inflation']" />
                <span class="label">General Inflation</span>
                <UnlockAnalytics v-if="!Account.Basis.isPremium" mode="simple">Unlock</UnlockAnalytics>
                <UTextInput v-else v-model="customizationParameters.general_inflation" v-bind="DataModel['general_inflation']" :debounce="1000" subtype="percent" :formatter="$format['%']" validationMessageShow>
                  <template v-slot:validation="{ message }">
                    <teleport v-if="message" :to="$refs['data-customizationPopup-validator-general_inflation']">
                      <span class="ui-input-validation-error ui-text-right" v-show="message" v-text="message"></span>
                    </teleport>
                  </template>
                </UTextInput>
              </div>
              <div ref="data-customizationPopup-validator-general_inflation"></div>
            </div>

          </div>
        </UCollapsible>
      </div>
      <div class="collapsible-wrapper">
        <UCollapsible label="Property Based Assumptions" opened>
          <div class="flex">
            <div class="side">
              <div class="input-group flex">
                <UTooltip :mode="$isMobile.value ? 'top' : 'right'" :text="TooltipTexts['average_length_of_tenant_stay']" />
                <span class="label">Average Length Of Tenant Stay</span>
                <UnlockAnalytics v-if="!Account.Basis.isPremium" mode="simple">Unlock</UnlockAnalytics>
                <UTextInput v-else v-model="customizationParameters.average_length_stay_years" v-bind="DataModel['average_length_of_tenant_stay']" :debounce="1000" validationMessageShow>
                  <template v-slot:validation="{ message }">
                    <teleport v-if="message" :to="$refs['data-customizationPopup-validator-average_length_of_tenant_stay']">
                      <span class="ui-input-validation-error ui-text-right" v-show="message" v-text="message"></span>
                    </teleport>
                  </template>
                </UTextInput>
              </div>
              <div ref="data-customizationPopup-validator-average_length_of_tenant_stay"></div>
              <div class="input-group flex">
                <UTooltip :mode="$isMobile.value ? 'top' : 'right'" :text="TooltipTexts['vacancy']" />
                <span class="label">Vacancy per Year</span>
                <UnlockAnalytics v-if="!Account.Basis.isPremium" mode="simple">Unlock</UnlockAnalytics>
                <UTextInput v-else v-model="customizationParameters.vacancy_per_year_days" v-bind="DataModel['vacancy']" :debounce="1000" validationMessageShow>
                  <template v-slot:validation="{ message }">
                    <teleport v-if="message" :to="$refs['data-customizationPopup-validator-vacancy']">
                      <span class="ui-input-validation-error ui-text-right" v-show="message" v-text="message"></span>
                    </teleport>
                  </template>
                </UTextInput>
              </div>
              <div ref="data-customizationPopup-validator-vacancy"></div>
              <div class="input-group flex">
                <UTooltip :mode="$isMobile.value ? 'top' : 'right'" :text="TooltipTexts['management_fees']" />
                <span class="label">Management Fees</span>
                <UnlockAnalytics v-if="!Account.Basis.isPremium" mode="simple">Unlock</UnlockAnalytics>
                <UTextInput v-else v-model="customizationParameters.management_fees_percent" v-bind="DataModel['management_fees']" :debounce="1000" subtype="percent" :formatter="$format['%']" validationMessageShow>
                  <template v-slot:validation="{ message }">
                    <teleport v-if="message" :to="$refs['data-customizationPopup-validator-management_fees']">
                      <span class="ui-input-validation-error ui-text-right" v-show="message" v-text="message"></span>
                    </teleport>
                  </template>
                </UTextInput>
              </div>
              <div ref="data-customizationPopup-validator-management_fees"></div>
              <div class="input-group flex">
                <UTooltip :mode="$isMobile.value ? 'top' : 'right'" :text="TooltipTexts['maintenance_reserves']" />
                <span class="label">Maintenance / Reserves</span>
                <UnlockAnalytics v-if="!Account.Basis.isPremium" mode="simple">Unlock</UnlockAnalytics>
                <UTextInput v-else v-model="customizationParameters.maintenance_cost_amount" v-bind="DataModel['maintenance_reserves']" :debounce="1000" :formatter="$format['usdInt']" validationMessageShow>
                  <template v-slot:validation="{ message }">
                    <teleport v-if="message" :to="$refs['data-customizationPopup-validator-maintenance_reserves']">
                      <span class="ui-input-validation-error ui-text-right" v-show="message" v-text="message"></span>
                    </teleport>
                  </template>
                </UTextInput>
              </div>
              <div ref="data-customizationPopup-validator-maintenance_reserves"></div>
            </div>
            <div class="side">
              <div class="input-group flex">
                <UTooltip :mode="$isMobile.value ? 'top' : 'right'" :text="TooltipTexts['overhead_miscellanous']" />
                <span class="label">Overhead / Miscellanous</span>
                <UnlockAnalytics v-if="!Account.Basis.isPremium" mode="simple">Unlock</UnlockAnalytics>
                <UTextInput v-else v-model="customizationParameters.overhead_cost_amount" v-bind="DataModel['overhead_miscellanous']" :debounce="1000" :formatter="$format['usdInt']" validationMessageShow>
                  <template v-slot:validation="{ message }">
                    <teleport v-if="message" :to="$refs['data-customizationPopup-validator-overhead_miscellanous']">
                      <span class="ui-input-validation-error ui-text-right" v-show="message" v-text="message"></span>
                    </teleport>
                  </template>
                </UTextInput>
              </div>
              <div ref="data-customizationPopup-validator-overhead_miscellanous"></div>
              <div class="input-group flex">
                <UTooltip :mode="$isMobile.value ? 'top' : 'right'" :text="TooltipTexts['closing_costs_on_purchase']" />
                <span class="label">Closing Costs On Purchase</span>
                <UnlockAnalytics v-if="!Account.Basis.isPremium" mode="simple">Unlock</UnlockAnalytics>
                <UTextInput v-else v-model="customizationParameters.closing_cost_on_purchase_percent" v-bind="DataModel['closing_costs_on_purchase']" :debounce="1000" subtype="percent" :formatter="$format['%']" validationMessageShow>
                  <template v-slot:validation="{ message }">
                    <teleport v-if="message" :to="$refs['data-customizationPopup-validator-closing_costs_on_purchase']">
                      <span class="ui-input-validation-error ui-text-right" v-show="message" v-text="message"></span>
                    </teleport>
                  </template>
                </UTextInput>
              </div>
              <div ref="data-customizationPopup-validator-closing_costs_on_purchase"></div>
              <div class="input-group flex">
                <UTooltip :mode="$isMobile.value ? 'top' : 'right'" :text="TooltipTexts['closing_costs_on_sale']" />
                <span class="label">Closing Costs On Sale</span>
                <UnlockAnalytics v-if="!Account.Basis.isPremium" mode="simple">Unlock</UnlockAnalytics>
                <UTextInput v-else v-model="customizationParameters.closing_cost_on_sale_percent" v-bind="DataModel['closing_costs_on_sale']" :debounce="1000" subtype="percent" :formatter="$format['%']" validationMessageShow>
                  <template v-slot:validation="{ message }">
                    <teleport v-if="message" :to="$refs['data-customizationPopup-validator-closing_costs_on_sale']">
                      <span class="ui-input-validation-error ui-text-right" v-show="message" v-text="message"></span>
                    </teleport>
                  </template>
                </UTextInput>
              </div>
              <div ref="data-customizationPopup-validator-closing_costs_on_sale"></div>
            </div>
          </div>
        </UCollapsible>
      </div>
      <div class="collapsible-wrapper">
        <UCollapsible label="Mortgage Calculation" opened>
          <div class="flex">
            <div class="side">
              <div class="input-group flex">
                <UTooltip :mode="$isMobile.value ? 'top' : 'right'" :text="TooltipTexts['interest_rate']" />
                <span class="label">Interest Rate</span>
                <UnlockAnalytics v-if="!Account.Basis.isPremium" mode="simple">Unlock</UnlockAnalytics>
                <UTextInput v-else v-model="customizationParameters.interest_rate" v-bind="DataModel['interest_rate'](Property.Basis.dto)" :debounce="1000" subtype="percent" :formatter="$format['%']" validationMessageShow>
                  <template v-slot:validation="{ message }">
                    <teleport v-if="message" :to="$refs['data-customizationPopup-validator-interest_rate']">
                      <span class="ui-input-validation-error ui-text-right" v-show="message" v-text="message"></span>
                    </teleport>
                  </template>
                </UTextInput>
              </div>
              <div ref="data-customizationPopup-validator-interest_rate"></div>
              <div class="input-group flex">
                <UTooltip :mode="$isMobile.value ? 'top' : 'right'" :text="TooltipTexts['down_payment']" />
                <span class="label">Down Payment (%)</span>
                <UnlockAnalytics v-if="!Account.Basis.isPremium" mode="simple">Unlock</UnlockAnalytics>
                <UTextInput v-else v-model="customizationParameters.down_payment" v-bind="DataModel['down_payment'](Property.Basis.dto)" :debounce="1000" subtype="percent" :decimals="0" :formatter="$format['%Int']" validationMessageShow>
                  <template v-slot:validation="{ message }">
                    <teleport v-if="message" :to="$refs['data-customizationPopup-validator-down_payment']">
                      <span class="ui-input-validation-error ui-text-right" v-show="message" v-text="message"></span>
                    </teleport>
                  </template>
                </UTextInput>
              </div>
              <div ref="data-customizationPopup-validator-down_payment"></div>
              <div class="input-group flex">
                <UTooltip :mode="$isMobile.value ? 'top' : 'right'" :text="TooltipTexts['loan_term']" />
                <span class="label">Loan Term</span>
                <UnlockAnalytics v-if="!Account.Basis.isPremium" mode="simple">Unlock</UnlockAnalytics>
                <UTextInput v-else v-model="customizationParameters.financing_years" v-bind="DataModel['financing_years'](Property.Basis.dto)" :debounce="1000" validationMessageShow>
                  <template v-slot:validation="{ message }">
                    <teleport v-if="message" :to="$refs['data-customizationPopup-validator-financing_years']">
                      <span class="ui-input-validation-error ui-text-right" v-show="message" v-text="message"></span>
                    </teleport>
                  </template>
                </UTextInput>
              </div>
              <div ref="data-customizationPopup-validator-financing_years"></div>
            </div>
            <div class="side">
              <UnlockAnalytics v-if="!Account.Basis.isPremium">Unlock</UnlockAnalytics>
              <div class="input-group flex readonly">
                <UTooltip :mode="$isMobile.value ? 'top' : 'right'" :text="TooltipTexts['loan_amount']" />
                <span class="label">Loan Amount</span>
                <span v-if="Account.Basis.isPremium" class="value">{{ $format['usdInt'](Property.Finance.dto?.performance.loan_value) }}</span>
              </div>
              <div class="input-group flex readonly">
                <UTooltip :mode="$isMobile.value ? 'top' : 'right'" :text="TooltipTexts['annual_payment']" />
                <span class="label">Annual Payment</span>
                <span v-if="Account.Basis.isPremium" class="value">{{ $format['usdInt'](Property.Finance.dto?.monthly_cash_flow.month_loan_payments * 12) }}</span>
              </div>
              <div class="input-group flex readonly">
                <UTooltip :mode="$isMobile.value ? 'top' : 'right'" :text="TooltipTexts['monthly_payment']" />
                <span class="label">Monthly Payment</span>
                <span v-if="Account.Basis.isPremium" class="value">{{ $format['usdInt'](Property.Finance.dto?.monthly_cash_flow.month_loan_payments) }}</span>
              </div>
            </div>
          </div>
        </UCollapsible>
      </div>
      <div class="collapsible-wrapper">
        <UCollapsible label="Basic Purchase Information" opened>
          <div class="flex">
            <div class="side">
              <div class="input-group flex">
                <UTooltip :mode="$isMobile.value ? 'top' : 'right'" :text="TooltipTexts['purchase_price']" />
                <span class="label">Purchase Price</span>
                <UnlockAnalytics v-if="!Account.Basis.isPremium" mode="simple">Unlock</UnlockAnalytics>
                <UTextInput v-else v-model="customizationParameters.price" v-bind="DataModel['purchase_price'](Property.Basis.dto?.data.price)" :debounce="1000" :formatter="$format['usdInt']" validationMessageShow>
                  <template v-slot:validation="{ message }">
                    <teleport v-if="message" :to="$refs['data-customizationPopup-validator-purchase_price']">
                      <span class="ui-input-validation-error ui-text-right" v-show="message" v-text="message"></span>
                    </teleport>
                  </template>
                </UTextInput>
              </div>
              <div ref="data-customizationPopup-validator-purchase_price"></div>
            </div>
            <div class="side">
              <UnlockAnalytics v-if="!Account.Basis.isPremium">Unlock</UnlockAnalytics>
              <div class="input-group flex readonly">
                <UTooltip :mode="$isMobile.value ? 'top' : 'right'" :text="TooltipTexts['down_payment']" />
                <span class="label">Down Payment ({{ $format['%'](Property.Finance.dto?.base.down_payment) }})</span>
                <span v-if="Account.Basis.isPremium" class="value">{{ $format['usdInt'](Property.Finance.dto?.performance.equity_investment) }}</span>
              </div>
              <div class="input-group flex readonly">
                <UTooltip :mode="$isMobile.value ? 'top' : 'right'" :text="TooltipTexts['down_payment']" />
                <span class="label">Equity at Purchase</span>
                <span v-if="Account.Basis.isPremium" class="value">{{ $format['usdInt'](Property.Finance.dto?.performance.equity_investment) }}</span>
              </div>
            </div>
          </div>
        </UCollapsible>
      </div>

      <div class="flex customization-popup-summary">
        <div class="side">
          <span class="title">Performance</span>
          <UnlockAnalytics class="hidden" v-if="!Account.Basis.isPremium">Unlock</UnlockAnalytics>
          <div class="input-group flex readonly">
            <UTooltip :mode="$isMobile.value ? 'top' : 'right'" :text="TooltipTexts['cap_rate']" />
            <span class="label">Cap Rate</span>
            <span v-if="Account.Basis.isPremium" class="value" v-colorBy:cap-coc="Property.Finance.dto?.performance.cap_rate_year1">{{ $format['%'](Property.Finance.dto?.performance.cap_rate_year1) }}</span>
          </div>
          <div class="input-group flex readonly">
            <UTooltip :mode="$isMobile.value ? 'top' : 'right'" :text="TooltipTexts['cash_on_cash']" />
            <span class="label">Cash on Cash</span>
            <span v-if="Account.Basis.isPremium" class="value" v-colorBy:cap-coc="Property.Finance.dto?.performance.cash_on_cash_year1">{{ $format['%'](Property.Finance.dto?.performance.cash_on_cash_year1) }}</span>
          </div>
          <div class="input-group flex readonly">
            <UTooltip :mode="$isMobile.value ? 'top' : 'right'" :text="TooltipTexts['total_return']" />
            <span class="label">Total Return</span>
            <span v-if="Account.Basis.isPremium" class="value">{{ $format['%'](Property.Finance.dto?.main_results.total_return) }}</span>
          </div>
        </div>
        <div class="side">
          <div class="summary">
            <UnlockAnalytics class="hidden" v-if="!Account.Basis.isPremium">Unlock</UnlockAnalytics>
            <div class="summary-row flex">
              <span class="summary-row-title">Down Payment ({{ $format['%'](Property.Finance.dto?.base.down_payment) }})</span>
              <span v-if="Account.Basis.isPremium" class="summary-row-value ui-text-bolder">{{ $format['usdInt'](Property.Finance.dto?.performance.equity_investment) }}</span>
            </div>
            <div class="summary-row flex">
              <span class="summary-row-title">Closing Costs {{ Property.Finance.dto?.detailed.closing_cost_on_purchase_percent ? `(${$format['%'](Property.Finance.dto?.detailed.closing_cost_on_purchase_percent)})` : '' }}</span>
              <span v-if="Account.Basis.isPremium" class="summary-row-value ui-text-bolder">{{ $format['usdInt'](Property.Finance.dto?.main_results.closing_costs) }}</span>
            </div>
            <div class="divider"></div>
            <span class="summary-row summary-row-total flex ui-text-bold">
              <span class="summary-row-title">Out of Pocket Costs</span>
              <span v-if="Account.Basis.isPremium" class="summary-row-value">{{ $format['usdInt'](Property.Finance.dto?.main_results.total_cash_needed) }}</span>
            </span>
          </div>
        </div>
      </div>

    </div>
    <div class="footer">
      <UButton class="ui-btn ui-btn-green flex" @click="() => $refs.customizationPopup.close()"><UIcon name="checked" />&nbsp;Apply Changes</UButton>
    </div>
  </div>
</UPopup>

<UPopup ref="imagesPopup" class="popup-images">
  <UIcon name="cross" @click="() => $refs.imagesPopup.close()" />
  <div class="content" @click.stop="close">
    <div class="controls flex">
      <UIcon name="list" :class="{ active: photosStyle == 'list' }" @click="photosStyle = 'list'" />
      <UIcon name="grid" :class="{ active: photosStyle == 'grid' }" @click="photosStyle = 'grid'" />
    </div>
    <div class="popup-images-list" ref="imagesWrapper"> 
      <div class="wrapper" :class="[photosStyle]">
        <div class="img-aspect-ratio" v-for="imgUrl of Property.Basis.dto?.photos" :key="imgUrl">
          <img :src="imgUrl" alt="Additional photo">
        </div>
      </div>
    </div>
  </div>
</UPopup>

<Footer />
</template>

<style lang="less" scoped>
.property {
  margin: 20px auto;
  padding-bottom: 70px;

  @media @mobile {
    &, .wrapper { max-width: none; }
  }
  &::v-deep .ui-slider.monthly-rate-slider {
    .slider-base {
      background: linear-gradient(90deg, #E4E4E4 16.67%, #01D092 46.88%, #01D092 53.65%, #E4E4E4 84.38%);
    }
    .slider-connect { background: transparent; }
  }
  > .top-bar {
    @tabs-height: 50px;

    height: @header-height;

    @media @mobile {
      height: auto;
      min-height: 2*@header-height-mobile;
    }
    
    .heading-row {
      height: inherit;
      background: @col-bg;
      z-index: 1001;

      &.sticked {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        box-shadow: 0 1px 12px @col-shadow;

        @media @mobile {
          .hide-mobile-sticked { display: none; }

          &.scrollingUp {
            top: @header-height-mobile;
            z-index: 999;
          }
        }
        > .header-bar {
          height: @header-height;
          
          @media @mobile {
            height: @header-height-mobile;
            justify-content: space-between;
            flex-direction: row;
            align-content: center;
            align-items: center;
          }
          .address::v-deep {
            display: block;

            @media @mobile { display: none; }

            span {
              display: block;
              margin: .5rem 0;
            }
            .street { font-size: 1rem; }
            .location { font-size: .875rem; }
            .label { display: none; }
            .svg-icon { display: none; }
          }
          > .small-props {
            display: flex;
            justify-content: flex-start;
            align-items: flex-start;

            .hidden {
              margin: 0 16px;

              .unlock-analytics {
                font-size: 0.875rem;
                margin-bottom: 5px;
                padding: 0;
                justify-content: flex-start;
                flex-wrap: nowrap;


                @media @mobile { font-size: 1rem; }
                &::v-deep {
                  .svg-icon {
                    width: 1.125rem;
                    height: 1.125rem;

                    @media @mobile {
                      width: 1.14rem;
                      height: 1.14rem;
                    }
                  }
                  .ui-href {
                    line-height: 1rem; 
                    text-decoration: underline;
                    padding: 0 0 0 6px;
                  }
                }
              }
              > span {
                display: block;
                font-size: 0.675rem;
                font-weight: 700;
                color: @col-text-gray-darker;
                text-transform: uppercase;
              }
            }
            @media @mobile {
              justify-content: flex-start;
              width: 100%;

              .ui-small-prop {
                margin: 0 @mm/2;

                &:first-child { margin-left: @mm; }
                &:last-child { margin-right: @mm; }
              }
              &::v-deep {
                span.value { font-size: 1.14rem; }
                span.title { font-size: .75rem; }
              }
            }
          }
          .prop-actions {
            @media @mobile {
              width: auto;
              margin: 0 @mm;
              flex-shrink: 0;

              .mobile-mm, .ui-drop, .ui-button { display: none; }
              &::v-deep .ui-property-favorite-icon {
                @s: 24px;

                display: block;
                width: @s;
                min-width: @s;
                height: @s;
                min-height: @s;
              }
            }
          }
        }
      }
      &.sticked-full {
        height: auto;

        > .ui-divider { display: block; }
        > .tabs {
          display: flex;

          @media @mobile {
            width: 100%;
            overflow-x: auto;

            .ui-radio-chip {
              flex-shrink: 0;
              padding: 0 15px;
            }
          }
        }
      }
      &::v-deep .ui-property-favorite-icon {
        fill: transparent;
        stroke: @col-text-gray-darker;

        &.active {
          fill: @col-blue;
          stroke: @col-blue;
        }
      }
      > .header-bar {
        height: inherit;
        justify-content: space-between;
        align-content: center;
        align-items: center;

        @media @mobile {
          flex-direction: column;
          justify-content: flex-start;
          align-content: flex-start;
          align-items: flex-start;
        }
        .address {
          justify-content: flex-start;
          flex-wrap: wrap;
          align-items: center;
          align-content: flex-start;

          @media @mobile { padding: 0 @mm;}
          span {
            margin-right: 1rem;
            vertical-align: baseline;

            @media @mobile {
              display: block;
              margin: 0;
            }
          }
          .street, .location { cursor: pointer; }
          .street {
            font-weight: 700;
            font-size: 2rem;
            margin-right: 0;
            margin-bottom: 10px;
            display: block;
            width: 100%;

            @media @mobile {
              font-size: 1.7rem;
              margin-bottom: 5px;
            }
          }
          .location {
            font-weight: 600;
            font-size: 1.125rem;
            color: @col-text-gray-darker;

            @media @mobile {
              display: inline-block;
              font-size: 1.07rem;
              margin-top: 5px;
            }
          }
          .label {
            @media @mobile {
              margin-top: 5px;
              display: inline-block;
            }
          }
        }
        .prop-actions {
          justify-content: flex-end;
          align-items: stretch;
          align-content: stretch;

          @media @mobile {
            margin: @mm 0;
            width: 100%;
            overflow-x: auto;
            justify-content: flex-start;
            align-items: center;
            align-content: center;
          }
          &::v-deep .ui-drop-label {
            box-shadow: none;
            display: block;
            color: @col-text-gray-dark;
          }
          &::v-deep .ui-drop.opened .ui-drop-label {
            background: transparent;
            color: @col-text-dark;
          }
          &::v-deep .ui-drop-container {
            z-index: 5;
            padding: 20px;

            @media @mobile { padding: 0; }
            .heading {
              font-weight: 700;
              margin-bottom: .5rem;
            }
          }
          .ui-btn-text-gray,
          &::v-deep .ui-drop-label {
            font-weight: 500;
            margin-left: 1rem;
            text-align: center;
            font-size: 0.75rem;
            line-height: 1rem;
            height: auto;
            padding: 0 .5rem;

            @media @mobile {
              display: flex;
              justify-content: flex-start;
              align-items: center;
              align-content: center;
              white-space: nowrap;
              height: 36px;
              line-height: 36px;
              font-weight: 700;
              padding: 10px;
              border-radius: 18px;
              color: @col-text-dark;
              border: 1px solid @col-gray;
              margin: 0 8px 0 0;

              &:hover, &:focus, &:active { background: lighten(@col-gray, 4%); }
            }
            .svg-icon {
              @s: 21px;

              width: @s;
              height: @s;
              display: block;
              margin: 0 auto .5rem;

              @media @mobile {
                @s: 16px;

                margin: 0 10px 0 0;
                width: @s;
                height: @s;
              }
            }
          }
          > .mobile-mm:last-child {
            width: @mm - 8px;
            min-width: @mm - 8px;
          }
          @media @mobile {
            &::v-deep .ui-property-favorite-icon { display: none; }
          }
        }
      }
      > .ui-divider {
        display: none;
        margin: 0 auto;
      }
      > .tabs {
        display: none;
        height: @tabs-height;
        justify-content: flex-start;
        align-items: stretch;

        .ui-radio-chip {
          border-radius: 0;
          border-bottom: 3px solid transparent;
          background: transparent;
          box-shadow: none;
          color: @col-text-gray-darker;
          height: @tabs-height;
          line-height: @tabs-height;
          font-weight: 700;
          font-size: 1rem;
          padding: 0 1.5rem;

          &.selected {
            color: @col-text-dark;
            border-bottom-color: @col-text-dark;
          }
        }
      }
      .small-props {
        justify-content: center;
        align-items: center;
        display: none;

        .ui-small-prop {
          margin: 0 1rem;

          &::v-deep {
            span.label { font-size: 0.675rem }
            span.value { font-size: 1.125rem }
          }
        }
      }
    }
  }
  .ui-divider {
    margin: .5rem 0;

    @media @mobile { margin: @mm 0; }
  }
  > .basic-info {
    justify-content: space-between;
    align-content: flex-start;
    align-items: flex-start;

    @media @mobile { display: block; }
    span { display: block; }
    > .ui-preloader { margin-right: 2.5rem; }
    > .images {
      width: 55%;
      margin-right: 2.5rem;

      .label-block {
        position: absolute;
        top: 10px;
        left: 10px;

        .label { margin: 0 6px 0 0; }
      }
    }
    > .images-mobile {
      @h: 230px;

      margin-bottom: @mm;
      position: relative;      

      &::v-deep {
        img {
          height: @h;
          object-fit: cover;
        }
        .swiper-pagination-bullet {
          background: @col-bg;
          opacity: 1;
          box-shadow: 0px 2px 4px rgba(0, 0, 0, 0.25);
        }
        .swiper-pagination-bullet-active { background: @col-green; }
      }
      .image-placeholder {
        width: 100%;
        height: @h;
        object-fit: contain;
        padding: 20% 0;
        background: @col-gray-light;
      }
      .label-block {
        position: absolute;
        top: 10px;
        left: 10px;
        z-index: 1;

        .label { margin: 0 6px 0 0; }
      }
      &::v-deep .ui-property-favorite-icon {
        position: absolute;
        top: 10px;
        right: 10px;
        z-index: 1;
      }
    }
    > .info {
      flex: 1;

      @media @mobile { padding: 0 @mm; }
      .ui-divider { margin: 2rem 0; }
      .chars-row {
        justify-content: flex-start;
        align-content: flex-start;
        align-items: flex-start;
        margin-bottom: @mm;

        .char {
          white-space: nowrap;

          .title {
            font-size: .875rem;
            color: @col-text-gray-dark;

            @media @mobile { font-size: 1rem; }
          }
          .value {
            font-size: 1.5rem;
            font-weight: 700;
            margin-top: .5rem;

            @media @mobile { font-size: 1.285rem; }
          }

          & + .char {
            margin-left: 2rem;

            @media @mobile { margin-left: @mm; }
          }
          @media screen and (max-width: 370px) {
            &.hide-mobile-small { display: none }
          }
        }
      }
      .slider {
        margin: 2rem 0;

        @media @mobile { margin: @mm 0 36px; }
        .slider-info {
          justify-content: space-between;
          margin-bottom: 1rem;

          > .title {
            color: @col-text-gray-darker;
            display: flex;
            flex-wrap: nowrap;
            justify-content: flex-start;
            align-content: center;
            align-items: center;

            @media @mobile { font-size: 1.14rem; }
            .ui-tooltip { margin-right: 5px; }
          }
          > .value { font-weight: 700; }
          .unlock-analytics {
            justify-content: flex-start;
            padding: 0;
          }
        }
        .ui-slider { width: 100%; }

        &.slider-estimated-rent {
          position: relative;

          > .slider-info img {
            position: absolute;
            top: 0;
            left: 50%;
            transform: translateX(-50%);
            height: 1.125rem;
            width: auto;
            object-fit: fill;

            @media @mobile {
              position: static;
              transform: none;
              // svg width workaround
              width: 100px;
            }
          }
        }
      }
      .estimated-prediction-quality {
        justify-content: flex-start;
        align-items: center;
        margin-top: 2rem;

        > .title {
          color: @col-text-gray-darker;
          display: flex;
          flex-wrap: nowrap;
          justify-content: flex-start;
          align-content: center;
          align-items: center;
          flex-shrink: 0;

          @media @mobile { font-size: 1.14rem; }
          .ui-tooltip { margin-right: 5px; }
        }
        > .bar {
          @h: 5px;

          flex: 1;
          height: @h;
          overflow: hidden;
          border-radius: @h/2;
          background: @col-gray-light;
          color: transparent;
          user-select: none;
          margin: 0 25px;

          &.quality-low { background: linear-gradient(270deg, #E4E4E4 89.58%, #01D193 100%); }
          &.quality-medium { background: linear-gradient(270deg, #E4E4E4 46.87%, #01D193 100%); }
          &.quality-high { background: linear-gradient(270deg, #E4E4E4 0%, #01D193 48.96%); }

          @media @mobile {
            order: 1;
            width: 100%;
            margin: 16px 0 0;
            flex-basis: 100%;
          }
        }
        > .value {
          font-weight: 700;

          &.quality-low { color: @col-text-gray-darker; }
          &.quality-medium { color: @col-green-light }
          &.quality-high { color: @col-green }
        }
        .unlock-analytics {
          justify-content: flex-start;
          padding: 0;
        }
        @media @mobile {
          justify-content: space-between;
          flex-wrap: wrap;
        } 
      }
      .fifty-five-community {
        background: rgba(255, 153, 0, 0.1);
        border-radius: @border-radius;
        margin-bottom: 20px;

        &::v-deep .ui-collapsible {
          padding: 20px;          

          .header {
            cursor: pointer;

            > .flex { justify-content: space-between; }
            .svg-icon--smooth-arrow {
              transform: rotate(180deg);
              transition: transform ease 0.2s;
              width: 14px;
              height: 14px;
            }
            span {
              vertical-align: middle;
              font-weight: 700;

              .svg-icon { 
                width: 22px;
                height: 22px;
                margin-right: 12px;
              }  
            }
            .svg-icon { vertical-align: middle; }
          }
          .container {
            span {
              font-weight: 400;
              line-height: 1.375rem;
              color: @col-text-gray-dark;
              margin-top: 20px;
            }
          }
          @media @mobile { padding: 12px 15px; }
        }
      }
      .fin-table .unlock-analytics {
        justify-content: flex-start;
        padding: 0 0 0.5rem 0;
        flex-wrap: nowrap;
      }
    }
  }
  > .tabs {
    justify-content: flex-start;
    align-content: stretch;
    margin: 50px 0;
    position: relative;

    @media @mobile {
      margin: 50px 0 30px;
      width: 100%;
      overflow-x: auto;
    }
    &:before {
      @h: 1px;

      content: '';
      position: absolute;
      display: block;
      bottom: 0;
      left: 0;
      height: @h;
      width: 100%;
      background: @col-gray;
    }
    .ui-radio-chip {
      box-shadow: none;
      border-radius: 0;
      height: auto;
      padding: .5rem 1.5rem;
      text-align: center;
      font-weight: 700;
      border-bottom: 3px solid transparent;
      margin: 0;
      flex-shrink: 0;
      line-height: 1rem;

      @media @mobile {
        padding: 0 1rem 12px;
        font-size: 1.14rem;
        line-height: 1.25rem;
      }
      .svg-icon {
        @s: 2rem;

        display: block;
        width: @s;
        height: @s;
        margin: 0 auto 10px;
      }
      .tab-name { font-size: 1rem; }
      &.selected {
        background: transparent;
        border-bottom-color: @col-text-dark;
        color: @col-text-dark;
      }
    }
  }
  > .tab {
    span.heading {
      display: block;
      font-size: 1.5rem;
      font-weight: 700;
      margin-bottom: 1.25rem;

      @media @mobile { padding: 0 @mm; }
    }
    @media @mobile {
      .table-wrapper {
        padding: 0 @mm;
        width: 100%;
        overflow-x: auto;
      }
    }
  }
  .tab-summary {

    @media @mobile { padding: 0 @mm; }

    .sided-info {
      justify-content: space-between;
      align-content: flex-start;
      align-items: flex-start;

      @media @mobile { display: block; }
      .text-side {
        flex: 1;
        margin-right: 2.5rem;

        @media @mobile { margin-right: 0; }
        .description {
          font-weight: 400;
          line-height: 1.75rem;
          margin-bottom: 40px;

          @media @mobile {
            margin: 30px 0;
            line-height: 1.5rem;
          }
        }
        .call-agents {
          padding: 0 2.5rem;
          height: 46px;
          margin: 40px 0;
          display: block;

          @media @mobile {
            width: 100%;
            margin: 30px 0;
          }
        }
      }
      .location {
        width: 40%;
        padding-bottom: 20%;
        position: relative;

        @media @mobile {
          width: 100%;
          padding-bottom: 100%;
          margin-top: 30px;
        }
        > .map {
          position: absolute;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          border-radius: @border-radius;
          overflow: hidden;

          .google-map {
            &, &::v-deep > div {
              width: 100%;
              height: 100%;
            }
          }
        }
      }
    }
    .additional-info {
      .ui-property-feature-block { margin-top: 30px; }
    }
  }
  .tab-financial {
    .params {
      @h: 60px;

      margin: 1.25rem 0 2rem;
      justify-content: space-between;
      align-content: stretch;
      align-items: stretch;


      @media @mobile {
        padding: 0 @mm;
        display: grid;
        grid-template-rows: repeat(1fr);
        grid-template-columns: 1fr 1fr;
        gap: 10px 10px;
      }
      @media @desktop {
        .ui-drop + .ui-drop,
        .ui-drop + .ui-btn { margin-left: 1rem; }
      }
      .ui-drop, > .ui-btn { flex: 1; }

      > .ui-btn {
        height: @h;
        font-weight: 700;
        justify-content: center;
        align-items: center;

        &:focus, &:active { border-color: @col-text-dark; }
        .svg-icon {
          @s: 1.25rem;

          width: @s;
          height: @s;
          margin-right: .5rem;
        }
      }
      &::v-deep .ui-drop {
        .ui-drop-label  {
          justify-content: space-between;
          align-content: center;
          align-items: center;
          padding: 10px 15px;
          cursor: pointer;
          width: 100%;
          height: @h;
        }
        .ui-drop-container {
          @media @desktop {
            z-index: 5;
            top: @h + 20px;
            padding: 20px;
            min-width: 340px;
          }
        }
        @media @mobile {
          .padder { padding: 0 @mm; }
        }
        @media @desktop and (max-width: 1400px) {
          &:first-child .ui-drop-container,
          &:last-child .ui-drop-container { transform: none; }
          &:first-child .ui-drop-container { left: 0; }
          &:last-child .ui-drop-container { right: 0; }
        }
      }
      .ui-drop .ui-drop-label {
        .svg-icon { margin: 0 0 0 10px; }
        .param-data {
          span {
            display: block;
            white-space: nowrap;
            height: auto;
            line-height: 1.2rem;
          }
          .param-name {
            color: @col-text-gray-dark;
            font-size: .875rem;
            margin-bottom: 5px;
          }
          .param-value {
            font-weight: 700;
          }
          .unlock-analytics::v-deep {
            justify-content: flex-start;
            padding: 0;
            @s: 1.2rem;

            .svg-icon {
              width: @s;
              height: @s;
            }
            .ui-href { line-height: @s; }
          }
        }
      }
    }
    .fin-details {
      justify-content: space-between;
      align-content: stretch;
      align-content: stretch;
      flex-wrap: wrap;
    }
    .full-pro-forma {
      margin-top: 50px;

      .head-row {
        justify-content: flex-start;
        align-content: center;
        align-items: center;
        margin-bottom: 1rem;

        @media @mobile {
          margin-bottom: @mm;
          justify-content: space-between;
          white-space: nowrap;
          padding: 0 @mm;
        }
        .heading {
          margin: 0;

          @media @mobile { padding: 0; }
        }
        .ui-btn {
          margin-left: 1rem;

          @media @mobile {
            margin: 0;
            padding-left: 10px;
            padding-right: 10px;
          }
          .svg-icon {
            @s: 20px;
            
            width: @s;
            height: @s;
            vertical-align: middle;
            margin: 0 .5rem 0 0;
          }
        }
      }
      .slide-to-more-years {
        @s: 14px;
        padding: 0 20px;
        margin: 20px 0;
        text-align: end;

        span {
          font-size: 0.875rem;
          color: @col-text-gray-darker;
          margin-right: 6px;
        }
        .svg-icon {
          width: @s;
          height: @s;
          fill: @col-text-gray-darker;
          vertical-align: middle;
        }
      }
      .fin-table td { padding: 10px 20px; }
      .fin-table {
        position: relative;
        
        .unlock-analytics {
          position: absolute;
          right: 0;
          top: 40px;
          width: 70%;
          height: calc(100% - 40px);
          z-index: 1;

          @media @mobile { width: 30%; }
        }
      }
    }
    .property-financial-plots {
      .plot-item {
        margin-top: 40px;
        justify-content: flex-start;
        align-items: flex-start;

        @media @mobile {
          margin-top: @mm;
          flex-direction: column;
          padding: 0 @mm;
        }
        .side-data {
          width: 20%;
          max-width: 205px;
          border-radius: @border-radius;
          border: 1px solid @col-gray-light;
          margin-right: 40px;

          @media @mobile {
            width: 100%;
            max-width: none;
            order: 2;
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 0;
            margin-top: @mm;
          }
          .unlock-analytics {
            justify-content: flex-start;
            padding: 0;
            margin-bottom: 10px;
          }
          .data-row {
            padding: 20px;
            font-weight: 700;

            @media @desktop {
              & + .data-row { border-top: 1px solid @col-gray-light; }
            }
            @media @mobile {
              &:nth-child(2n) { border-left: 1px solid @col-gray-light; }
              &:nth-child(n+3) { border-top: 1px solid @col-gray-light; }
            }
            .value {
              font-size: 1.375rem;
              margin-bottom: 5px;
              display: block;
            }
            .description {
              color: #7a7a7a;
              font-size: .75rem;
              line-height: 1rem;
              text-transform: uppercase;

              .ui-tooltip { margin: 0 2px 0 0; }
            }
          }
        }
        .ui-plot {
          .unlock-analytics { height: 300px; }
          @media @desktop { flex: 1; }
          @media @mobile { width: 100%; }
        }
      }
    }
  }
}
.tab-tax-history {
  > .ui-plot {
    margin-bottom: 40px;

    @media @mobile {
      margin-bottom: @mm;
      padding: 0 @mm;
    }
  }
}
.tab-schools {
  .school-filter {
    width: 100%;
    margin-bottom: 1rem;

    @media @mobile {
      padding: 0 @mm;
      margin-bottom: @mm;
    }
  }
  .ui-table {
    width: 100%;

    .svg-icon--star {
      fill: @col-text-gray-darker;

      &.active { fill: @col-green; }
    }
    .rating {
      font-size: 0.75rem;
      vertical-align: baseline;

      > span {
        font-size: 1rem;
        font-weight: 600;
      }
    }
    td:last-child { white-space: nowrap; }
  }
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
      // background-image: url("data:image/svg+xml,%3csvg width='100%25' height='100%25' xmlns='http://www.w3.org/2000/svg'%3e%3crect width='100%25' height='100%25' fill='none' stroke='%230000001A' stroke-width='1' stroke-dasharray='3%2c 4' stroke-dashoffset='0' stroke-linecap='square'/%3e%3c/svg%3e");
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
}

.prop-list-table {
  @pv: 15px;
  @ph: 10px;
  @ps: 11px;
  @pb: 3px;
  @pshd: 2px;

  width: 100%;
  border-collapse: separate;
  position: relative;

  &:before {
    content: '';
    position: absolute;
    left: @ph - @pb - @pshd - 1px;
    width: 0;
    top: @pv + @pshd;
    bottom: @pv - @pshd;
    border-right: 2px dashed @col-text-gray-darker;
    z-index: 0;
  }
  tr td {
    padding: @pv @ph;
    vertical-align: top;
    white-space: nowrap;
  }
  tr td:first-child {
    padding-left: 0;

    .point {
      width: @ps;
      height: @ps;
      border-radius: 50%;
      border: @pb solid @col-bg;
      background: @col-bg;
      box-shadow: 0 0 0 @pshd @col-text-gray-darker, 0 0 0 @pv @col-bg;
      position: relative;
      z-index: 1;
    }
  }
  tr:first-child td:first-child .point {
    background: @col-text-dark;
    box-shadow: 0 0 0 @pshd @col-text-dark, 0 0 0 @pv @col-bg;
  }
  tr td:last-child { padding-right: 0; }
  tr:last-child td:first-child {
    position: relative;

    .point {
      position: static;

      &:before {
        content: '';
        position: absolute;
        display: block;
        top: @pv + @ps + 2*@pb + 2*@pshd;
        left: 0;
        right: 0;
        bottom: 0;
        background: @col-bg;
      }
    }
  }

  td.operation {
    font-size: 2rem;
    vertical-align: middle;
    text-align: center;
    color: #cbcbcb;
  }
  .prop-block {
    > span { display: block; }
    span.prop-name {
      font-size: .875rem;
      color: @col-text-gray-darker;
      margin-bottom: 10px;
    }
    span.smaller { font-size: .875rem; }
  }
}
.popup-customization {
  > .content {
    @rh: 50px;

    width: 100%;

    @media @mobile { border-radius: 0 }
    > .header,
    > .customization-params-sides {
      padding: 15px 20px;

      .ui-btn-text-gray { padding: 0; }
    }


    > .header,
    > .footer { height: @rh; }

    > .header {
      justify-content: center;
      align-items: center;
      white-space: nowrap;

      @media @mobile {
        padding: 0;

        > div { padding: 15px 0; }
        > div:first-child { padding: 15px 20px; }
        > div:last-child { padding: 0; }
      }
      .svg-icon--cross {
        @s: 1rem;

        width: 1rem;
        height: 1rem;
        cursor: pointer;
        fill: @col-text-gray-darker;

        @media @mobile {
          @is: 1.25rem;
          @h: 50px;
          @w: 30px;
          @p: 20px;

          width: calc(@w/2 + @is/2 + @p);
          min-width: calc(@w/2 + @is/2 + @p);
          height: @h;
          min-height: @h;
          padding: calc(@h/2 - @is/2) calc(@w/2 - @is/2);
          padding-right: @p;
        }
      }
    }
    > .footer {
      overflow: hidden;
      border-radius: 0 0 @border-radius @border-radius;

      .ui-btn {
        height: 100%;
        width: 100%;
        border-radius: 0;
        justify-content: center;
        align-items: center;

        .svg-icon {
          @s: 16px;
          height: @s;
          width: @s;
        }
      }
    }
    > .customization-params-sides {
      max-height: calc(100*var(--vh) - 4*@rh);
      overflow-y: auto;
      padding-left: 30px;
      padding-right: 30px;
      border-top: 1px solid @col-text-gray-light;
      border-bottom: 1px solid @col-text-gray-light;

      @media @mobile {
        max-height: calc(100*var(--vh) - 100px);
        padding: @mm;
        
        &::v-deep .ui-collapsible > .container > .flex {
          display: block;

          .side { padding: 0; }
        }
      }
      .collapsible-wrapper + .collapsible-wrapper {
        margin-top: 10px;
      }
      .side {
        @gap: 50px;

        flex: 1 0;
        padding-right: @gap/2;
        position: relative;

        @media @desktop {
          + .side {
            padding-right: 0;
            padding-left: @gap/2;
          }
        }
        @media @mobile {
          margin-bottom: @mm;
          padding: 0;
        }
        span.title {
          font-weight: 700;
          display: block;
          margin: 10px 0 20px;
        }
        .input-group {
          @h: 40px;

          align-items: center;
          justify-content: space-between;
          height: @h;
          margin: 20px 0;

          @media @mobile { margin: 15px 0; }
          span.label {
            font-size: .9375rem;
            margin: 0 5px;
            flex: 2;
            line-height: @h/2;
          }
          &::v-deep .ui-input {
            flex: 1;
            max-width: 140px;

            .empty { order: -1; }
          }
          &.readonly {
            margin: 15px 0;
            height: 20px;

            .label { color: @col-text-gray-darker; }
            .value { font-weight: 600; }
            .ui-input {
              box-shadow: none;
            
              &::v-deep .input-wrapper { font-weight: 600; }
            }
          }
          .unlock-analytics {
            border-radius: @border-radius;
            box-shadow: 0 0 0 1px @col-gray;
            flex: 1;
            flex-wrap: nowrap;
            justify-content: flex-end;
          }
        }
        > .unlock-analytics {
          position: absolute;
          @top: 10px;
          top: @top;
          right: 0;
          width: 20%;
          height: calc(100% - 2*@top);

          @media @mobile {
            top: 0;
            width: 30%;
            height: 100%;
          }
        }
      }
      .collapsible-wrapper .ui-collapsible::v-deep > .header > .flex {
        height: 50px;
        border-bottom: 1px solid @col-gray-light;

        .svg-icon--smooth-arrow {
          @s: 12px;
          height: @s;
          width: @s;
        }
      }
      .customization-popup-summary {
        padding: 40px 0 10px;

        .side > .unlock-analytics {
          top: 30px;
          height: calc(100% - 40px);

          @media @mobile {
            height: calc(100% - 30px);
          }
        }
        .summary .unlock-analytics {
          @top: 10px;
          position: absolute;
          height: calc(100% - 2*@top);
          width: 20%;
          top: @top;
          right: @top;

          @media @mobile { width: 30%; }
        }
        @media @mobile { display: block; }
      }
      .summary {
        background: #f9f9f9;
        border-radius: @border-radius;
        padding: 10px 30px;

        @media @mobile { padding: @mm; }
        .summary-row {
          padding: 10px 0;
          justify-content: space-between;
          align-items: center;
          align-content: center;
          font-size: 0.9375rem;

          .summary-row-title { color: @col-text-on-disabled; }
          &.summary-row-total {
            font-size: 1.125rem;

            .summary-row-title {
              color: @col-text-dark;
              @media @mobile { line-height: 1.15rem; }
            }
            .summary-row-value {
              color: @col-green;
              font-size: 1.25rem;
            }
          }
        }
        .divider {
          margin: 10px 0;
          border-bottom: 1px dashed @col-gray;
        }
      }
    }
  }
}
.popup-images {
  background: rgba(0, 0, 0, 0.8);

  > .svg-icon--cross {
    @s: 20px;

    position: absolute;
    top: 10px;
    right: 10px;
    color: @col-text-light;
    width: @s;
    height: @s;
    cursor: pointer;
  }
  > .content {
    max-width: none;
    width: 100%;
    max-height: calc(100*var(--vh));
    background: transparent;

    > .controls {
      width: 100%;
      height: 40px;
      justify-content: center;
      align-items: center;

      @media @mobile { justify-content: flex-start; }
      .svg-icon {
        @s: 24px;

        width: @s;
        height: @s;
        margin: 0 @s/2;
        fill: @col-text-light;
        cursor: pointer;

        &.active { fill: @col-green; }
      }
    }
    .popup-images-list {
      width: 100%;
      height: calc(100vh - 40px);
      overflow-y: auto;

      > .wrapper {
        display: grid;
        grid-template-rows: 1fr;
        gap: 2rem;
        justify-content: center;
        align-content: stretch;
        align-items: stretch;
        padding: 2rem 0;

        @media @mobile { gap: 10px; }
        &.list { grid-template-columns: repeat(1, 1fr); }
        &.grid { grid-template-columns: repeat(2, 1fr); }
        .img-aspect-ratio {
          width: 100%;
          padding-bottom: 80%;
          position: relative;

          img {
            position: absolute;
            top: 0;
            left: 0;
            height: 100%;
            width: 100%;
            object-fit: cover;
            display: block;
          }
        }
      }
    }
  }
}

.disclaimer {
  text-align: center;

  @media @mobile { padding: 0 20px; }
}
&::v-deep {
  .mls-info, .disclaimer {
    margin-top: 70px;
    font-size: 0.875rem;
    line-height: 1.5rem;
    font-weight: 400;
    color: @col-text-gray-dark;

    a {
      font-weight: 700;
      color: @col-text-gray-dark;

      &:hover {
        color: @col-text-gray;
        text-decoration-color: @col-text-gray;
      }
    }
  }
}

.slide-enter-active,
.slide-leave-active { transition: opacity .3s ease, transform .3s ease; }
.slide-enter-from,
.slide-leave-to {
  opacity: 0;
  transform: translateY(30px);
}
</style>
<style>@import '~swiper/components/pagination/pagination.min.css';</style>

<script lang="ts">
import { defineComponent } from 'vue';
import qs from 'query-string';

import Footer from '@/components/static/footer.vue';
import UDivider from '@/components/ui/UDivider.vue';
import UDrop from '@/components/ui/UDrop.vue';
import UTooltip from '@/components/ui/UTooltip.vue';
import UButton from '@/components/ui/UButton.vue';
import URadioChip from '@/components/ui/URadioChip.vue';
import UTextInput from '@/components/ui/UTextInput.vue';
import USlider from '@/components/ui/USlider.vue';
import UCollapsible from '@/components/ui/UCollapsible.vue';
import UImagesPreview from '@/components/ui/UImagesPreview.vue';
import SmallPropsTable from '@/components/OFRC/SmallPropsTable.vue';
import UBreadcrumbs from '@/components/ui/UBreadcrumbs.vue';
import UDropAdjustment from '@/components/ui/UDropAdjustment.vue';
import FavoriteHeart from '@/components/Property/sub/FavoriteHeart.vue';
import FeatureBlock from '@/components/Property/FeatureBlock.vue';
import USmallProp from '@/components/ui/USmallProp.vue';
import UPopup from '@/components/ui/UPopup.vue';
import UShare from '@/components/ui/UShare.vue';
import MLSInfo from '@/components/OFRC/MLSInfo.vue';
import UCopyToCb from '@/components/ui/UCopyToCb.vue';
import UPreloader from '@/components/ui/UPreloader.vue';
import UnlockAnalytics from '@/components/OFRC/UnlockAnalytics.vue';
import Vue3ChartJs from '@j-t-mcc/vue3-chartjs';
import isMobile from '@/services/isMobile.service';

import MonthlyCashFlow from '@/components/Property/MonthlyCashFlow.vue';
import DetailedAssumptions from '@/components/Property/DetailedAssumptions.vue';
import PerfomanceDashboard from '@/components/Property/PerfomanceDashboard.vue';

import SwiperCore, { Pagination } from 'swiper';
import { Swiper, SwiperSlide } from 'swiper/vue';

SwiperCore.use([Pagination]);


import { useRoute } from 'vue-router';
import { debounce } from 'ts-debounce';

import AccountStore from '@/models/Account';
import PropertyStore from '@/models/Property';
import { TPropertyDTO_Financial, TPropertyDTO_Financial_CustomParams } from '@/models/Property/finance';
import { TPropertyTaxRow } from '@/models/Property/taxes';
import { TProperty_School } from '@/models/Property/schools';

import TooltipTexts from '@/constants/Tooltips';
import envModel from '@/models/env.model';

import { GoogleMap, Marker } from 'vue3-google-map';

import DataModel from '@/models/Property/finance/dataModel'

import { toUrl } from '@/models/Search';

import StatusLabel from '@/components/Property/sub/StatusLabel.vue';
import { APP_DEFAULT_SMTH_BAD_FROM_SERVER } from '@/constants/DefaultMessages';

function processData(data:Record<string, number>, years:Array<number>) {
  let res = [];
  for (let y of years)
    res.push(data[y]);
    
  return res;
}

const featuresBlocksIcons = {
  'Building and Construction': 'house-foundament-structural',
  'Community': 'team',
  'Exterior': 'nature',
  'Features': 'house-gear-inside',
  'Interior': 'rich-chair',
  'Legal and finance': 'house-dollar-inside',
  'Listing': 'clipboard-checkmark',
}

const ProFormaLayout = [
  {
    titleRow: {
      type: 'row',
      rowClass: ['high'],
      title: 'Gross Income',
      titleClass: ['title', 'title-bigger'],
      tooltip: TooltipTexts['gross_income'],
      valuesKey: 'rent_less_vacancy',
      valuesClass: ['value', 'trans-opacity'],
      format: 'usdInt'
    },
    collapsibleRows: [
      {
        type: 'row',
        rowClass: [],
        title: 'Rent',
        titleClass: ['name'],
        tooltip: TooltipTexts['rent'],
        valuesKey: 'rent',
        valuesClass: ['value', 'interim'],
        format: 'usdInt'
      },
      {
        type: 'row',
        rowClass: [],
        title: 'Vacancy',
        titleClass: ['name'],
        tooltip: TooltipTexts['vacancy'],
        valuesKey: 'vacancy_costs_empty',
        valuesClass: ['value', 'interim'],
        format: 'usdInt'
      },
      {
        type: 'divider',
        rowClass: ['divider', 'solid']
      },
      {
        type: 'row',
        rowClass: ['high'],
        title: 'Rent Less Vacancy',
        titleClass: ['title'],
        valuesKey: 'rent_less_vacancy',
        valuesClass: ['value'],
        format: 'usdInt'
      }
    ],
    appendRows: []
  },
  {
    titleRow: {
      type: 'row',
      rowClass: ['high'],
      title: 'Operating Expenses',
      titleClass: ['title', 'title-bigger'],
      tooltip: TooltipTexts['operating_expanses'],
      valuesKey: 'operating_expenses',
      valuesClass: ['value', 'trans-opacity'],
      format: 'usdInt'
    },
    collapsibleRows: [
      {
        type: 'row',
        rowClass: [],
        title: 'Management Fees',
        titleClass: ['name'],
        tooltip: TooltipTexts['management_fees'],
        valuesKey: 'management_fees',
        valuesClass: ['value', 'interim'],
        format: 'usdInt'
      },
      {
        type: 'row',
        rowClass: [],
        title: 'Maintenance / Reserves',
        titleClass: ['name'],
        tooltip: TooltipTexts['maintenance_reserves'],
        valuesKey: 'maintenance_reserves',
        valuesClass: ['value', 'interim'],
        format: 'usdInt'
      },
      {
        type: 'row',
        rowClass: [],
        title: 'HOA Fees',
        titleClass: ['name'],
        tooltip: TooltipTexts['hqa_fees'],
        valuesKey: 'hoa_fees',
        valuesClass: ['value', 'interim'],
        format: 'usdInt'
      },
      {
        type: 'row',
        rowClass: [],
        title: 'Insurance',
        titleClass: ['name'],
        tooltip: TooltipTexts['insurance'],
        valuesKey: 'insurance',
        valuesClass: ['value', 'interim'],
        format: 'usdInt'
      },
      {
        type: 'row',
        rowClass: [],
        title: 'Property Taxes',
        titleClass: ['name'],
        tooltip: TooltipTexts['property_taxes'],
        valuesKey: 'property_taxes',
        valuesClass: ['value', 'interim'],
        format: 'usdInt'
      },
      {
        type: 'row',
        rowClass: [],
        title: 'Agent Leasing Fees',
        titleClass: ['name'],
        tooltip: TooltipTexts['agent_leasing_fees'],
        valuesKey: 're_lease_fees',
        valuesClass: ['value', 'interim'],
        format: 'usdInt'
      },
      {
        type: 'row',
        rowClass: [],
        title: 'Overhead / Miscellanous',
        titleClass: ['name'],
        tooltip: TooltipTexts['overhead_miscellanous'],
        valuesKey: 'overhead_miscellanous',
        valuesClass: ['value', 'interim'],
        format: 'usdInt'
      },
      {
        type: 'divider',
        rowClass: ['divider', 'solid']
      },
      {
        type: 'row',
        rowClass: ['high'],
        title: 'Total Operating Expenses',
        titleClass: ['title'],
        valuesKey: 'operating_expenses',
        valuesClass: ['value'],
        format: 'usdInt'
      }
    ],
    appendRows: []
  },
  {
    titleRow: {
      type: 'row',
      rowClass: ['high'],
      title: 'Operating Income',
      titleClass: ['title', 'title-bigger'],
      tooltip: TooltipTexts['operating_income'],
      valuesKey: 'operating_income',
      valuesClass: ['value', 'trans-opacity'],
      format: 'usdInt'
    },
    collapsibleRows: [
      {
        type: 'row',
        rowClass: [],
        title: 'Income',
        titleClass: ['name'],
        tooltip: TooltipTexts['net_income'],
        valuesKey: 'net_income',
        valuesClass: ['value', 'interim'],
        format: 'usdInt'
      },
      {
        type: 'row',
        rowClass: [],
        title: 'Operating Expenses',
        titleClass: ['name'],
        tooltip: TooltipTexts['operating_expanses'],
        valuesKey: 'operating_expenses',
        valuesClass: ['value', 'interim'],
        format: 'usdInt'
      },
      {
        type: 'divider',
        rowClass: ['divider', 'solid']
      },
      {
        type: 'row',
        rowClass: ['high'],
        title: 'Operating Income',
        titleClass: ['title'],
        valuesKey: 'operating_income',
        valuesClass: ['value'],
        format: 'usdInt'
      }
    ],
    appendRows: [
      {
        type: 'row',
        rowClass: [],
        title: 'Operating Income Margin',
        titleClass: ['name'],
        tooltip: TooltipTexts['operating_income_margin'],
        valuesKey: 'operating_income_margin',
        valuesClass: ['value', 'interim'],
        format: '%'
      }
    ]
  },
  {
    titleRow: {
      type: 'row',
      rowClass: ['high'],
      title: 'Net Income',
      titleClass: ['title', 'title-bigger'],
      tooltip: TooltipTexts['net_income'],
      valuesKey: 'net_income',
      valuesClass: ['value', 'trans-opacity'],
      format: 'usdInt'
    },
    collapsibleRows: [
      {
        type: 'row',
        rowClass: [],
        title: 'Operating Income',
        titleClass: ['name'],
        tooltip: TooltipTexts['operating_income'],
        valuesKey: 'operating_income',
        valuesClass: ['value', 'interim'],
        format: 'usdInt'
      },
      {
        type: 'row',
        rowClass: [],
        title: 'Interest Payments',
        titleClass: ['name'],
        tooltip: TooltipTexts['interest_payments'],
        valuesKey: 'interest_payments',
        valuesClass: ['value', 'interim'],
        format: 'usdInt'
      },
      {
        type: 'divider',
        rowClass: ['divider', 'solid']
      },
      {
        type: 'row',
        rowClass: ['high'],
        title: 'Net Income',
        titleClass: ['title'],
        valuesKey: 'net_income',
        valuesClass: ['value'],
        format: 'usdInt'
      }
    ],
    appendRows: [
      {
        type: 'row',
        rowClass: [],
        title: 'Net Income Margin',
        titleClass: ['name'],
        tooltip: TooltipTexts['net_income_margin'],
        valuesKey: 'net_income_margin',
        valuesClass: ['value', 'interim'],
        format: '%'
      }
    ]
  },
  {
    titleRow: {
      type: 'row',
      rowClass: ['high'],
      title: 'Cash Flow',
      titleClass: ['title', 'title-bigger'],
      tooltip: TooltipTexts['cash_flow'],
      valuesKey: 'cash_flow',
      valuesClass: ['value', 'trans-opacity'],
      format: 'usdInt'
    },
    collapsibleRows: [
      {
        type: 'row',
        rowClass: [],
        title: 'Operating Income',
        titleClass: ['name'],
        tooltip: TooltipTexts['operating_income'],
        valuesKey: 'operating_income',
        valuesClass: ['value', 'interim'],
        format: 'usdInt'
      },
      {
        type: 'row',
        rowClass: [],
        title: 'Interest Payments',
        titleClass: ['name'],
        tooltip: TooltipTexts['interest_payments'],
        valuesKey: 'interest_payments',
        valuesClass: ['value', 'interim'],
        format: 'usdInt'
      },
      {
        type: 'row',
        rowClass: [],
        title: 'Principal Payments',
        titleClass: ['name'],
        tooltip: TooltipTexts['principal_payments'],
        valuesKey: 'loan_payments',
        valuesClass: ['value', 'interim'],
        format: 'usdInt'
      },
      {
        type: 'divider',
        rowClass: ['divider', 'solid']
      },
      {
        type: 'row',
        rowClass: ['high'],
        title: 'Cash Flow',
        titleClass: ['title'],
        valuesKey: 'cash_flow',
        valuesClass: ['value'],
        format: 'usdInt'
      }
    ],
    appendRows: []
  }
];

const updateFinanceModel = debounce(function (model:any, params: object) {
  if ((<any>params).monthly_rent != undefined)
    model.load({ ...params, monthly_rent: Math.round((<any>params).monthly_rent) });
  else
    model.load(params);
}, 1000);

let _Property:any = undefined;

export default defineComponent({
  components: {
    UDivider,
    UDrop,
    UButton,
    USlider,
    URadioChip,
    UTextInput,
    UTooltip,
    UDropAdjustment,
    UCollapsible,
    USmallProp,
    FeatureBlock,
    UBreadcrumbs,
    SmallPropsTable,
    UImagesPreview,
    UPopup,
    UShare,
    UCopyToCb,
    UPreloader,
    UnlockAnalytics,
    MLSInfo,
    Footer,
    Vue3ChartJs,
    Swiper,
    SwiperSlide,
    GoogleMap,
    Marker,
    StatusLabel,
    FavoriteHeart,
    MonthlyCashFlow,
    DetailedAssumptions,
    PerfomanceDashboard
  },
  computed: {
    featuresBlocksIcons() {
      return featuresBlocksIcons
    },
    Property() {
      if (this.initStarted)
        return _Property;

      const params = <string | undefined>this.route.params.financialProps;
      const parsedParams = params && qs.parse(params, { parseBooleans: true, parseNumbers: true });

      // down_payment=0.2&interest_rate=0.033&loan_type=30&priceMode=cash
      const financialData = parsedParams ? {
        down_payment: parsedParams.priceMode == 'cash' ? 1 : parsedParams.down_payment,
        financing_years: parsedParams.loan_type,
        interest_rate: parsedParams.interest_rate
      } : {};

      //@ts-ignore
      const { PropertyObject: PropertyStoreInstance, existPromise } = PropertyStore(this.route.params.id, financialData);
      _Property = PropertyStoreInstance;

      if (financialData?.down_payment)
        this.$router.replace({ name: 'property', params: { id: this.route.params.id } });

      this.initStarted = true;

      existPromise.then(exists => {
        if (!exists)
          this.$router.push({ name: 'static-not-found' });
      });

      PropertyStoreInstance.Finance.isReadyPromise.then(() => {
        this.resetCustomization('all');
        this.customizationParametersPercentiles = {
          price: [
            //@ts-ignore
            Math.round(0.5 * PropertyStoreInstance.Basis.dto?.data.price / 1000) * 1000,
            //@ts-ignore
            Math.round(1.5 * PropertyStoreInstance.Basis.dto?.data.price / 1000) * 1000
          ]
        }

        this.customizationReady = true;

        AccountStore.Auth.initPromise.then(() => {
          window.dataLayer = window.dataLayer || [];
          window.dataLayer.push({
            event: 'listing_page_view',
            user_id: JSON.stringify(AccountStore.Basis.dto?.pk),
            cap_rate: JSON.stringify(PropertyStoreInstance.Finance.dto?.main_results.cap_rate),
            price: JSON.stringify(PropertyStoreInstance.Finance.dto?.base.price),
            prop_type: JSON.stringify(PropertyStoreInstance.Basis.dto?.summary.prop_type)
          });
        });
      })
      .catch(() => {
        AccountStore.Auth.initPromise.then(() => {
          if (!AccountStore.Basis.isPremium) {
            this.resetCustomization('all');
            this.customizationParametersPercentiles = {
              price: [
                //@ts-ignore
                Math.round(0.5 * PropertyStoreInstance.Basis.dto?.data.price / 1000) * 1000,
                //@ts-ignore
                Math.round(1.5 * PropertyStoreInstance.Basis.dto?.data.price / 1000) * 1000
              ]
            }
            this.customizationReady = true;
          }
          window.dataLayer = window.dataLayer || [];
          window.dataLayer.push({
            event: 'listing_page_view',
            user_id: JSON.stringify(AccountStore.Basis.dto?.pk),
            prop_type: JSON.stringify(PropertyStoreInstance.Basis.dto?.summary.prop_type)
          });
        });
      });
      return PropertyStoreInstance;
    },
    fullPropertyAddress() {
      const address = <any>this.Property.Basis.dto?.address;
      return [address?.line, address?.city, address?.state, address?.zip].filter(e => e != undefined).join(' ');
    },
    ProForma() {
      const FinanceModel = <any>this.Property.Finance.dto;
      const proforma = (<TPropertyDTO_Financial>FinanceModel)?.proforma;

      if (!proforma)
        return {};
      
      const years = [];
      for (let y in proforma.year)
        years.push(y);

      return {
        years,
        blocks: ProFormaLayout
      }
    },
    FinanceAccumulatedWealthPlot() {
      const FinanceModel = <any>this.Property.Finance.dto;
      const acw = (<TPropertyDTO_Financial>FinanceModel)?.accumulated_wealth;

      if (!acw)
        return null;

      let labels:number[] = [];
      for (let y in acw.year)
        labels.push(acw.year[y]);

      this.plotsShow = false;
      this.$nextTick(() => {
        this.plotsShow = true;
        this.finance_acw_plot_tooltip_index = this.FinanceAccumulatedWealthPlot?.__maxYears || 1;
      });
      return {
        __maxYears: labels[labels.length - 1],
        type: 'line',
        data: {
          labels: labels.map(l => l == 1 || l % 5 == 0 ? l : ''),
          datasets: [{
            __autoLegendOff: true,
            label: 'Loan Balance',
            __attrName: 'loan_balance',
            fill: false,
            borderColor: '#222222',
            borderDash: [8, 8],
            pointRadius: 0,
            data: processData(acw.loan_balance, labels),
            datalabels: { display: false }
          }, {
            label: 'Cash Flow',
            __attrName: 'cash_flow_from_operations',
            fill: true,
            borderColor: '#01D092',
            backgroundColor: 'rgba(192, 243, 228, 0.5)',
            pointRadius: 0,
            stack: 'combined',
            data: processData(acw.cash_flow_from_operations, labels),
            datalabels: { display: false }
          }, {
            label: 'Appreciation',
            __attrName: 'property_appreciation',
            fill: true,
            borderColor: '#6454C3',
            backgroundColor: 'rgba(216, 212, 240, 0.5)',
            pointRadius: 0,
            stack: 'combined',
            data: processData(acw.property_appreciation, labels),
            datalabels: { display: false }
          }, {
            label: 'Equity',
            __attrName: 'eqity',
            fill: true,
            borderColor: '#00A3FF',
            backgroundColor: 'rgba(191, 232, 255, 0.5)',
            pointRadius: 0,
            stack: 'combined',
            data: processData(acw.eqity, labels),
            datalabels: { display: false }
          }]
        },
        options: {
          interaction: {
            intersect: false,
            mode: 'index',
          },
          aspectRatio: isMobile.value ? 1 : 3,
          scales: {
            x: {
              grid: {
                display: false,
                drawBorder: false,
                drawTicks: false
              }
            },
            y: {
              position: 'right',
              grid: {
                drawBorder: false,
                color: "rgba(0, 0, 0, 0.02)"
              },
              stacked: true
            }
          },
          elements: {
            line: {
              tension: 0.4
            }
          },
          plugins: {
            legend: {
              display: false
            },
            tooltip: {
              enabled: false,
              position: 'nearest',
              external: (context:any) => {
                this.finance_acw_plot_tooltip(context);
              }
            }
          }
        }
      }
    },
    TaxHistoryPlot() {
      const TaxHistory = <TPropertyTaxRow[]>this.Property.Taxes.dto?.tax_history;

      if (!TaxHistory || TaxHistory.length < 1)
        return null;

      let labels = TaxHistory.map(e => e.year).reverse();
      let data = TaxHistory.map(e => e.tax).reverse();
      
      return {
        type: 'line',
        data: {
          labels,
          datasets: [{
            label: 'Property Tax',
            fill: false,
            borderColor: '#6454C3',
            pointRadius: 0,
            data,
            datalabels: { display: false },
          }]
        },
        options: {
          aspectRatio: isMobile.value ? 1 : 3,
          scales: {
            x: {
              grid: {
                display: false,
                drawBorder: false,
                drawTicks: false
              },
              ticks: { padding: 20 }
            },
            y: {
              grid: {
                drawBorder: false,
                color: "rgba(0, 0, 0, 0.02)"
              },
              ticks: { padding: 20 }
            }
          },
          elements: {
            line: {
              tension: 0.4
            }
          },
          plugins: {
            legend: {
              display: false,
              align: 'start'
            }
          }
        }
      }
    },
    SchoolsFiltered() {
      let schoolsDTO = this.Property.Schools.dto;
      let schools = <TProperty_School[]>schoolsDTO?.schools
      
      if (!schools)
        return [];

      //@ts-ignore
      let type:string = this.schoolType;
      if (type == 'all')
        return schools;

      return schools.filter((s) => s.education_levels.includes(type));
    },
    TooltipTexts() {
      return TooltipTexts;
    },
    GAPI_KEY() {
      return envModel.VUE_APP_API_GOOGLE_MAP_TOKEN
    },
    DataModel() {
      return DataModel;
    },
    toUrl() {
      return toUrl;
    },
    Account() {
      return AccountStore;
    }
  },
  watch: {
    customizationParameters: {
      handler(newv, old) {
        if (this.customizationReady && Object.keys(old).length > 0)
          updateFinanceModel(<any>this.Property.Finance, newv);
      },
      deep: true
    },
    activeTab() {
      const tabs = (<any>this.$refs).tabsBar.getBoundingClientRect();
      let offset = tabs.top;

      const supportPageOffset = window.pageXOffset !== undefined;
      const isCSS1Compat = ((document.compatMode || "") === "CSS1Compat");
      const scrollOffset = supportPageOffset ? window.pageYOffset : isCSS1Compat ? document.documentElement.scrollTop : document.body.scrollTop;

      const tabsOffsetTop = scrollOffset + offset - tabs.height;
      window.scrollTo({ top: tabsOffsetTop, behavior: 'smooth' });
    }
  },
  setup() {
    const route = useRoute();
    return { route };
  },
  data() {
    return {
      initStarted: false,
      headerRowState: 0,
      scrollingDown: 0,
      lastScrollOffset: 0,
      activeTab: 'financial',
      schoolType: 'all',
      photosStyle: 'grid',

      plotsShow: true,
      proFormaRowsOpenStatus: Array(ProFormaLayout.length).fill(false),

      customizationReady: false,
      customizationParameters: {} as TPropertyDTO_Financial_CustomParams,
      customizationParametersPercentiles: {
        price: []
      },
      finance_acw_plot_tooltip_index: 1,
      report_in_progress: false,
      proFormaRowspan: 5
    }
  },
  methods: {
    onScroll() {
      const posun = this.lastScrollOffset - window.pageYOffset;
      this.scrollingDown = posun < 0 ? 0 : this.scrollingDown + posun;

      this.lastScrollOffset = window.pageYOffset;

      let newState = 0;

      const header = <HTMLDivElement>this.$refs.headerBar;
      if (!header)
        return this.headerRowState = 0;
      
      const headerBR = header.getBoundingClientRect();
      if (headerBR.top <= 0)
        newState = 1;

      const tabs = <HTMLDivElement>this.$refs.tabsBar;
      const tabsBR = tabs.getBoundingClientRect();
      if (tabsBR.top <= 0)
        newState = 2;

      if (newState > 0) {
        // Vue 3 workaround (works fine w/o, but throws exceptions. WTF?)
        try { (<any>this.$root).$refs.accountDropMenu.close(); }
        catch (ex) {}

        try { (<any>this.$root).$refs.learnDropMenu.close(); }
        catch (ex) {}
      }

      this.headerRowState = newState;
    },
    finance_acw_plot_tooltip(context:any) {
      const { chart, tooltip } = context;

      if (tooltip.opacity !== 0 && tooltip.dataPoints && tooltip.dataPoints[0])
        this.finance_acw_plot_tooltip_index = tooltip.dataPoints[0].dataIndex + 1;
      else
        this.finance_acw_plot_tooltip_index = this.FinanceAccumulatedWealthPlot?.__maxYears || 1;

      // chart.canvas.offsetLeft + tooltip.caretX + 'px';
    },
    resetCustomization(attr: string | Array<string>) {
      const customizationParameters = this.Property.Finance.getCustomizationParams();
      if (!customizationParameters)
        return;

      if (Array.isArray(attr)) {
        attr.forEach(m => {
          this.customizationParameters[m] = customizationParameters[m];
        });
      } else if (attr == 'all') {
        this.customizationParameters = customizationParameters;
      } else if (Object.keys(this.customizationParameters).includes(attr)) {
        this.customizationParameters[attr] = customizationParameters[attr];
      }
    },
    close(e?:MouseEvent) {
      if (e && e.target != this.$refs.imagesWrapper)
        return;

      (<any>this).$refs.imagesPopup.close()
    },
    getReport() {
      if (this.report_in_progress)
        return;

      this.report_in_progress = true;

      this.Property.Basis.generateReport(this.customizationParameters)
      .then((res: any) => {
        if (!res)
          return (<any>this.$root).$refs.globMessages.push(APP_DEFAULT_SMTH_BAD_FROM_SERVER);
        
        //@ts-ignore
        if (res == false) {
          (<any>this.$root).$refs.globMessages.push({ type: 'custom-rent-anal-limit-warning', message: 'You have reached your limits!' });
          return (<any>this.$root).$refs.popupUpgrade.open();
        }

        window.open(res.report_file, '_blank');
      })
      .catch((ex: any) => {
        return (<any>this.$root).$refs.globMessages.push(APP_DEFAULT_SMTH_BAD_FROM_SERVER);
      })
      .finally(() => {
        this.report_in_progress = false;
      });
    }
  },
  mounted() {
    window.addEventListener('scroll', this.onScroll);
  },
  beforeUnmount() {
    window.removeEventListener('scroll', this.onScroll);
  }
})
</script>