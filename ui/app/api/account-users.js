import {
  http,
} from '~tools/rest';


export default {
  list: (id, opts = {}) => http.get(`/public/v1/accounts/${id}/users?status=active`, opts),
};
