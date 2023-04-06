import rest, {
  http,
} from '~tools/rest';


const URL = '/api/v1/databases';

export default rest(URL, {
  reconfigure: (id, data, opts = {}) => http.post(
    `${URL}/${id}/reconfigure`,
    { body: data, ...opts },
  ),

  delete: (id, opts = {}) => http.delete(
    `${URL}/${id}`,
    opts,
  ),

  activate: (id, data, opts = {}) => http.post(
    `${URL}/${id}/activate`,
    { body: data, ...opts },
  ),
});
