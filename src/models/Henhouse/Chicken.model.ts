import { Egg, EggEnum } from '@/models/Henhouse/Egg.model';
import { computed, ComputedRef, toRaw } from 'vue';

function navigator(egg: Egg<any> | EggEnum<any> | Record<string, any>, cb: Function, path: Array<string> = []) {
  if (egg instanceof Egg || egg instanceof EggEnum)
    return cb(egg, path);

  for (let key of Object.keys(egg))
    if (!navigator(egg[key], cb, path.concat([key])))
      return false;
}

export default function Chicken<T, K>(initObject: T, actions?: K) {
  const $hasErrors = computed(() => {
    function hasErrors(egg: Egg<any> | EggEnum<any> | Record<string, any>): boolean {
      let has = false;

      navigator(egg, (_egg: Egg<any> | EggEnum<any>) => {
        if (_egg.hasError.value)
          return !(has = true);

        return true;
      });

      return has;
    }

    return hasErrors(initObject);
  });

  const $getSnapshot = (fetchRaw: boolean = true) => {
    let result = {} as Record<keyof T, any>;
    navigator(initObject, (egg: Egg<any> | EggEnum<any>, path: Array<keyof T>) => {
      let obj = result;
      const last = <keyof T>path.pop();
      for (let key of path) {
        if (obj[key] == undefined)
          obj[key] = {};
          obj = obj[key];
      }

      if (fetchRaw)
        obj[last] = egg instanceof EggEnum ? egg.rawValue.value?.value : egg.rawValue.value;
      else
        obj[last] = egg.value.value;

      obj[last] = toRaw(obj[last]);

      return true;
    });
    return result;
  }

  const $getDiff = () => {
    
  }

  const $setValues = (obj: Record<string, any>) => {
    for (let k in obj) {
      
    }
  }

  return Object.assign({}, initObject, actions || {}, {
    $hasErrors,
    $getSnapshot
  });
}