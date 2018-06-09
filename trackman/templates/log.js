var djset_id = {{ djset_id or "null" }};
var dj_id = {{ dj_id }};

var t = new Trackman("{{ url_for('trackman_private.login', _external=True)[:-1] }}", djset_id, dj_id, "{{ config.PUBSUB_SUB_URL_DJ }}");
t.init();
