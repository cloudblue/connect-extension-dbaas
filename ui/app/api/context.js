import {
  http,
} from '~tools/rest';


export default {
  get: (opts = {}) => http.get('/public/v1/auth/context', opts),
};
