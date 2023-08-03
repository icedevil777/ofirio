import { of } from 'await-of';

export default function CornAndPopcornAwaiter() {
  return function (target: Object, key: string | symbol, descriptor: PropertyDescriptor) {
    const original = descriptor.value;
    descriptor.value = function(...args: any[]) {
      return of(original.apply(this, args));
    };
    return descriptor;
  };
}