import rest, {
  http,
} from '~tools/rest';


const URL = '/api/v1/databases';

export default rest(URL, {
  reconfigure: (id, data, opts = {}) => http.post(
    `${URL}/${id}/reconfigure`,
    { body: data, ...opts },
  ),

  activate: (id, opts = {}) => http.post(
    `${URL}/${id}/activate`,
    opts,
  ),
});
