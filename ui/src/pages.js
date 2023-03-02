/*
Copyright (c) 2023, Ingram Micro
All rights reserved.
*/
import {
  getDatabases,
  getRegions,
} from './utils';

import {
  hideComponent,
  prepareDatabases,
  renderDatabases,
  showComponent,
} from './components';


export const saveSettingsData = async () => {};

export const index = async () => {
  hideComponent('app');
  showComponent('loader');

  const databases = await getDatabases();
  await getRegions();

  hideComponent('loader');
  showComponent('app');

  renderDatabases(prepareDatabases(databases));
};

