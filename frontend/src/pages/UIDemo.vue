<template>
  <div class="padded">
    <UCollapsible label="Checkbox">
      <UCheckbox required v-model="checkboxModel1">Test 1-1</UCheckbox>
      <div class="div">Group of checkboxes</div>
      <UCheckbox v-model="checkboxModel2">Test 2-1</UCheckbox>
      <UCheckbox v-model="checkboxModel2">Test 2-2</UCheckbox>
    </UCollapsible>


    <UCollapsible label="Togglers">
      <UToggle v-model="checkboxModel1" />
      <br>
      <br>
      <UToggle v-model="checkboxModel2" />
    </UCollapsible>


    <UCollapsible label="Radio">
      <URadio v-model="radioModel1" required name="radio-gr-1" value="a">Test 1-1</URadio>
      <URadio v-model="radioModel1" required name="radio-gr-1" value="b">Test 1-2</URadio>
      <div class="div">Radio with preselected</div>
      <URadio v-model="radioModel2" name="radio-gr-2" value="one">Test 2-1</URadio>
      <URadio v-model="radioModel2" name="radio-gr-2" value="two">Test 2-2</URadio>
    </UCollapsible>

    <UCollapsible label="Radio Chips">
      <URadioChip v-model="radioModel2" name="radio-gr-2" value="a">Test 1-1</URadioChip>
      <URadioChip v-model="radioModel2" name="radio-gr-2" value="b">Test 1-1</URadioChip>
      <URadioChip v-model="radioModel2" name="radio-gr-2" value="c">Test 1-1</URadioChip>
    </UCollapsible>


    <UCollapsible label="Select">
      <USelect v-model="selectModel1" :options="selectOptions"></USelect>
      <div class="div">Multiple select</div>
      <USelect v-model="selectModel2" :options="selectOptions" multiple></USelect>
      <div class="div">Multiple select with chips</div>
      <USelect v-model="selectModel2" :options="selectOptions" multiple taggable searchable></USelect>
      <div class="div-l"></div>
      <div class="div-l"></div>
    </UCollapsible>


    <UCollapsible label="Chips">
      <UChip>Chip #1</UChip>
      <UChip>Chip #2</UChip>
      <UChip>Chip #3</UChip>
    </UCollapsible>


    <UCollapsible label="Inputs">
      <UTextInput type="text" v-model="textModel1" prepend="Min" prefix="$" postfix="%" postpend="Max" />
      
      <div class="div">Basic input flexible</div>
      <UTextInput type="text" v-model="textModel1" prepend="Min" prefix="$" postfix="%" postpend="Max" flexible />
      <UTextInput type="text" v-model="textModel1" prepend="Min" prefix="$" postfix="%" vertical />
      <UTextInput type="text" v-model="textModel1" prepend="Min" prefix="$" postfix="%" flexible vertical />
      <div class="div">Basic input number</div>
      <UTextInput type="number" v-model="textModel2" prepend="Min" prefix="$" flexible />
      <div class="div">Basic input number with formatter</div>
      <UTextInput type="number" v-model="textModel2" prepend="Min" prefix="$" :formatter="$format['usd']"/>
      <div class="div">Basic input number with formatter in percent</div>
      <UTextInput type="number" subtype="percent" v-model="textModelPercent" prepend="Min" postfix="%" :formatter="$format['%']"/>
      <div class="div">Basic input custom input</div>
      <UTextInput type="number" v-model="textModel3" prepend="Min" postfix="%" flexible>
        <template v-slot:default="props">
          <input
            type="email"
            name="test"
            :value = "textModel3"
            @input="props.updateModel"
            @focus="props.isFocused = !0"
            @blur="props.isFocused = !1"
          >
        </template>
      </UTextInput>

      <UFloatingInput label="Label" v-model="textModel1" type="text"/>
    </UCollapsible>


    <UCollapsible label="Incremental input">
      <UIncremental v-model="incModel" prefix="$" :min="0" :max="9999" flexible />
      <UIncremental v-model="incModel" prefix="$" :min="0" :max="9999" label="Min" />
      <UIncremental v-model="incModel" prefix="$" :min="0" :max="9999" />
    </UCollapsible>


    <UCollapsible label="Links">
      <a href="#" class="ui-href ui-href-default">Default</a><br><br>
      <a href="#" class="ui-href ui-href-bold">Bold</a><br><br>
      <a href="#" class="ui-href ui-href-underline">Underline</a><br><br>
      <div style="background: #555; padding: 20px;">
        <a href="#" class="ui-href ui-href-underline ui-href-dark">Underline</a>
        <br>
        <a href="#" class="ui-href ui-href-default ui-href-dark">Default</a>
      </div>
    </UCollapsible>
    <UCollapsible label="Buttons">
      <UButton class="ui-btn-text">Text button #1</UButton>
      <UButton class="ui-btn-text" disabled>Text button #1</UButton>
      <br>
      <br>
      <UButton class="ui-btn-text ui-btn-text-black">Text button #2</UButton>
      <UButton class="ui-btn-text ui-btn-text-black" disabled>Text button #2</UButton>
      <br>
      <br>
      <UButton class="ui-btn-text ui-btn-text-gray">Text button #3</UButton>
      <UButton class="ui-btn-text ui-btn-text-gray" disabled>Text button #3</UButton>
      <br>
      <br>
      <UButton href="#" class="ui-btn-text ui-btn-iconic"><UIcon name="cross"/>Text button #3</UButton>
      <br>
      <br>
      <UButton class="ui-btn ui-btn-green">Button #1</UButton>
      <UButton class="ui-btn ui-btn-green" disabled>Button #1</UButton>
      <br>
      <br>
      <UButton class="ui-btn ui-btn-blue">Button #1</UButton>
      <UButton class="ui-btn ui-btn-blue" disabled>Button #1</UButton>
      <br>
      <br>
      <UButton class="ui-btn ui-btn-bordered">Button #2</UButton>
      <UButton class="ui-btn ui-btn-bordered" disabled>Button #2</UButton>
      <br>
      <br>
      <UButton class="ui-btn ui-btn-iconic ui-btn-circle"><UIcon name="cross"/></UButton>
      <UButton class="ui-btn ui-btn-iconic ui-btn-circle" disabled><UIcon name="cross"/></UButton>
      <br>
      <br>
      <UButton class="ui-btn ui-btn-iconic ui-btn-circle ui-btn-circle-on-dark"><UIcon name="cross"/></UButton>
      <br>
      <br>
      <UButton href="#" class="ui-btn ui-btn-green ui-btn-iconic"><UIcon name="cross"/>Button #3</UButton>
    </UCollapsible>

    <UCollapsible label="Drop">

      <div class="flex" style="justify-content: center">
        <UDrop ref="uiDrop1" label="Label">
          <template v-slot:content="props">
            <div class="uiDrop1-container">
              This is container.<br>
              <span @click="props.props.close"><UIcon name="cross" width="10px" height="10px" /></span>
            </div>
          </template>
        </UDrop>
        <div class="div-l"></div>
      </div>

    </UCollapsible>

    <UCollapsible label="Pagination">

      <UPagination v-model="paginationModel" :chunkSize="20" :dataCount="231" :startPage="4" class="demo-pagination" />
      showing {{ `${paginationModel[0]} - ${paginationModel[1]}` }}
    </UCollapsible>

    <UCollapsible label="Popup">
      <UButton class="ui-btn ui-btn-green" @click="() => $refs.popupDemo.open()">Open popup</UButton>
      <UPopup ref="popupDemo" class="demo-popup">
        <div class="content">
          Popup Content
          <br><br>
          <UButton class="ui-btn ui-btn-green" @click="() => $refs.popupDemo.close()">Close popup</UButton>
        </div>
      </UPopup>
    </UCollapsible>

    <UCollapsible label="Slider - One value">

      <div class="div-l"></div>
      <USlider v-model="sliderModelMono" :tooltips="false" :stops="[0.25, 0.5, 0.75]" :stopsVisible="[1,0,1]" :stopBuffer="5" :min="20" :max="100" showPercentiles />
      <br>
      {{ sliderModelMono }}
      <div class="div-l"></div>

    </UCollapsible>

    <UCollapsible label="Slider - Two values">

      <div class="div-l"></div>
      <USlider v-model="sliderModel" :tooltips="false" :stops="[0.75]" :stopBuffer="5" :min="20" :max="100"/>
      <br>
      from {{ sliderModel[0] }} to {{ sliderModel[1] }}
      <div class="div-l"></div>

    </UCollapsible> 

    <UCollapsible label="Slider w/ histogram - In progress">
      <div class="div-l"></div>
      <!-- <UHistogramSlider
        v-model="sliderModel"
        :histArray="histogramArray"
        :processArray="true"
        :min="1"
        :max="200"
      /> -->
      <br>
      from {{ sliderModel[0] }} to {{ sliderModel[1] }}
      <div class="div-l"></div>
    </UCollapsible>

    <UCollapsible label="Message">
      <UMessage type="error" text="This is an example message" />
      <UMessage type="warning" text="This is an example message" />
      <UMessage type="success" text="This is an example message" />
      <UMessage type="info" text="This is an example message" />
    </UCollapsible>

    <UCollapsible label="Message List">
      <UMessageList :initialList="messageList" :initialDelay="30000" />
    </UCollapsible>

    <UCollapsible label="Tables">
      <table class="ui-table">
        <tr>
          <th>Column 1</th>
          <th>Column 2</th>
          <th>Column 3</th>
          <th>Column 4</th>
          <th>Column 5</th>
        </tr>
        <tr>
          <td>Data 1-1</td>
          <td>Data 1-2</td>
          <td>Data 1-3</td>
          <td>Data 1-4</td>
          <td>Data 1-5</td>
        </tr>
        <tr>
          <td>Data 2-1</td>
          <td>Data 2-2</td>
          <td>Data 2-3</td>
          <td>Data 2-4</td>
          <td>Data 2-5</td>
        </tr>
        <tr>
        <td>Data 3-1</td>
        <td>Data 3-2</td>
        <td>Data 3-3</td>
        <td>Data 3-4</td>
        <td>Data 3-5</td>
        </tr>
        <tr>
        <td>Data 4-1</td>
        <td>Data 4-2</td>
        <td>Data 4-3</td>
        <td>Data 4-4</td>
        <td>Data 4-5</td>
        </tr>
      </table>
      <div class="div-l"></div>
      <table class="ui-table ui-table--stripped">
        <tr>
          <th>Column 1</th>
          <th>Column 2</th>
          <th>Column 3</th>
          <th>Column 4</th>
          <th>Column 5</th>
        </tr>
        <tr>
          <td>Data 1-1</td>
          <td>Data 1-2</td>
          <td>Data 1-3</td>
          <td>Data 1-4</td>
          <td>Data 1-5</td>
        </tr>
        <tr>
          <td>Data 2-1</td>
          <td>Data 2-2</td>
          <td>Data 2-3</td>
          <td>Data 2-4</td>
          <td>Data 2-5</td>
        </tr>
        <tr>
        <td>Data 3-1</td>
        <td>Data 3-2</td>
        <td>Data 3-3</td>
        <td>Data 3-4</td>
        <td>Data 3-5</td>
        </tr>
        <tr>
        <td>Data 4-1</td>
        <td>Data 4-2</td>
        <td>Data 4-3</td>
        <td>Data 4-4</td>
        <td>Data 4-5</td>
        </tr>
      </table>
      <div class="div-l"></div>
    </UCollapsible>


    <UCollapsible label="Small props">
      <div class="div-l"></div>
      <USmallProp :value="0.26" label="CAP rate" postfix="%" />
      <USmallProp :value="0.26" label="CAP rate" postfix="%" color="#01D755"/>
      <div class="div-l"></div>
    </UCollapsible>

  </div>
</template>

<script lang="ts">
import UCheckbox from '@/components/ui/UCheckboxInput.vue';
import URadio from '@/components/ui/URadioInput.vue';
import USelect from '@/components/ui/USelect.vue';
import UChip from '@/components/ui/UChip.vue';
import UTextInput from '@/components/ui/UTextInput.vue';
import UFloatingInput from '@/components/ui/UFloatingInput.vue';
import UIncremental from '@/components/ui/UIncremental.vue';
import UButton from '@/components/ui/UButton.vue';
import UCollapsible from '@/components/ui/UCollapsible.vue';
import USlider from '@/components/ui/USlider.vue';
import UHistogramSlider from '@/components/ui/UHistogramSlider.vue';
import UDrop from '@/components/ui/UDrop.vue';
import UPagination from '@/components/ui/UPagination.vue';
import UPopup from '@/components/ui/UPopup.vue';
import UMessage from '@/components/ui/UMessage.vue';
import UMessageList from '@/components/ui/UMessageList.vue';
import USmallProp from '@/components/ui/USmallProp.vue';
import UToggle from '@/components/ui/UToggle.vue';
import URadioChip from '@/components/ui/URadioChip.vue';



import { defineComponent } from 'vue';

export default defineComponent({
  components: {
    UCheckbox,
    URadio,
    USelect,
    UChip,
    UTextInput,
    UIncremental,
    UButton,
    UCollapsible,
    USlider,
    UDrop,
    UPagination,
    UPopup,
    UHistogramSlider,
    UFloatingInput,
    UMessage,
    UMessageList,
    USmallProp,
    UToggle,
    URadioChip
  },

  data() {
    return {
      checkboxModel1: false,
      checkboxModel2: true,
      radioModel1: undefined,
      radioModel2: 'one',
      selectModel1: undefined,
      selectModel2: [],
      selectOptions: ['Good', 'Better', 'The best'],
      textModel1: 'TestValue',
      textModel2: undefined,
      textModel3: 0,
      textModelPercent: 0,
      incModel: 0,
      sliderModelMono: 20,
      sliderModel: [20, 40],
      paginationModel: [],
      histogramArray: Array(200).fill(!1).map(e => Math.random()),
      _rndInterval: undefined,
      messageList: [
        { type: 'error', message: Date.now().toString() },
        { type: 'warning', message: Date.now().toString() },
        { type: 'error', message: Date.now().toString() },
        { type: 'error', message: Date.now().toString() },
        { type: 'error', message: Date.now().toString() },
        { type: 'error', message: Date.now().toString() },
        { type: 'error', message: Date.now().toString() }
      ]
    };
  },
  mounted() {
    // this._rndInterval = <any>setInterval(() => {
    //   this.histogramArray = Array(200).fill(!1).map(e => Math.random());
    // }, 500);
  },
  beforeUnmount() {
    clearInterval(this._rndInterval);
  }
});
</script>

<style lang="less" scoped>
  .div {
    margin: 30px 0;
  }
  .div-l {
    margin-top: 100px;
    padding: 50px 0;
  }
  .ui-collapsible {
    margin-bottom: 10px;
    border-bottom: 2px solid @col-gray;
    padding: 10px 0;

    &::v-deep .container { padding: 5px; }
  }
  .demo-pagination { width: fit-content; }
  .uiDrop1-container { padding: 20px; white-space: nowrap; }
</style>