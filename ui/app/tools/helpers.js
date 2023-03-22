import {
  __,
  anyPass,
  curry,
  has,
  includes,
  isEmpty,
  join,
  map,
  objOf,
  path,
  pipe,
  replace,
  split,
  test,
  when,
} from 'ramda';

import convert from 'color-convert';

import {
  colorVars,
  colorsValues as predefinedColors,
} from '~constants';


/**
 * Convert HEX to RGB.
 *
 * @function
 * @param {string} hex Hex string
 * @returns {array} Color in RGB color space
 *
 * @example
 * hexToRGB('ffffff') //=> [255, 255, 255]
 */
export const hexToRGB = hex => convert.hex.rgb(hex);

/**
 * Returns a object with a given key as property in format `--{key}` and
 * RGB components with comma delimiter as value.
 *
 * @function
 * @param {string} key
 * @param {string} hexVal
 * @returns {object}
 *
 * @example
 * hexToStyleVar('color', '#00FF00') //=> { --color: '0, 255, 0' }
 */
export const hexToStyleVar = curry((key, hex) => pipe(
  hexToRGB,
  join(', '),
  objOf(`--${key}`),
)(hex));

/**
 * If the input has no units, adds px to it, otherwise returns the input.
 *
 * @function
 * @param {string|number} value
 *
 * @example
 * ```javascript
 * addUnits(20) // '20px';
 * addUnits('20px') // '20px';
 * ```
 */
export const addUnits = when(
  test(/^-?\d+$/),
  v => `${v}px`,
);

export const checkVarColor = includes(__, colorVars);

export const hexColor = when(
  has(__, predefinedColors),
  colorName => path([colorName, 'color'], predefinedColors),
);

export const colorToRGB = pipe(
  hexColor,
  hexToRGB,
);

/**
 * Convert RGB to HEX.
 *
 * @function
 * @param {string} rgb rgb string
 * @returns {string} hex color string
 *
 * @example
 * hexToRGB('255, 255, 255') //=> 'ffffff'
 */
export const rgbToHEX = pipe(
  split(','),
  map(Number),
  convert.rgb.hex,
);

export const hexRegExp = /^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$/;

export const validateColor = anyPass([
  isEmpty,
  test(hexRegExp),
  checkVarColor,
  has(__, predefinedColors),
]);

/**
 * Check is color bright or not.
 * https://www.w3.org/TR/AERT/#color-contrast
 *
 * @function
 * @param {string} color Color in hex (supports `#` at start)
 * @returns {boolean} Is color bright or not
 */
export const isBright = pipe(
  replace('#', ''),
  convert.hex.rgb,
  ([r, g, b]) => r * 0.299 + g * 0.587 + b * 0.114 > 180,
);
