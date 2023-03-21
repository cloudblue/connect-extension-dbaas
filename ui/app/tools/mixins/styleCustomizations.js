import {
  objOf,
} from 'ramda';


import {
  hexToRGB,
} from '~helpers';


const getStyleCustomizations = (namespace = 'theme', {
  primary = '#1565c0',
  accent = '#4797f2',
  contrast = '#ffffff',
} = {}) => ({
  computed: {
    styleCustomizations() {
      return {
        [`--${namespace}_primary`]: primary,
        [`--${namespace}_primary_rgb`]: hexToRGB(primary),
        [`--${namespace}_accent`]: accent,
        [`--${namespace}_accent_rgb`]: hexToRGB(accent),
        [`--${namespace}_contrast`]: contrast,
        [`--${namespace}_contrast_rgb`]: hexToRGB(contrast),
      };
    },
  },

  methods: {
    genCssVar(name, value) {
      return objOf(`--${namespace}_${name}`, value);
    },
  },
});


export default getStyleCustomizations;
