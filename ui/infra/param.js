const fs = require('fs');
const path = require('path');
const yaml = require('js-yaml');

const CONFIG = yaml.load(fs.readFileSync(path.resolve(__dirname, '../config.yml')).toString());
const ENV = process.env;

module.exports = (k, def) => ENV[k] || CONFIG[k] || def;
