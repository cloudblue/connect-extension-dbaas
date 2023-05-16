/*
Copyright (c) 2023, Ingram Micro
All rights reserved.
*/
module.exports = {
  moduleFileExtensions: [
    'js',
    'json',
    'vue',
  ],

  clearMocks: true,

  transform: {
    '^.+\\.vue$': '@vue/vue2-jest',
    '.+\\.(css|styl|less|sass|scss|png|jpg|ttf|woff|woff2)$': 'jest-transform-stub',
    '^.+\\.js$': 'babel-jest',
  },
  transformIgnorePatterns: [],


  testMatch: [
    '<rootDir>/ui/(**/*\\.spec.(js|jsx|ts|tsx)|**/__tests__/*.(js|jsx|ts|tsx))',
  ],

  collectCoverage: true,

  collectCoverageFrom: [
    'ui/src/**/*.js',
  ],

  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/ui/src/$1',
    '\\.(jpg|jpeg|png|gif|eot|otf|webp|svg|ttf|woff|woff2|mp4|webm|wav|mp3|m4a|aac|oga)$': '<rootDir>/__mocks__/fileMock.js',
    '\\.(css|less)$': '<rootDir>/__mocks__/styleMock.js',

    '^rest$': '<rootDir>/ui/app/tools/rest',
    '^~tools$': '<rootDir>/ui/app/tools/',
    '^~tools/(.*)$': '<rootDir>/ui/app/tools/$1',
    '^~utils$': '<rootDir>/ui/app/tools/utils',
    '^~helpers$': '<rootDir>/ui/app/tools/helpers',
    '^~constants$': '<rootDir>/ui/app/tools/constants',
    '^~mixins$': '<rootDir>/ui/app/tools/mixins/',
    '^~mixins/(.*)$': '<rootDir>/ui/app/tools/mixins/$1',
    '^~views$': '<rootDir>/ui/app/views/',
    '^~views/(.*)$': '<rootDir>/ui/app/views/$1',
    '^~components$': '<rootDir>/ui/app/components/',
    '^~components/(.*)$': '<rootDir>/ui/app/components/$1',
    '^~styles$': '<rootDir>/ui/app/styles/',
    '^~styles/(.*)$': '<rootDir>/ui/app/styles/$1',
    '^~api$': '<rootDir>/ui/app/api/',
    '^~api/(.*)$': '<rootDir>/ui/app/api/$1',
  },

  coverageDirectory: '<rootDir>/ui/tests/coverage/',

  coveragePathIgnorePatterns: ['<rootDir>/ui/src/pages/'],

  testEnvironment: 'jsdom',
};
