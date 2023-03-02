
/*
Copyright (c) 2023, Ingram Micro
All rights reserved.
*/
// API calls to the backend
export const getDatabases = () => fetch('/api/v1/databases').then(
  (response) => response.json(),
);

export const getRegions = () => fetch('/api/v1/regions').then(
  (response) => response.json(),
);

