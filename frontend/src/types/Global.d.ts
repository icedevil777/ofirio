type TypeExtender<T, U> = U & Omit<T, keyof U>;

type GetFunctionArgs<T> = T extends new (...args: infer U) => any ? U : never