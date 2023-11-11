<template>
  <div class="rent-estimator">
    <div class="wrapper">
      <div class="header flex" :class="{ 'show-toggle-customization': showToggleCustomization }">
        <h1>Rent Analyzer</h1>
        <div class="toggle-customization" @click="toggleCustomizationCollapsible" v-show="showToggleCustomization" ref="toggle-customization"></div>
      </div>
      <UCollapsible opened ref="customizationCollapsible">
        <template v-slot:header="props">
          <teleport v-if="$refs['toggle-customization']" :to="$refs['toggle-customization']">
            <UButton :class="{ 'opened': props.isOpen }">
              Edit {{ query.customization.searchMode }}
              <UIcon name="smooth-arrow"/>
            </UButton>
          </teleport>
        </template>
        <div class="search-mode-selector flex">
          <div class="mobile-mm"></div>
          <URadioChip v-model="query.customization.searchMode" name="search-mode-radio" value="address"><UIcon name="house-smaller" />Address</URadioChip>
          <URadioChip v-model="query.customization.searchMode" name="search-mode-radio" value="zip"><UIcon name="placemark" />ZIP Code</URadioChip>
          <URadioChip v-model="query.customization.searchMode" name="search-mode-radio" value="city"><UIcon name="city" />City</URadioChip>
          <div class="mobile-mm"></div>
        </div>
        <div class="search" :class="{'search-zip-city': query.customization.searchMode != 'address'}">
          <div class="search-string search-box">
            <span class="label" v-if="!$isMobile.value">{{ query.customization.searchMode.charAt(0).toUpperCase() + query.customization.searchMode.slice(1) }}</span>
            <UAutocomplete icon="target" :placeholder="`Enter ${query.customization.searchMode}`" inactive :searchFunction="() => {}" @keyup.enter="Account.Restrictions.canUseCustomization() && calculate()" ref="queryAutoComplete"/>
          </div>
          <div class="search-building-size search-box" v-show="query.customization.searchMode == 'address'">
            <span class="label" v-if="!$isMobile.value">Living Area Size</span>
            <span class="label" v-else>Living Area Size:</span>
            <UTextInput placeholder="Enter Living Area Size" name="rent_analyzer_building_size" v-model="query.customization.building_size" type="number" postpend="sq ft." allowNull dataHjAllow />
          </div>
          <div class="search-lookback search-box">
            <span class="label" v-if="!$isMobile.value">Look Back</span>
            <span class="label" v-else>Look Back:</span>
            <USelectDrop v-model="query.customization.lookBack" :label="query.customization.lookBack.label" :options="lookBackDefs" mHeader="Look Back">
              <template v-slot:item="{ option }">{{ option.label }}</template>
            </USelectDrop>
          </div>
          <div class="search-distance search-box">
            <span class="label" v-if="!$isMobile.value">Distance</span>
            <span class="label" v-else>Distance:</span>
            <USelectDrop v-model="query.customization.distance" :label="query.customization.distance.label" :options="distanceDefs" mHeader="Distance">
              <template v-slot:item="{ option }">{{ option.label }}</template>
            </USelectDrop>
          </div>
          <div class="search-beds search-box">
            <span class="label" v-if="!$isMobile.value">Beds</span>
            <span class="label" v-else>Beds:</span>
            <USelectDrop v-model="query.customization.beds" :label="query.customization.beds.label" :options="bedsDefs" mHeader="Beds">
              <template v-slot:item="{ option }">{{ option.label }}</template>
            </USelectDrop>
          </div>
          <div class="search-baths search-box">
            <span class="label" v-if="!$isMobile.value">Baths</span>
            <span class="label" v-else>Baths:</span>
            <USelectDrop v-model="query.customization.baths" :label="query.customization.baths.label" :options="bathsDefs" mHeader="Baths">
              <template v-slot:item="{ option }">{{ option.label }}</template>
            </USelectDrop>
          </div>
          <div class="search-type search-box">
            <span class="label" v-if="!$isMobile.value">Type</span>
            <span class="label" v-else>Type:</span>
            <USelectDrop v-model="query.customization.propType" :label="query.customization.propType.label" :options="propTypes2Defs" mHeader="Property Type">
              <template v-slot:item="{ option }">{{ option.label }}</template>
            </USelectDrop>
          </div>
          <div class="search-search search-box">
            <span class="label hide-mobile">&nbsp;</span>
            <UButton class="ui-btn ui-btn-green btn-analyze" :busy="queryInProgress" @click="calculate()" :class="{ disabled: queryInProgress }">Analyze</UButton>
          </div>
        </div>
      </UCollapsible>

      <UMessageList ref="messageList" />

      <UDivider ref="diviredReady" />

      <div class="rent-estimator-results" v-if="result != null">
        <div class="header flex">
          <div class="address-row flex">
            <span class="address">{{ result.address.formatted_address }}</span>
            <span class="more">{{ [result.address.city, result.address.state_name].join(', ') }}, USA</span>
          </div>
          <div class="rent-estimator-actions flex">
            <UShare />
            <UButton class="ui-btn-text-gray" :class="{ disabled: !Account.Auth.isLoggedIn || report_in_progress }" @click="getReport"><UIcon name="download" />Report</UButton>
          </div>
        </div>
        <div class="highlights flex">
          <div class="details">
            <table class="fin-table">
              <tr>
                <td>
                  <USmallProp :value="result.rent.average" label="Average" :formatter="$format['usdInt']"/>
                </td>
                <td>
                  <USmallProp :value="result.rent.median" label="Median" :formatter="$format['usdInt']"/>
                </td>
                <td rowspan="2" class="rich-prop">
                  <USmallProp :value="result.rent.prediction" label="Est. Rent" :formatter="$format['usdInt']"/>
                  <img src="../../assets/icons/ai-powered-color.svg" alt="" />
                </td>
              </tr>
              <tr>
                <td>
                  <USmallProp :value="result.rent.percentile25" label="25th Percentile" :formatter="$format['usdInt']"/>
                </td>
                <td>
                  <USmallProp :value="result.rent.percentile75" label="75th Percentile" :formatter="$format['usdInt']"/>
                </td>
              </tr>
            </table>
            <span class="based-on">Results based on {{ result.stat.qty }} rentals seen in a {{ result.stat.max_dist.toFixed(2) }} mile radius.</span>
            <USVGraph
              :minValue="result.rent.min"
              :maxValue="result.rent.max"
              :medianValue="result.rent.median"
              :q25="result.rent.percentile25"
              :q75="result.rent.percentile75"
              :est_rate="result.rent.prediction"
            />
          </div>
          <div class="map-list hide-mobile">
            <div class="map">
              <GoogleMap
                class="google-map"
                :api-key="GAPI_KEY"
                :center="{ lat: result.address.lat, lng: result.address.lon }"
                :zoom="10"
                :disableDefaultUI="true"
                :streetViewControl="true"
                :mapTypeControl="true"
                :fullscreenControl="false"
                :zoomControl="true"
                :minZoom="8"
                :zoomControlPosition="'TOP_RIGHT'"
                gestureHandling="greedy"
                ref="map1Ref"
              >

                <Circle
                  :options="{
                    center: { lat: result.address.lat, lng: result.address.lon },
                    radius: result.stat.max_dist * 1612,
                    strokeWeight: 0,
                    fillColor: '#6454C3',
                    fillOpacity: 0.07
                  }"
                />
                <Marker
                  v-for="i of mapMarkers"
                  :key="i"
                  :options="{
                    position: i.position,
                    icon: i.icon
                  }"
                  @click="markerOnClick(1, i.list)"
                />
                <Marker
                  :options="{
                    position: { lat: result.address.lat, lng: result.address.lon },
                    icon: {
                      url: '/mapMarkerIcons/map-icon-home.svg',
                      anchor: {x: 15, y: 15}
                    }
                  }"
                />

                <InfoWindowWrapper ref="map1InfoWindow" mode="rent_anal" />
              </GoogleMap>
              <UDrop v-if="$isMobile.value" :mHeader="mapInfoWindowMobileHeader" ref="map1InfoWindowMobileDrop" label="test">
                <template v-slot:content>
                  <InfoWindowWrapper ref="map1InfoWindowMobile" dontRemove mode="rent_anal" />
                </template>
              </UDrop>
            </div>
            <div class="markers-description flex">
              <div class="marker-info flex">
                <UIcon name="rent-estimator-marker-green-wo-shadow" />
                Lower Rent
              </div>
              <div class="marker-info flex">
                <UIcon name="rent-estimator-marker-blue-wo-shadow" />
                Moderate Rent
              </div>
              <div class="marker-info flex">
                <UIcon name="rent-estimator-marker-red-wo-shadow" />
                Higher Rent
              </div>
            </div>
          </div>
        </div>
        <div class="plots flex">
          <div class="ui-plot">
            <span class="ui-plot-title">Rent Distribution</span>
            <div class="ui-plot-legend flex">
              <div class="item flex" v-for="i of rentDistributionPlot?.data?.datasets?.filter(o => !o.__autoLegendOff)" :key="i">
                <div class="flex">
                  <span class="color" :style="{ background: i.backgroundColor, 'border-color': i.backgroundColor }"></span>
                  <span class="title" v-text="i.label"></span>
                </div>
              </div>
            </div>
            <vue3-chart-js
              v-if="rentDistributionPlot && !queryInProgress"
              v-bind="{ ...rentDistributionPlot }"
              :width="100"
            ></vue3-chart-js>
          </div>
          <div class="ui-plot">
            <span class="ui-plot-title">Offers and Median Rent by Bedroom Type</span>
            <div class="ui-plot-legend flex">
              <div class="item flex" v-for="i of bedroomTypePlot?.data?.datasets?.filter(o => !o.__autoLegendOff)" :key="i">
                <div class="flex">
                  <span class="color" :style="{ background: i.backgroundColor || i.pointBackgroundColor, 'border-color': i.backgroundColor || i.pointBackgroundColor }"></span>
                  <span class="title" v-text="i.label"></span>
                </div>
              </div>
            </div>
            <vue3-chart-js
              v-if="bedroomTypePlot && !queryInProgress"
              v-bind="{ ...bedroomTypePlot }"
              :width="100"
            ></vue3-chart-js>
          </div>
          <div class="ui-plot">
            <span class="ui-plot-title">Offers and Median Rent by Building Type</span>
            <div class="ui-plot-legend flex">
              <div class="item flex" v-for="i of buildingTypePlot?.data?.datasets?.filter(o => !o.__autoLegendOff)" :key="i">
                <div class="flex">
                  <span class="color" :style="{ background: i.backgroundColor || i.pointBackgroundColor, 'border-color': i.backgroundColor || i.pointBackgroundColor }"></span>
                  <span class="title" v-text="i.label"></span>
                </div>
              </div>
            </div>
            <vue3-chart-js
              v-if="buildingTypePlot && !queryInProgress"
              v-bind="{ ...buildingTypePlot }"
              :width="100"
            ></vue3-chart-js>
          </div>
          <div class="ui-plot">
            <span class="ui-plot-title">Offers and Median Rent by Living Area Size</span>
            <div class="ui-plot-legend flex">
              <div class="item flex" v-for="i of homePriceTypePlot?.data?.datasets?.filter(o => !o.__autoLegendOff)" :key="i">
                <div class="flex">
                  <span class="color" :style="{ background: i.backgroundColor || i.pointBackgroundColor, 'border-color': i.backgroundColor || i.pointBackgroundColor }"></span>
                  <span class="title" v-text="i.label"></span>
                </div>
              </div>
            </div>
            <vue3-chart-js
              v-if="homePriceTypePlot && !queryInProgress"
              v-bind="{ ...homePriceTypePlot }"
              :width="100"
            ></vue3-chart-js>
          </div>
        </div>
        <div class="map-list">
          <div class="map">
            <GoogleMap
              class="google-map"
              :api-key="GAPI_KEY"
              :center="{ lat: result.address.lat, lng: result.address.lon }"
              :zoom="10"
              :disableDefaultUI="true"
              :streetViewControl="true"
              :mapTypeControl="true"
              :fullscreenControl="false"
              :zoomControl="true"
              :minZoom="8"
              :zoomControlPosition="'TOP_RIGHT'"
              gestureHandling="greedy"
              ref="map2Ref"
            >

              <Circle
                :options="{
                  center: { lat: result.address.lat, lng: result.address.lon },
                  radius: result.stat.max_dist * 1612,
                  strokeWeight: 0,
                  fillColor: '#6454C3',
                  fillOpacity: 0.07,
                }"
              />
              <Marker
                v-for="i of mapMarkers"
                :key="i"
                :options="{
                  position: i.position,
                  icon: i.icon
                }"
                @click="markerOnClick(2, i.list)"
              />
              />
              <Marker
                :options="{
                  position: { lat: result.address.lat, lng: result.address.lon },
                  icon: {
                    url: '/mapMarkerIcons/map-icon-home.svg',
                    anchor: {x: 15, y: 15}
                  }
                }"
              />
              <InfoWindowWrapper ref="map2InfoWindow" mode="rent_anal" />
            </GoogleMap>
            <UDrop v-if="$isMobile.value" :mHeader="mapInfoWindowMobileHeader" ref="map2InfoWindowMobileDrop" label="test">
              <template v-slot:content>
                <InfoWindowWrapper ref="map2InfoWindowMobile" dontRemove mode="rent_anal" />
              </template>
            </UDrop>
          </div>
          <div class="markers-description flex">
            <div class="marker-info flex">
              <UIcon name="rent-estimator-marker-green-wo-shadow" />
              Lower Rent
            </div>
            <div class="marker-info flex">
              <UIcon name="rent-estimator-marker-blue-wo-shadow" />
              Moderate Rent
            </div>
            <div class="marker-info flex">
              <UIcon name="rent-estimator-marker-red-wo-shadow" />
              Higher Rent
            </div>
          </div>
        </div>
        <div class="nearest-props">
          <span class="heading">{{ result.items?.length || 'No' }} Closest Comparable Properties</span>
          <table class="ui-table ui-table--stripped ui-table--mobile-transform">
            <tr>
              <th>Address</th>
              <th>Distance</th>
              <th>Rent</th>
              <th>Size</th>
              <th>$/ft²</th>
              <th>Beds</th>
              <th>Baths</th>
              <th>Prop Type</th>
            </tr>
            <tr v-for="p of result.items" :key="p">
              <td>
                <UIcon :name="
                  p.type == 'lower' ? 'rent-estimator-marker-green-wo-shadow' :
                  p.type == 'moderate' ? 'rent-estimator-marker-blue-wo-shadow' :
                  p.type == 'higher' ? 'rent-estimator-marker-red-wo-shadow' : 
                  'rent-estimator-marker-blue-wo-shadow'
                "/>
                {{ p.address }}
              </td>
              <td data-desc="Distance">{{ p.distance.toFixed(2) }} mi</td>
              <td data-desc="Rent">{{ $format['usdInt'](p.price) }}</td>
              <td data-desc="Size">{{ $format['number'](p.building_size) }} ft²</td>
              <td data-desc="$/ft²">{{ $format['usd'](p.price_per_ft2) }}</td>
              <td data-desc="Beds">{{ p.beds }}</td>
              <td data-desc="Baths">{{ p.baths }}</td>
              <td data-desc="Prop Type">{{ p.prop_type2 }}</td>
            </tr>
          </table>
        </div>
      </div>

      <div class="tool-description flex" v-if="result == null">
        <div class="text">
          <h2>Are you charging enough for rent? <br>Having difficulty finding tenants?</h2>
          <p>Rent Analyzer is the best way to compare properties to optimize rent prices - so you don’t miss out on profits and your property does not sit vacantly</p>
        </div>
        <USVGraph
          :est_rate="3970"
          :minValue="1700"
          :maxValue="12850"
          :medianValue="3750"
          :q25="2600"
          :q75="5950"
        />
      </div>
    </div>
  </div>
  <Footer />
</template>


<style lang="less" scoped>
.rent-estimator {
  margin: 40px 0 50px;

  @media @mobile { margin: 25px 0; }
  .map {
    position: relative;
    border-radius: @border-radius;
    overflow: hidden;
    box-shadow: 0 0 0 1px @col-shadow;

    &::v-deep {
      .ui-drop-label { display: none }
      .property-card .data .ui-small-prop:nth-child(3) { display: block; }
      .property-card .data .ui-small-prop .value { margin-bottom: 5px; }
    }
  }
  .google-map {
    position: absolute;
    top: 0;
    left: 0;

    &, &::v-deep > div {
      width: 100%;
      height: 100%;
    }
  }
  .wrapper {

    @media @mobile { max-width: none; }
    .limit {
      max-width: 440px;
      margin: 0 auto 30px;
      justify-content: center;
      align-items: center;

      .ui-href { cursor: pointer }
    }
    > .header {
      justify-content: center;
      align-items: center;
      margin-bottom: 40px;

      &.show-toggle-customization { justify-content: space-between; }
      @media @mobile {
        padding: 0 @mm;
        margin-bottom: 25px;
      }
    }
    h1 {
      display: block;
      text-align: center;
      font-size: 2.625rem;
      font-weight: 800;

      @media @mobile {
        line-height: 2.6rem;
        font-size: 1.85rem;
      }
    }
    .toggle-customization {
      .ui-button {
        font-weight: 600;
        border-radius: 20px;
        box-shadow: 0 0 0 1px @col-gray;
        padding: 10px 12px;
  
        .svg-icon {
          @s: 12px;
  
          transition: transform 0.2s ease;
          transform: rotate(180deg);
          width: @s;
          height: @s;
          margin-left: 8px;
        }
        &.opened {
          .svg-icon { transform: rotate(0); }
        }
      }
    }
    .search-mode-selector {
      justify-content: center;
      align-items: center;
      margin-bottom: 30px;

      @media @mobile {
        padding: 5px 0;
        overflow-x: auto;
        width: 100%;
        justify-content: flex-start;
      }
      .ui-radio-chip {
        color: @col-text-gray-darker;
        font-weight: 700;
        padding: 0 24px;
        height: 40px;
        line-height: 40px;
        display: flex;
        justify-content: flex-start;
        align-items: center;
        border-radius: 20px;
        font-size: 1rem;
        box-shadow: 0 0 0 1px @col-gray-light;
        flex-shrink: 0;

        @media @mobile { padding: 0 10px; }
        &:hover {
          color: @col-text-gray-dark;
          box-shadow: 0 0 0 1px @col-text-gray-dark;
        }
        &.selected {
          color: @col-text-dark;
          box-shadow: 0 0 0 1px #EBEBEB;
          background: #EBEBEB;
        }

        .svg-icon {
          @s: 20px;

          width: @s;
          min-width: @s;
          height: @s;
          min-height: @s;
          margin-right: 8px;
        }
      }
    }
    > .unregistered-warning {
      text-align: center;
      margin: 60px 0;
      font-weight: 400;
      display: flex;
      align-items: center;
      align-content: center;
      justify-content: center;

      @media @mobile { display: block; }
      .warning {
        background: @col-disabled;
        border-radius: @border-radius;
        padding: 15px 20px;
        margin-right: 30px;
        font-size: .875rem;
        align-items: center;
        align-content: center;
        justify-content: center;
  
        > .svg-icon {
          width: 15px;
          height: 15px;
          margin-right: 15px;
          flex-shrink: 0;
        }
      }
      .start-free-trial {
        font-size: 0.875rem;
        color: @col-text-gray-darker;

        @media @mobile { font-size: .75rem }
        > span {
          font-size: 1rem;
          color: @col-green;
          text-decoration-color: @col-green;
          font-weight: 700;
        }
      }
      @media @mobile {
        padding: 0 20px;
        margin: 20px 0;

        .warning {
          align-items: center;
          width: 100%;
          margin-bottom: 20px;
          line-height: 1.25rem;
        }
      }
    }
    .search {
      display: grid;
      grid-template-columns: repeat(5, 1fr);
      grid-template-rows: repeat(2, 1fr);
      gap: 20px;
      grid-template-areas:
        "s s s . ."
        ". . . . .";

      @media @mobile {
        grid-template-columns: 1fr;
        grid-template-rows: 1fr;
        grid-template-areas: none;
        padding: 0 @mm;
      }
      @media @desktop {
        .search-string { grid-area: s; }
      }
      .search-box {

        @media @mobile {
          display: flex;
          flex-wrap: nowrap;
          align-items: center;
          align-content: center;
          justify-content: flex-start;
          border: 1px solid @col-gray;
          border-radius: @border-radius;

          &.search-search { border-color: transparent; }
          &::v-deep {
            .input-wrapper, .ui-input, .ui-drop-label {
              box-shadow: none;
            }
            .search-component, .ui-input, .ui-drop {
              flex: 1;
            }
          }
        }
        > span.label {
          font-weight: 700;
          margin-bottom: 10px;
          display: block;

          @media @mobile {
            white-space: nowrap;
            margin: 0 5px 0 10px;
          }
        }
        > .btn-analyze {
          width: 100%;
          height: 45px;
        }
        &.disabled {
          position: relative;
          opacity: 0.3;

          &:before {
            content: '';
            display: block;
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 1;
          }
        }
      }
      .search-building-size::v-deep > .ui-input {
        height: 45px;
        margin: 0;

        .input-wrapper {
          width: 100%;
          font-weight: inherit;
        }
        .empty { display: none; }
      }
    }
    .search-zip-city {
      grid-template-areas:
        "s s s s s"
        ". . . . .";

      .search-distance { display: none; }
      @media @mobile { grid-template-areas: none; }
    }
    > .ui-message-list {
      margin-top: 20px;

      @media @mobile {
        padding: 0 @mm;
      }
    }
    > .ui-divider {
      margin-top: 40px;
      margin-bottom: 50px;

      @media @mobile {
        margin: 25px auto;
        width: calc(100% - 2*@mm);
      }
    }
    > .tool-description {
      justify-content: space-between;
      align-items: center;

      @media @mobile {
        padding: 0 @mm;
        display: block;
      }
      > .text {
        padding-bottom: 20px;
        width: 55%;

        @media @mobile {
          text-align: center;
          width: 100%; 
        }
        h2 {
          font-size: 2.25rem;
          font-weight: 800;
          margin-bottom: 25px;
          display: block;
          line-height: 2.65rem;

          @media @mobile {
            font-size: 1.85rem;
            line-height: 2rem;
            margin-bottom: 1.25rem;

            br { display: none; }
          }
        }
        p {
          font-weight: 600;
          font-size: 1.125rem;
          line-height: 1.625rem;
          color: @col-text-gray-dark;
        }
      }
      > svg {
        width: 300px;
        min-width: 300px;
        margin-left: 20px;

        @media @mobile {
          width: 100%;
          min-width: 0;
          margin: @mm 0 0;
        }
      }
    }
    > .rent-estimator-results {

      @media @mobile { padding: 0 @mm; }
      > .header {
        justify-content: space-between;
        align-content: center;
        align-items: center;
        margin-bottom: 40px;

        @media @mobile { display: block; }
        .address-row {
          justify-content: flex-start;
          align-content: center;
          align-items: baseline;

          @media @mobile {
            display: block;
            margin-bottom: @mm;
          }
          span { display: block; }
          .address {
            font-weight: 700;
            font-size: 1.875rem;
            margin-right: 20px;

            @media @mobile {
              font-size: 1.715rem;
              margin: 0 0 5px;
            }
          }
          .more {
            font-weight: 600;
            font-size: 1.125rem;
            color: @col-text-gray-darker;
          }
        }
        .rent-estimator-actions {
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
            overflow-x: auto;
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
              font-size: 1rem;

              &:hover, &:focus, &:active { background: lighten(@col-gray, 4%); }
            }
            .svg-icon {
              @s: 20px;

              width: @s;
              height: @s;
              display: block;
              margin: 0 auto .5rem;

              @media @mobile { margin: 0 7px 0 0; }
            }
          }
          > .mobile-mm:last-child {
            width: @mm - 8px;
            min-width: @mm - 8px;
          }
        }
      }
      .highlights {
        justify-content: space-between;
        align-items: stretch;
        align-content: stretch;
        margin-bottom: 90px;

        
        .details {
          width: 40%;
          margin-right: 20px;

          @media @mobile {
            width: 100%;
            margin: 0;
            display: flex;
            flex-wrap: nowrap;
            flex-direction: column-reverse;
            justify-content: stretch;
            align-content: flex-start;
          }
          > .fin-table {
            border: 1px solid @col-gray;
            border-radius: @border-radius;
            border-collapse: collapse;
            table-layout: fixed;
            border-style: hidden;
            box-shadow: 0 0 0 1px @col-gray;
            width: 100%;

            td {
              border: 1px solid @col-gray;
              padding: 15px;
              vertical-align: middle;

              &.rich-prop {
                text-align: center;

                .ui-small-prop {
                  display: inline-block;
                }
                img {
                  margin-top: 10px;
                  display: block;
                  height: 1.125rem;
                  width: 100%;
                }
              }
            }
          }
          .based-on {
            display: block;
            margin: 20px 0;
            font-size: 0.875rem;
            color: @col-text-gray-darker;
          }
          > svg {
            max-width: 300px;
            width: 100%;
          }
        }
        .map { flex: 1; }
        @media @mobile { margin-bottom: 30px; }
      }
      > .plots {
        flex-wrap: wrap;
        justify-content: space-between;
        align-items: flex-start;
        align-content: flex-start;
        
        .ui-plot {
          width: calc(50% - 20px);
          margin-bottom: 20px;
          min-height: calc(40vh*var(--vh));

          @media @mobile {
            width: 100%;
          }
        }
      }
      .map-list {
        margin: 50px 0 30px;
        width: 100%;

        @media @mobile {
          margin: 30px 0;
        }
        > .map {
          width: 100%;
          min-height: 450px;
          height: 55vh;
          margin-bottom: 20px;

          @media @mobile {
            height: 0;
            padding-bottom: 100%;
          }
        }
        > .markers-description {
          justify-content: flex-start;
          align-items: center;

          @media @mobile { flex-wrap: wrap; }
          .marker-info {
            justify-content: flex-start;
            align-items: center;
            color: @col-text-gray-dark;
            font-size: .875rem;

            .svg-icon {
              @s: 20px;

              width: @s;
              height: @s;
              margin-right: 5px;
            }
            @media @desktop {
              & + .marker-info { margin-left: 20px; }
            }
            @media @mobile {
              margin-right: 15px;
              margin-bottom: 15px;
              font-size: 1rem;
            }
          }
        }
        &.hide-mobile {
          margin: 0;
          width: auto;
          flex: 1;
          > .map { height: 100%; }
        }
      }
      .nearest-props {
        .heading {
          display: block;
          font-weight: 700;
          margin-bottom: 20px;
          font-size: 1.375rem;
        }
        > .ui-table {
          width: 100%;

          tr td:first-child {
            .svg-icon {
              margin-right: 10px;
              vertical-align: top;
            }
          }
          @media @mobile {
            tr {
              padding: 25px 0;
              grid-template-areas:
              "a a a a"
              ". . t t"
              ". . . .";

              td:first-child {
                grid-area: a;
                display: flex;
                justify-content: flex-start;
                align-items: flex-start;
                font-size: 1.143rem;
                line-height: 1.285rem;
              }
              td:last-child { grid-area: t; }
              td {
                font-size: 1.07rem;
              }
            }
          }
        }
      }
    }
  }
  .full-description {
    margin-top: 50px;
    margin-bottom: 70px;

    @media @mobile { padding: 0 @mm; }
    span.header {
      display: block;
      margin-bottom: 20px;
      font-weight: 700;
      font-size: 1.125rem;

      @media @mobile {
        text-align: center;
        font-size: 1.285rem;
      }
    }
    > p {
      font-weight: 400;
      line-height: 1.625rem;

      @media @mobile { font-size: 1.14rem; }
    }
  }
}
</style>


<script lang="ts">
import { defineComponent, watch } from 'vue';

import URadioChip from '@/components/ui/URadioChip.vue';
import UCollapsible from '@/components/ui/UCollapsible.vue';
import UButton from '@/components/ui/UButton.vue';
import UShare from '@/components/ui/UShare.vue';
import UDrop from '@/components/ui/UDrop.vue';
import USelectDrop from '@/components/ui/USelectDrop.vue';
import UDivider from '@/components/ui/UDivider.vue';
import USmallProp from '@/components/ui/USmallProp.vue';
import UAutocomplete from '@/components/ui/UAutocomplete.vue';
import UMessageList from '@/components/ui/UMessageList.vue';
import UMessage from '@/components/ui/UMessage.vue';
import UTextInput from '@/components/ui/UTextInput.vue';
import Footer from '@/components/static/footer.vue';
import USVGraph from './estimator-o-meter.vue';
import InfoWindowWrapper from '@/components/Property/InfoWindowWrapper.vue';

import Vue3ChartJs from '@j-t-mcc/vue3-chartjs';
import datalablesPlugin from 'chartjs-plugin-datalabels';
Vue3ChartJs.registerGlobalPlugins([datalablesPlugin]);

import envModel from '@/models/env.model';
import RentEstimatorModel from '@/models/RentEstimator';
import { TRentEstimate_Result, TRentEstimate_ResultTableRow } from '@/models/RentEstimator/api';
import AccountStore from '@/models/Account';

import { GoogleMap, Circle, Marker } from 'vue3-google-map';

import { toObject } from '@/models/Search';
import RentEstimator from '@/models/RentEstimator';
import { APP_DEFAULT_SMTH_BAD_FROM_SERVER } from '@/constants/DefaultMessages';

const searchModes = [ 'address', 'city' , 'zip' ];
const distanceDefs = [
  { label: 'Auto', value: 'auto' },
  { label: '0.1 miles', value: 0.1 },
  { label: '0.2 miles', value: 0.2 },
  { label: '0.33 miles', value: 0.33 },
  { label: '0.50 miles', value: 0.50 },
  { label: '0.75 miles', value: 0.75 },
  { label: '1 miles', value: 1 },
  { label: '1.5 miles', value: 1.5 },
  { label: '2 miles', value: 2 },
  { label: '3 miles', value: 3 },
  { label: '5 miles', value: 5 },
  { label: '10 miles', value: 10 }
];
const bedsDefs = [
  { label: 'Any', value: 'any' },
  { label: '0', value: '0' },
  { label: '1', value: '1' },
  { label: '2', value: '2' },
  { label: '3', value: '3' },
  { label: '4', value: '4' },
  { label: '5+', value: '5+' },
];
const bathsDefs = [
  { label: 'Any', value: 'any' },
  { label: '1', value: '1' },
  { label: '2', value: '2' },
  { label: '3', value: '3' },
  { label: '4+', value: '4+' },
];
const propTypes2Defs = [
  { label: 'Any', value: 'any' },
  { label: 'Condo & Apts.', value: 'condo-apt' },
  { label: 'Single Family', value: 'house-duplex' },
];
const lookBackDefs = [
  { label: '3 mo', value: 3 },
  { label: '6 mo', value: 6 },
  { label: '9 mo', value: 9 },
  { label: '12 mo', value: 12 },
  { label: '18 mo', value: 18 },
  { label: '24 mo', value: 24 },
  { label: '36 mo', value: 36 },
  { label: '48 mo', value: 48 },
];

export default defineComponent({
  components: {
    URadioChip,
    UCollapsible,
    UDrop,
    UButton,
    UShare,
    USelectDrop,
    UDivider,
    USmallProp,
    UAutocomplete,
    UMessageList,
    UMessage,
    UTextInput,
    Footer,
    Vue3ChartJs,
    USVGraph,
    GoogleMap,
    Circle,
    Marker,
    InfoWindowWrapper
  },
  computed: {
    Account() {
      return AccountStore;
    },
    rentDistributionPlot(this:any) {
      const plotData = this.result?.tables.histogram;

      if (!plotData)
        return null;

      let labels = plotData.titles;
      let data = plotData.values;
      
      return {
        type: 'bar',
        data: {
          labels,
          datasets: [{
            label: 'Offers',
            fill: true,
            backgroundColor: 'rgba(100, 84, 195, 0.1)',
            borderRadius: 8,
            data
          }]
        },
        options: {
          aspectRatio: 1.5,
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
          plugins: {
            legend: { display: false },
            datalabels: {
              align: 'end',
              anchor: 'end',
              color: '#222222'
            }
          }
        }
      }
    },
    bedroomTypePlot(this:any) {
      const plotData = this.result?.tables.rent_by_beds;

      if (!plotData)
        return null;

      let labels = plotData.titles;
      
      return {
        type: 'bar',
        data: {
          labels,
          datasets: [{
            type: 'bar',
            label: 'Offers',
            fill: true,
            backgroundColor: 'rgba(100, 84, 195, 0.1)',
            borderRadius: 8,
            data: plotData.offers,
            yAxisID: 'y',
            datalabels: {
              align: 'end',
              anchor: 'end',
              color: '#222222'
            }
          }, {
            type: 'line',
            label: 'Median Rent',
            fill: false,
            borderColor: '#01D092',
            pointRadius: 5,
            hoverRadius: 7,
            pointBorderWidth: 0,
            hoverBorderWidth: 0,
            pointBackgroundColor: '#01D092',
            data: plotData.median,
            yAxisID: 'y2',
            datalabels: { display: false }
          }]
        },
        options: {
          aspectRatio: 1.5,
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
              type: 'linear',
              position: 'left',
              grid: {
                drawBorder: false,
                color: "rgba(0, 0, 0, 0.02)"
              },
              ticks: { padding: 20 }
            },
            y2: {
              type: 'linear',
              position: 'right',
              grid: {
                drawOnChartArea: false
              },
              ticks: { padding: 20 }
            }
          },
          plugins: {
            legend: { display: false }
          }
        }
      }
    },
    buildingTypePlot(this:any) {
      const plotData = this.result?.tables.rent_by_type;

      if (!plotData)
        return null;

      let labels = plotData.titles;
      
      return {
        type: 'bar',
        data: {
          labels,
          datasets: [{
            type: 'bar',
            label: 'Offers',
            fill: true,
            backgroundColor: 'rgba(100, 84, 195, 0.1)',
            borderRadius: 8,
            data: plotData.offers,
            yAxisID: 'y',
            datalabels: {
              align: 'end',
              anchor: 'end',
              color: '#222222'
            }
          }, {
            type: 'line',
            label: 'Median Rent',
            fill: false,
            borderColor: '#01D092',
            pointRadius: 5,
            hoverRadius: 7,
            pointBorderWidth: 0,
            hoverBorderWidth: 0,
            pointBackgroundColor: '#01D092',
            data: plotData.median,
            yAxisID: 'y2',
            datalabels: { display: false }
          }]
        },
        options: {
          aspectRatio: 1.5,
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
              type: 'linear',
              position: 'left',
              grid: {
                drawBorder: false,
                color: "rgba(0, 0, 0, 0.02)"
              },
              ticks: { padding: 20 }
            },
            y2: {
              type: 'linear',
              position: 'right',
              grid: {
                drawOnChartArea: false
              },
              ticks: { padding: 20 }
            }
          },
          plugins: {
            legend: { display: false },
          }
        }
      }
    },
    homePriceTypePlot(this:any) {
      const plotData = this.result?.tables.rent_by_size;

      if (!plotData)
        return null;

      let labels = plotData.titles;
      
      return {
        type: 'bar',
        data: {
          labels,
          datasets: [{
            type: 'bar',
            label: 'Offers',
            fill: true,
            backgroundColor: 'rgba(100, 84, 195, 0.1)',
            borderRadius: 8,
            data: plotData.offers,
            yAxisID: 'y',
            datalabels: {
              align: 'end',
              anchor: 'end',
              color: '#222222'
            }
          }, {
            type: 'line',
            label: 'Median Rent',
            fill: false,
            borderColor: '#01D092',
            pointRadius: 5,
            hoverRadius: 7,
            pointBorderWidth: 0,
            hoverBorderWidth: 0,
            pointBackgroundColor: '#01D092',
            data: plotData.median,
            yAxisID: 'y2',
            datalabels: { display: false }
          }]
        },
        options: {
          aspectRatio: 1.5,
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
              type: 'linear',
              position: 'left',
              grid: {
                drawBorder: false,
                color: "rgba(0, 0, 0, 0.02)"
              },
              ticks: { padding: 20 }
            },
            y2: {
              type: 'linear',
              position: 'right',
              grid: {
                drawOnChartArea: false
              },
              ticks: { padding: 20 }
            }
          },
          plugins: {
            legend: { display: false },
          }
        }
      }
    },
    GAPI_KEY() {
      return envModel.VUE_APP_API_GOOGLE_MAP_TOKEN
    },
    showToggleCustomization(this:any) {
      return this.$isMobile.value && (this.result != null || this.queryInProgress);
    }
  },
  data() {
    const data = {
      query: {
        defaults: {
          prop_id: undefined as undefined | string,
          searchMode: searchModes[0],
          distance: distanceDefs[0],
          beds: bedsDefs[0],
          baths: bathsDefs[0],
          propType: propTypes2Defs[0],
          lookBack: lookBackDefs[3],
          building_size: undefined as undefined | number
        },
        customization: {
          prop_id: undefined as undefined | string,
          searchMode: searchModes[0],
          distance: distanceDefs[0],
          beds: bedsDefs[0],
          baths: bathsDefs[0],
          propType: propTypes2Defs[0],
          lookBack: lookBackDefs[3],
          building_size: undefined as undefined | number
        }
      },
      queryInProgress: false,
      plotsShow: false,
      report_in_progress: false,
      result: null as null | TRentEstimate_Result,
      searchModes,
      distanceDefs,
      bedsDefs,
      bathsDefs,
      propTypes2Defs,
      lookBackDefs,
      map1InfoWindowObject: null as any,
      map2InfoWindowObject: null as any,
      mapMarkers: [] as any[],
      mapInfoWindowMobileHeader: 'Property'
    };
    
    return data;
  },
  watch: {
    'query.customization.searchMode' (prevValue: string, newValue: string) {
      this.clearInput(prevValue, newValue);
    },
    'query.customization': {
      handler() {
        if (this.queryInProgress)
          return;
        setTimeout(() => { this.clearPropId(); }, 0);
      },
      deep: true
    }
  },
  methods: {
    clearPropId() {
      const curState = this.queryInProgress;
      this.queryInProgress = true;
      this.query.customization.prop_id = undefined;
      this.queryInProgress = curState;
    },
    async calculate() {
      if (this.queryInProgress || !AccountStore.Auth.inited)
        return;

      try {
        const toSaveObject = {
          address: (<any>this.$refs.queryAutoComplete).getSearchvalue(),
          options: {
            prop_id: this.query.customization.prop_id ? <any>this.query.customization.prop_id : undefined,
            propType: <any>this.query.customization.propType.value,
            distance: <any>this.query.customization.distance.value,
            beds: <any>this.query.customization.beds.value,
            baths: <any>this.query.customization.baths.value,
            lookBack: <any>this.query.customization.lookBack.value,
            building_size: <any>this.query.customization.searchMode == 'address' ? (<any>this.query.customization.building_size || undefined) : undefined,
            type: <any>this.query.customization.searchMode
          }
        }
        localStorage.setItem('ofirio-saved-after-login-data-after-login', JSON.stringify(toSaveObject));
        localStorage.setItem('ofirio-saved-after-login-url', JSON.stringify({ name: 'rent-estimator' }));
      } catch (ex) {}

      if (!AccountStore.Restrictions.canUseCustomization())
        return;

      this.queryInProgress = true;
      (<any>this.$refs).messageList.reset();

      this.result = null;
      const [ res, err ] = await RentEstimatorModel.query({
        query: (<any>this.$refs.queryAutoComplete).getSearchvalue(),
        prop_id: this.query.customization.prop_id ? <any>this.query.customization.prop_id : undefined,
        prop_type2: <any>this.query.customization.propType.value,
        distance: <any>this.query.customization.distance.value,
        beds: <any>this.query.customization.beds.value,
        baths: <any>this.query.customization.baths.value,
        look_back: <any>this.query.customization.lookBack.value,
        building_size: <any>this.query.customization.searchMode == 'address' ? (<any>this.query.customization.building_size || undefined) : undefined,
        type: <any>this.query.customization.searchMode
      });

      if (err) {
        (<any>this.$refs).messageList.push({
          type: 'warning',
          message: err
        });
        this.queryInProgress = false;
        return;
      }
    
      let markers = [];
      if (res && res.items) {
        let hashMap = <Record<string, TRentEstimate_ResultTableRow[]>>{};

        for (let m of res.items) {
          const coordsLength = 100000;
          let lat = Math.floor((m.lat as number)*coordsLength)/coordsLength;
          let lon = Math.floor((m.lon as number)*coordsLength)/coordsLength;
          const coordsCropped = `(${lat}, ${lon})`;

          hashMap[coordsCropped] = hashMap[coordsCropped] || [] as TRentEstimate_ResultTableRow[];
          hashMap[coordsCropped].push(m);
        }

        const keys = Object.keys(hashMap);
        for (let coord of keys) {
          let count:Array<[TRentEstimate_ResultTableRow['type'], number]> = [
            ['lower', 0],
            ['moderate', 0],
            ['higher', 0]
          ]
          hashMap[coord].forEach((m) => {
            let index = m.type == 'higher' ? 2 : (m.type == 'moderate' ? 1 : 0);
            count[index][1]++;
          });
          count.sort((a, b) => b[1] - a[1]);

          markers.push({
            position: { lat: hashMap[coord][0].lat, lng: hashMap[coord][0].lon },
            icon: count[0][0] == 'lower' ? '/mapMarkerIcons/rent-estimator-marker-green.svg' :
                  count[0][0] == 'moderate' ? '/mapMarkerIcons/rent-estimator-marker-blue.svg' :
                  count[0][0] == 'higher' ? '/mapMarkerIcons/rent-estimator-marker-red.svg' : 
                  '/mapMarkerIcons/rent-estimator-marker-blue.svg',
            list: hashMap[coord]
          });
        }
      }
      this.mapMarkers = markers;
      this.result = res;
      
      this.$nextTick(() => {
        this.queryInProgress = false;
        this.$nextTick(() => {
          //@ts-ignore
          if (this.$isMobile.value)
            this.toggleCustomizationCollapsible();
          else
            this.scrollToResult();
        })
        this.$nextTick(this.setMapBoundsAwaiter);
      });
    },
    toggleCustomizationCollapsible() {
      const customizationCollapsible = <any>this.$refs.customizationCollapsible;
      customizationCollapsible.toggle();
    },
    scrollToResult() {
      const br = (<any>this.$refs).diviredReady.$el.getBoundingClientRect();
      let offset = br.top + window.scrollY - 70;
      window.scrollTo({top: offset, behavior: 'smooth'});
    },
    clearInput(prevValue: string, newValue: string) {
      if (prevValue != newValue)
        (<any>this.$refs.queryAutoComplete).searchString = '';
    },
    setMapBoundsAwaiter() {
      const map1Ref = <any>this.$refs.map1Ref;
      const map2Ref = <any>this.$refs.map2Ref;

      if (map1Ref.ready && map2Ref.ready) {
        this.setMapBounds();
        map1Ref.map.setOptions({ mapId: '8e0a97af9386fef' });
        this.registerPopups(map1Ref, 1, 'map1InfoWindow');
        this.registerPopups(map2Ref, 2, 'map2InfoWindow');
        return;
      }

      const watchOnce = watch(() => map1Ref.ready && map2Ref.ready, (state: boolean) => {
        if (state != true)
          return;

        watchOnce();
        this.setMapBounds();
        
        map1Ref.map.setOptions({ mapId: '8e0a97af9386fef' });
        this.registerPopups(map1Ref, 1, 'map1InfoWindow');
        this.registerPopups(map2Ref, 2, 'map2InfoWindow');

      });
      
    },
    setMapBounds() {
      const map1Ref = <any>this.$refs.map1Ref;
      const map2Ref = <any>this.$refs.map2Ref;
      const GMApi = map1Ref.api;

      if (!this.result)
        return;

      const mapMarkers = this.result?.items;

      if (mapMarkers.length < 1)
        return;
      
      let bounds = new GMApi.LatLngBounds();
      for (let point of mapMarkers)
        bounds = bounds.extend({
          lat: point.lat,
          lng: point.lon
        });

      bounds.extend({
        lat: this.result.address.lat, lng: this.result.address.lon
      })

      map1Ref.map.fitBounds(bounds);
      map2Ref.map.fitBounds(bounds);
    },
    rentAnalyzerEvent() {
      window._learnq = window._learnq || [];
      window._learnq.push(['track', 'viewed page', {
        'page': 'rent analyzer'
      }]);
    },
    getReport() {

      if (this.report_in_progress || !AccountStore.Auth.inited)
        return;

      this.report_in_progress = true;

      let reportWindowReference = window;
      if ((<any>this).$isMobile.value)
        reportWindowReference.open("about:blank","_blank");

      RentEstimator.generateReport({
        query: (<any>this.$refs.queryAutoComplete).getSearchvalue(),
        prop_id: this.query.customization.prop_id ? <any>this.query.customization.prop_id : undefined,
        prop_type2: <any>this.query.customization.propType.value,
        distance: <any>this.query.customization.distance.value,
        beds: <any>this.query.customization.beds.value,
        baths: <any>this.query.customization.baths.value,
        look_back: <any>this.query.customization.lookBack.value,
        building_size: <any>this.query.customization.searchMode == 'address' ? (<any>this.query.customization.building_size || undefined) : undefined,
        type: <any>this.query.customization.searchMode
      })
      .then((res) => {
        //@ts-ignore
        if (res[1] === false) {
          (<any>this.$root).$refs.globMessages.push({ type: 'custom-rent-anal-limit-warning', message: 'You have reached your limits!' });
          return (<any>this.$root).$refs.popupUpgrade.open();
        }

        if (res[1] != null || !res[0])
          return (<any>this.$root).$refs.globMessages.push(APP_DEFAULT_SMTH_BAD_FROM_SERVER);

        if ((<any>this).$isMobile.value)
          reportWindowReference!.location.href = res[0].report_file;
        else
          reportWindowReference.open(res[0].report_file, '_blank');
      })
      .catch((ex) => {
        if ((<any>this).$isMobile.value)
          reportWindowReference!.close();
        return (<any>this.$root).$refs.globMessages.push(APP_DEFAULT_SMTH_BAD_FROM_SERVER);
      })
      .finally(() => {
        this.report_in_progress = false;
      });
    },
    restoreFromObject(object: Record<string, any>) {
      if (!object)
        return;

      if (object.address != undefined)
        (<any>this.$refs.queryAutoComplete).searchString = object.address;

      if (object.options) {
        const options = object.options;

        type Assad = [string, { label: string, value: any }[]];
        (<Assad[]>[
          ['searchMode', searchModes],
          ['distance', distanceDefs],
          ['beds', bedsDefs],
          ['baths', bathsDefs],
          ['propType', propTypes2Defs],
          ['lookBack', lookBackDefs]
        ]).forEach(row => {
          const [attr, dict]:Assad = row;

          let findValue:any = attr in options ? options[attr] : (<any>this.query.defaults)[attr];

          if (!findValue)
            return;

          for (let row of dict)
            if (row.value == findValue)
              return (<any>this.query.customization)[attr] = row;
          
        });

        if (options.building_size != undefined)
          this.query.customization.building_size = <number>options.building_size;

        if (options.prop_id != undefined)
          this.query.customization.prop_id = <string>options.prop_id;
      }
    },
    registerPopups(mapRef: any, index: number, refName: any) {
      const infoWindow = new mapRef.api.InfoWindow({
        content: (<any>this.$refs)[refName].$el
      });

      if (index == 1)
        //@ts-ignore
        this.map1InfoWindowObject = infoWindow;
      else if (index == 2)
        //@ts-ignore
        this.map2InfoWindowObject = infoWindow;
    },
    markerOnClick(map: number = 1, markers: any) {
      const mapRef = map == 1 ? (<any>this.$refs)?.map1Ref : (<any>this.$refs)?.map2Ref;
      const infoWindowObject = map == 1 ? this.map1InfoWindowObject : this.map2InfoWindowObject;
      const infoWindow = map == 1 ? (<any>this.$refs).map1InfoWindow : (<any>this.$refs).map2InfoWindow;
      const infoWindowMobile = map == 1 ? (<any>this.$refs).map1InfoWindowMobile : (<any>this.$refs).map2InfoWindowMobile;
      const infoWindowDrop = map == 1 ? (<any>this.$refs).map1InfoWindowMobileDrop : (<any>this.$refs).map2InfoWindowMobileDrop;

      if ((<any>this).$isMobile.value) {
        if (markers.length > 1)
          this.mapInfoWindowMobileHeader = `${markers[0].address.split(',')[0]} - ${markers.length} listings`;
        else
          this.mapInfoWindowMobileHeader = 'Property';

        infoWindowMobile.setProperties(markers);
        infoWindowDrop.open();
      } else {
        infoWindow.setProperties(markers);
        infoWindowObject.setPosition({
          lat: markers[0].lat,
          lng: markers[0].lon
        });
        infoWindowObject.open({ map: mapRef.map });
      }
    }
  },
  mounted() {
    const params = <Record<string, string>>this.$route.params;

    let savedParams;

    try {
      const isSaved = <Record<string, string>>JSON.parse(<string>(localStorage.getItem('ofirio-saved-after-login-active')));

      if (isSaved)
        savedParams = <Record<string, string>>JSON.parse(<string>(localStorage.getItem('ofirio-saved-after-login-data-after-login')));

      localStorage.removeItem('ofirio-saved-after-login-data-after-login');
      localStorage.removeItem('ofirio-saved-after-login-active');
      localStorage.removeItem('ofirio-saved-after-login-url');

    } catch (ex) {}

    if (params.address) {
      this.queryInProgress = true;

      this.query.customization.searchMode = searchModes[0];
      this.restoreFromObject({ address: params.address, options: toObject(params.options) })
      this.query.customization.lookBack = lookBackDefs[3];
      
      let watchOnce = () => {};

      if (!AccountStore.Auth.inited)
        watchOnce = watch(() => {
          return AccountStore.Auth.inited;
        }, (value) => {
          if (!value)
            return;
          watchOnce();
          this.queryInProgress = false;
          this.calculate();
        });
      else {
        this.$nextTick(() => {
          this.queryInProgress = false;
          this.calculate();
        });
      }


      const watchSearchChangedOnce = watch(() => {
        return (<any>this.$refs).queryAutoComplete.searchString;
      }, () => {
        watchSearchChangedOnce();
        this.clearPropId();
      });

    } else if (savedParams) {
      this.restoreFromObject(savedParams);
    }



    this.rentAnalyzerEvent();
  }
})
</script>