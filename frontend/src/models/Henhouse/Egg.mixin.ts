import { Egg, EggEnum } from '@/models/Henhouse/Egg.model';
import { debounce, throttle } from 'throttle-debounce-ts';
import { defineComponent, PropType } from 'vue';

export function EggMixin<T>(init: GetFunctionArgs<typeof Egg>[0]) {
  return {
    data() {
      return {
        egg: new Egg(init)
      }
    }
  }
}

export function EggEnumMixin<T>(init: GetFunctionArgs<typeof EggEnum>[0]) {
  return {
    data() {
      return {
        egg: new EggEnum(init)
      }
    }
  }
}

export const EggInputModel = defineComponent({
  inheritAttrs: false,
  props: {
    egg: { required: true, type: Object },
    jitter: {
      default: 'throttle',
      type: String as PropType<'throttle' | 'debounce' | 'reactive' | 'blur'>,
      validator: (value: string) => {
        return ['throttle', 'debounce', 'reactive', 'blur'].includes(value);
      }
    },
    jitterTime: { default: 500, type: Number },
    
    name: {
      default: () => {
        return 'input__' + (Date.now() + Math.round((Math.random() * 100)) );
      },
      type: String
    },

    customAttributes: Object,
    noValidationMessages: Boolean,
    flexible: Boolean,

    placeholder: String,
    readonly: { type: [String, Boolean] },
    disabled: { type: [String, Boolean] }
  },
  data() {
    let updateFn = (value: any) => { this.egg.value = value; }

    if (this.jitter == 'throttle')
      updateFn = throttle({ delay: this.jitterTime, trailing: true }, updateFn);
    else if (this.jitter == 'debounce')
      updateFn = debounce(this.jitterTime, updateFn);

    return {
      isFocused: false,
      internalValue: '' as any,
      appendAttributes: Object.assign({}, this.customAttributes || {}) as Record<string, string>,
      updateFn
    }
  },
  watch: {
    'egg.value'(newValue) {
      if (!this.isFocused)
        this.internalValue = this.egg.getValue();
    }
  },

  methods: {
    onFocus() {
      this.isFocused = true;
      this.internalValue = this.egg.getValue();
    },
    onBlur() {
      this.isFocused = false;

      if (this.jitter == 'blur')
        this.updateFn(this.internalValue);
      this.internalValue = this.egg.getValue();
    },
    focus() {
      this.onFocus();
      (<any>this.$refs.input).focus();
    },
    onInput(e:any) {
      if (this.jitter != 'blur')
        this.updateFn(this.internalValue);
    }
  },
  mounted() {
    this.internalValue = this.egg.getValue();
  }
});

export const EggMultiChoiseInputModel = defineComponent({
  mixins: [ EggInputModel ],
  props: {
    value: String,
    jitter: { default: 'reactive' }
  },
  computed: {
    isChecked():boolean {
      const value = this.egg.rawValue;

      if (this.value)
        return value.includes(this.value);
      else
        return !!value;
    }
  }
});