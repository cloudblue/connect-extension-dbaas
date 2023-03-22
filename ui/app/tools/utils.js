import {
  T,
  __,
  all,
  anyPass,
  applyTo,
  chain,
  complement,
  cond,
  curry,
  equals,
  fromPairs,
  identity,
  ifElse,
  is,
  isEmpty,
  isNil,
  map,
  or,
  path,
  pipe,
  prop,
  props,
  replace,
  split,
  toLower,
  toPairs,
  trim,
  type,
  useWith,
  when,
} from 'ramda';


/**
 * Flattens nested object properties.
 *
 * @function
 * @param {object} source Source object.
 * @returns {object}
 *
 * @example
 * flattenObj({ a: { b: B, c: C } }) //=> { 'a.b': B, 'a.c': C }
 */
export const flattenObj = (source) => {
  const go = obj_ => chain(([k, v]) => {
    if (type(v) === 'Object' || type(v) === 'Array') {
      return map(([k_, v_]) => [`${k}.${k_}`, v_], go(v));
    }

    return [[k, v]];
  }, toPairs(obj_));

  return fromPairs(go(source));
};

/**
 * Returns first truthy value of two property paths.
 * If there is no truthy value returns last of two.
 *
 * @function
 * @param {array} propPath
 * @param {array} altPropPath
 * @param {object} source
 * @returns {*}
 *
 * @example
 * pathOrPath([a, b], [c], { a: [ b: B ], c: C }) //=> B
 * pathOrPath([a, b], [c], { c: C }) //=> C
 */
export const pathOrPath = curry((a, b, source) => or(path(a, source), path(b, source)));

/**
 * Invokes `cb` function with value retrieved from `target` at a given path
 * and returns result of `cb`.
 *
 * @function
 * @param {array} path Prop path.
 * @param {function} cb Callback function.
 * @param {object} target Target object.
 * @returns {*} Result of `cb` call.
 *
 * @example
 * pathTo(['a', 'b'], a => a * 2, { a: { b: 2 } }) //=> 4
 */
export const pathTo = curry((p, cb, target) => pipe(path(p), cb)(target));

/**
 * Check that given value is object.
 *
 * @function
 * @param {object} value
 * @returns {boolean}
 *
 * @example
 * isObjectStrict({}) //=> true
 * isObjectStrict(1) //=> false
 */
export const isObjectStrict = pipe(type, equals('Object'));

/**
 * Verify all elements are number or string.
 *
 * @function
 * @param {array} arr
 * @returns {boolean}
 */
const isAllPrimitive = all(anyPass([is(Number), is(String)]));

/**
 * Returns new object based on a template.
 * Supports nested objects.
 *
 * @function
 * @param {object} template
 * @param {object} source
 * @returns {object}
 *
 * @example
 * template(
 *  {
 *    id: path(['data', 'uuid'])
 *  },
 *  { data: { uuid: 42 } }
 * ) //=> { id: 42 }
 *
 * @example #2
 * template({
 *   id: ['data', 'uuid'],
 *   title: ['data', 'details', 'title'],
 * })
 * ({
 *  data: {
 *    uuid: 53,
 *    details: {
 *      title: 'hello world!',
 *      amount: 10,
 *    },
 *  }
 * })  //=> { id: 53, title: 'hello world!' }
 */
export const template = curry((tpl, src) => {
  /* eslint-disable no-use-before-define */
  function processTpl(v) {
    return map(cond([
      // Result of function
      [is(Function), applyTo(src)],

      // Empty is constant data
      [isEmpty, identity],

      // Array may be path or template
      [is(Array), processArray],

      // Object is always template part
      [isObjectStrict, template(__, src)],

      // Everything else is constant data
      [T, identity],
    ]))(v);
  }

  function processArray(v) {
    return cond([
      // if array is path
      [isAllPrimitive, path(__, src)],

      // In other cases array is template part
      [T, processTpl],
    ])(v);
  }

  return processTpl(tpl);
});

/**
 * Calls `onTrueFn` if value at given path is truthy, otherwise `onFalseFn`.
 * Functions will be invoked with `source` object as first argument.
 *
 * @function
 * @param {array} path
 * @param {function} onTrueFn
 * @param {function} onFalseFn
 * @param {object} source
 * @returns {*}
 *
 * @example
 * pathIfElse(
 *  ['a', 'b'],
 *  () => 1,
 *  () => 2
 * )({ a: { b: 0 } })
 * //=> 2
 */
export const pathIfElse = curry((p, i, e) => pathTo(p, ifElse(identity, i, e)));

/**
 * Calls `fn` with `props` values as first argument and returns result of that call.
 *
 * @function
 * @param {array} props
 * @param {function} fn
 * @param {object} source
 * @returns {*}
 *
 * @example
 * propsTo(['a', 'b'], (props) => props, { a: 1, b: 2 }) //=> [1, 2]
 */
export const propsTo = curry((p, cb, source) => pipe(props(p), cb)(source));

/**
 * Returns value based on condition.
 * If truthy returns first, otherwise second.
 * Condition could be function, in this case returns a function that after call
 * invokes condition function with actual arguments and apply to `alt`.
 *
 * @function
 * @param {*} a Value if condition is true
 * @param {*} b Value if condition is false
 * @param {*} cond Condition
 * @returns {*}
 */
export const alt = curry((t, f, c) => {
  if (is(Function, c)) {
    return (...v) => alt(t, f, c(...v));
  }

  return c ? t : f;
});

/**
 * Returns `true` if value is empty, `null` or `undefined`, otherwise `false`.
 *
 * @function
 * @param {*} value
 * @returns {boolean}
 *
 * @example
 * isNilOrEmpty({}) //=> true
 * isNilOrEmpty([1]) //=> false
 */
export const isNilOrEmpty = anyPass([isEmpty, isNil]);

/**
 * Returns `true` if value is not empty and not `null`/`undefined`, otherwise `false`.
 *
 * @function
 * @param {*} value
 * @returns {boolean}
 */
export const isNotNilOrEmpty = complement(isNilOrEmpty);

/**
 * Checks truthiness of a property.
 * Returns true if property value is falsy.
 *
 * @function
 * @param {string} prop
 * @param {object}
 * @returns {boolean}
 *
 * @example
 * notProp('country', { country: '' }) //=> true
 * notProp('country', { country: 'France' }) //=> false
 */
export const notProp = complement(prop);

/**
 * Returns new empty object.
 *
 * @function
 * @returns {object}
 */
export const obj = () => ({});

/**
 * If value is truthy at given path return `t` value, `f` otherwise.
 *
 * @function
 * @param {array} path
 * @param {*} t Value returned if path value is truthy
 * @param {*} f Value returned if path value is falsy
 * @param {object} target Target object
 * @returns {*}
 *
 * @example
 * pathAlt(['a', 'b'], true, false, {}) //=> false
 * pathAlt(['a', 'b'], 'pass', 'fail', { a: { b: 42 } }) //=> 'pass'
 */
export const pathAlt = curry((p, t, f) => pathTo(p, alt(t, f)));

/**
 * Invokes `cb` function with value retrieved from `target` at a given prop
 * and returns result of `cb`.
 *
 * @function
 * @param {array} Prop name.
 * @param {function} cb Callback function.
 * @param {object} target Target object.
 * @returns {*} Result of `cb` call.
 *
 * @example
 * propTo('a', a => a * 2, { a: 2 }) //=> 4
 */
export const propTo = curry((p, cb, target) => pipe(prop(p), cb)(target));

/**
 * Curried
 * If string is passed - splits with provided separator
 * If passed value is not a string - returns as is
 *
 * @function
 * @param {string} s Separator.
 * @param {*} str Target string.
 * @returns {*}
 *
 * @example
 * safeSplit('.', 'a.b.c') //=> ['a', 'b', 'c']
 * safeSplit('.', ['a', 'b', 'c') //=> ['a', 'b', 'c']
 */
export const safeSplit = curry((s, str) => when(is(String), split(s))(str));

/**
 * Returns a value at a given path. Path must be in dot notation: `coords.lat`.
 *
 * @function
 * @param {string} path Property path in dot notation.
 * @param {object} obj Target object.
 * @returns {*}
 *
 * @example
 * dpath('a.b', { a: { b: 2 } }) //=> 2
 * dpath('a.b', { c: { b: 2 } }) //=> undefined
 */
export const dpath = useWith(path, [safeSplit('.')]);

export const random = (min = 0, max = 1) => Math.floor(Math.random() * (max - min + 1) + min);

/** Curried. Wraps function into debounced function
 *  Meaning function execution will be delayed for defined amount of ms provided
 *  Each call of a function starts ms counts from the beginning
 *
 * @sig Number -> Function -> Function
 *
 * @function
 * @param {number}    ms   debounce timeout
 * @param {function}  cb   callback function
 *
 * @returns {function}
 */
export const debounce = curry((ms, cb) => {
  let delay;

  return function debounced(...args) {
    clearTimeout(delay);
    delay = setTimeout(() => {
      delay = null;
      cb.apply(this, args);
    }, ms);
  };
});

/** Converts String to kebab case ('yet-another-kebab-case')
 *
 * @sig String -> String
 * @sig '  Yet Another__RANDOM    string' -> 'yet-another-random-string'
 *
 * @function
 * @param {string}  key   transformed string
 *
 * @returns {string}
 */
export const kebabCase = pipe(
  toLower,
  replace(/[-_]+/g, ' '),
  trim,
  replace(/\s+/g, '-'),
);

/**
 * Returns first truthy value of two properties.
 *
 * @function
 * @param {(string|number)} prop
 * @param {(string|number)} altProp
 * @param {object} source
 * @returns {*}
 *
 * @example
 * propOrProp(a, b, { a: A, b: B }) //=> A
 * propOrProp(a, b, { b: B }) //=> B
 */
export const propOrProp = curry((a, b, source) => or(prop(a, source), prop(b, source)));
