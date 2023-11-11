import { Ref, computed, ref, toRaw } from 'vue';
import { ValidationError as TValidationError, BaseSchema, BooleanSchema, StringSchema, NumberSchema, DateSchema } from 'yup';

type TValidator = BaseSchema | BooleanSchema | StringSchema | NumberSchema | DateSchema;


type TEggConstructorOptions<T> = Partial<{
  type: Egg<T>['type'],
  min: number,
  max: number,
  initialValue: Egg<T>['internalValue']['value'],
  defaultValue: Egg<T>['defaultValue']['value'],
  disabled: Egg<T>['disabled']['value'],
  readonly: Egg<T>['readonly']['value'],
  validators: Egg<T>['validators'],
  parser: Egg<T>['parser'],
  printer: Egg<T>['printer']
}>;

export class Egg<T> {
  /** constructor */
  constructor(init?: TEggConstructorOptions<T>) {
    if (!init)
      return;

    this.internalValue.value = init.initialValue;

    if (init.defaultValue)
      this.defaultValue.value = init.defaultValue;

    if (init.disabled)
      this.disabled.value = init.disabled;

    if (init.readonly)
      this.readonly.value = init.readonly;

    if (init.validators)
      this.validators = init.validators;

    if (init.min != undefined)
      this.min.value = init.min;

    if (init.max != undefined)
      this.max.value = init.max;

    if (init.type)
      this.type = init.type;

    if (init.parser)
      this.parser = init.parser;

    if (init.printer)
      this.printer = init.printer;

    this.validate();
  }

  /** values */
  protected defaultValue:Ref<T | undefined> = ref(undefined);
  protected internalValue:Ref<T | undefined> = ref(undefined);

  public rawValue = computed({
    get: () => {
      return this.internalValue.value;
    },
    set: (v: T | undefined) => {
      if (this.disabled.value || this.readonly.value)
        return;
        
      if (this.internalValue.value != v)
        this.pristine.value = false;

      this.internalValue.value = v;
      this.touched.value = true;
      this.validate();
    }
  });

  public value = computed({
    get: () => {
      return this.print();
    },
    set: (v: T) => {
      if (this.disabled.value || this.readonly.value)
        return;

      this.parse(v);
      this.touched.value = true;
      this.validate();
    }
  });

  public readonly getValue: () => T = () => {
    return toRaw(this.value.value);
  };


  /** props */
  readonly type: 'any' | 'number' = 'any';
  readonly inputType: string = 'text';

  public min = ref(-Infinity);
  public max = ref(+Infinity);

  readonly valid = ref(false);
  readonly invalid = computed(() => { return !this.valid.value; });

  readonly pending = ref(false);

  readonly readonly = ref(false);
  readonly editable = computed(() => { return !this.readonly.value; });

  readonly disabled = ref(false);
  readonly enabled = computed(() => { return !this.disabled.value; });
  
  readonly pristine = ref(false);
  readonly dirty = computed(() => { return !this.pristine.value; });
  
  readonly touched = ref(false);
  readonly untouched = computed(() => { return !this.touched.value; });
  
  protected validators:Array<TValidator> = [];
  readonly errors:Ref<Array<TValidationError>> = ref([]);


  /** methods */
  public readonly reset = () => {
    if (this.disabled.value)
      return;

    this.internalValue.value = this.defaultValue.value;
    this.pristine.value = true;
    this.touched.value = false;
    this.validate();
  };

  protected parse = (value: any) => {
    let newValue = this.parser(value);

    if (this.type == 'number') {
      newValue = <T><unknown>Math.min(<number><unknown>newValue, this.max.value);
      newValue = <T><unknown>Math.max(<number><unknown>newValue, this.min.value);

      if (isNaN(<number><unknown>newValue))
        newValue = <T><unknown>this.min.value;
    }

    if (this.internalValue.value != newValue)
      this.pristine.value = false;

    return this.internalValue.value = newValue;
  };

  public parser(value: any): T | undefined {
    if (this.type == 'number')
      return <T><unknown>parseFloat(value);
      
    return <T><unknown>value;
  };

  protected readonly print = () => {
    return this.printer(this.internalValue.value);
  };

  public printer(value: Egg<T>['internalValue']['value']) {
    return value ? (<any>value).toString() : value;
  };

  public readonly setDisabled: (value: boolean) => void = (value:boolean) => {
    this.disabled.value = value;
  };

  public readonly setReadonly: (value: boolean) => void = (value:boolean) => {
    this.readonly.value = value;
  };

  public readonly setDefault: (value: T) => void = (value: T) => {
    this.defaultValue.value = value;
  };

  public readonly hasError:Ref<boolean> = computed(() => {
    return this.errors.value.length > 0;
  });

  public readonly getError: () => TValidationError = () => {
    return this.errors.value[0];
  };

  public readonly addError: (err: TValidationError) => void = (err:TValidationError) => {
    this.errors.value.push(err);
  }

  public readonly validate: () => void = async () => {
    let results = await Promise.allSettled(this.validators.map(v => v.validate(this.internalValue.value)));
    let errors = results.filter(res => res.status == 'rejected').map(e => (<PromiseRejectedResult>e).reason?.message);
    this.errors.value = errors;
    this.valid.value = this.errors.value.length === 0;
  }

}

type TEnumArrayElement<T> = {
  $id: number,
  label?: string,
  value: T
};

type TEggEnumConstructorOptions<T> = TypeExtender<TEggConstructorOptions<TEnumArrayElement<T>>, {
  enum: Array<Omit<TEnumArrayElement<T>, '$id'>>,
  initialEnumIndex: number,
  defaultEnumIndex: number
}>;

export class EggEnum<T> extends Egg<TEnumArrayElement<T>> {
  /** constructor */
  constructor(init?: TEggEnumConstructorOptions<T>) {
    super(init);

    if (!init)
      return;
    
    this.enum = init.enum.map((e, i) => {
      return Object.assign({}, e, { $id: i });
    });

    this.internalValue.value = this.enum[init.initialEnumIndex];
    this.defaultValue.value = this.enum[init.defaultEnumIndex];
  }

  /** values */
  public readonly enum: Array<TEnumArrayElement<T>> = [];

  protected defaultValue:Ref<TEnumArrayElement<T> | undefined> = ref(undefined);
  protected internalValue:Ref<TEnumArrayElement<T> | undefined> = ref(undefined);

  public rawValue = computed({
    get: () => {
      return this.internalValue.value;
    },
    set: (v: TEnumArrayElement<T> | undefined) => {
      if (this.disabled.value)
        return;

      if (v != undefined)
        if (!this.enum.includes(v)) {
          let foundIndex = this.enum.findIndex(e => e.$id === v.$id);
          if (foundIndex === -1)
            return;
        }
        
      if (this.internalValue.value?.value != v?.value)
        this.pristine.value = false;

      this.internalValue.value = v;
      this.touched.value = true;
      this.validate();
    }
  });

  public value = computed({
    get: () => {
      return this.print();
    },
    set: (v: any) => {
      if (this.disabled.value)
        return;

      this.parse(v);
      this.touched.value = true;
      this.validate();
    }
  });

  
  /** methods */
  protected parse = (value: any) => {
    const newValue = this.parser(value);

    if (this.internalValue.value?.value != newValue)
      this.pristine.value = false;

    return this.internalValue.value = newValue;
  };

  public parser = (value: T) => {
    return this.enum.find(e => e.value === value);
  };

  public printer(value: TEnumArrayElement<T> | undefined) {
    if (value)
      if (value.label)
        return value.label;
      else
        return value.value;

    return value;
  };

  public readonly validate: () => void = async () => {
    let results = await Promise.allSettled(this.validators.map(v => v.validate(this.internalValue.value?.value)));
    let errors = results.filter(res => res.status == 'rejected').map(e => (<PromiseRejectedResult>e).reason?.message);
    this.errors.value = errors;
    this.valid.value = this.errors.value.length === 0;
  }

}

type TEggMultiEnumConstructorOptions<T> = TypeExtender<TEggConstructorOptions<Array<TEnumArrayElement<T>>>, {
  enum: Array<Omit<TEnumArrayElement<T>, '$id'>>,
  initialEnumIndexes: number[],
  defaultEnumIndexes: number[]
}>;
/*
export class EggMultiEnum<T> extends Egg<Array<TEnumArrayElement<T>>> {
  /** constructor *//*
  constructor(init?: TEggMultiEnumConstructorOptions<T>) {
    super(init);

    if (!init)
      return;
    
    this.enum = init.enum.map((e, i) => {
      return Object.assign({}, e, { $id: i });
    });

    this.internalValue.value = [];
    for (let i of init.initialEnumIndexes)
      this.internalValue.value.push(this.enum[i]);

    this.defaultValue.value = [];
    for (let i of init.defaultEnumIndexes)
      this.defaultValue.value.push(this.enum[i]);
  }

  /** values *//*
  public readonly enum: Array<TEnumArrayElement<T>> = [];

  protected defaultValue:Ref<Array<TEnumArrayElement<T>> | undefined> = ref(undefined);
  protected internalValue:Ref<Array<TEnumArrayElement<T>> | undefined> = ref(undefined);

  public rawValue = computed({
    get: () => {
      return this.internalValue.value;
    },
    set: (v: Array<TEnumArrayElement<T>> | undefined) => {
      if (this.disabled.value)
        return;

      this.pristine.value = false;

      this.internalValue.value = v;
      this.touched.value = true;
      this.validate();
    }
  });

  public value = computed({
    get: () => {
      return this.print();
    },
    set: (v: any) => {
      if (this.disabled.value)
        return;

      this.parse(v);
      this.touched.value = true;
      this.validate();
    }
  });

  
  /** methods *//*
  protected parse = (value: any) => {
    const newValue = this.parser(value);

    if (this.internalValue.value?.value != newValue)
      this.pristine.value = false;

    return this.internalValue.value = newValue;
  };

  public parser = (value: T) => {
    return this.enum.find(e => e.value === value);
  };

  public printer(value: TEnumArrayElement<T> | undefined) {
    if (value)
      if (value.label)
        return value.label;
      else
        return value.value;

    return value;
  };

  public readonly validate: () => void = async () => {
    let results = await Promise.allSettled(this.validators.map(v => v.validate(this.internalValue.value?.value)));
    let errors = results.filter(res => res.status == 'rejected').map(e => (<PromiseRejectedResult>e).reason?.message);
    this.errors.value = errors;
    this.valid.value = this.errors.value.length === 0;
  }

}*/