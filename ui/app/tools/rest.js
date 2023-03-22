import {
  T,
  always,
  cond,
  curry,
  forEachObjIndexed,
  identity,
  includes,
  is,
  isNil,
  propEq,
  startsWith,
  unless,
  values,
  when,
} from 'ramda';


import {
  flattenObj,
} from '~utils';

import {
  responseTypes,
} from '~constants';


export class ApiError extends Error {
  constructor(data, { status }, ...args) {
    super(...args);

    this.text = data;
    this.status = status;
  }
}

const isOctetStream = propEq('Content-Type', 'application/octet-stream');

const wrapInFormData = (data, flat = false) => {
  const formData = new FormData();

  if (data instanceof File || data instanceof Blob) {
    formData.append('value', data);
  } else {
    forEachObjIndexed(
      (v, k) => {
        if (typeof v !== 'undefined') {
          const encodedData = cond([
            [isNil, always('')],
            [is(Blob), identity],
            [is(Object), JSON.stringify],
            [T, identity],
          ])(v);

          formData.append(k, encodedData);
        }
      },
      when(
        always(flat),
        flattenObj,
        data,
      ),
    );
  }

  return formData;
};

async function request(
  path,
  method,
  body,
  headers,
  parseResponseAs,
  noCookies = false,
  fullResponse = false,
  flatFormData = true,
) {
  const url = new URL(
    when(
      startsWith('/'),
      v => `${window.location.origin}${v}`,
    )(path),
  );

  const requestConfig = {
    method,
    headers,
    credentials: noCookies ? 'omit' : 'same-origin',
  };

  let responseData;

  if (headers.upload) {
    requestConfig.body = (isOctetStream(headers)) ? body.file : wrapInFormData(body, flatFormData);
  } else if (body) {
    requestConfig.headers['Content-Type'] = 'application/json';
    requestConfig.body = unless(is(String), JSON.stringify, body);
  }

  const response = await fetch(url, requestConfig);
  try {
    const readableResponse = response.clone();
    const allowedType = includes(parseResponseAs, values(responseTypes));
    responseData = await readableResponse[allowedType ? parseResponseAs : 'json']();
  } catch (e) {
    responseData = response.text();
  }

  if (!response.ok) {
    let data;

    try {
      data = JSON.parse(responseData);
    } catch (e) {
      data = responseData;
    }

    throw new ApiError(
      data,
      response,
      `Server responded with non-ok code: ${response.status}`,
    );
  }

  return fullResponse ? {
    body: responseData,
    headers: response.headers,
    status: response.status,
  } : responseData;
}

/** Just a proxy for request with more reasonable arguments grouping
 *
 *  @sig context -> (method -> path -> options -> Promise)
 *
 *  @param  {string}   apiKey        api key
 *  @param  {string}  method        request method
 *  @param  {string}  path          request url path
 *  @param  {object}  options       rest of options passed as an object
 *
 *  @returns {promise}
 */
export const query = curry((
  method,
  path,
  {
    apiKey = undefined,
    body = undefined,
    headers = {},
    parseResponseAs = responseTypes.JSON,
    noCookies = false,
    fullResponse = false,
    flatFormData = true,
  },
) => {
  const requestHeaders = headers;

  if (apiKey) requestHeaders.Authorization = apiKey;

  return request(
    path,
    method,
    body,
    requestHeaders,
    parseResponseAs,
    noCookies,
    fullResponse,
    flatFormData,
  );
});

export const http = {
  query,
  get: query('GET'),
  post: query('POST'),
  put: query('PUT'),
  patch: query('PATCH'),
  delete: query('DELETE'),
};

export default (url, extend) => ({
  list: (opt = {}) => http.get(url, opt),
  create: (data, opt = {}) => http.post(url, { body: data, ...opt }),
  get: (id, opt = {}) => http.get(`${url}/${id}`, opt),
  update: (id, data, opt = {}) => http.put(`${url}/${id}`, { body: data, ...opt }),
  delete: (id, opt = {}) => http.delete(`${url}/${id}`, opt),
  ...extend,
});
