var djset_id = {{ djset_id or "null" }};
var dj_id = {{ dj_id }};

var t = new Trackman("{{ url_for('trackman_private.login')[:-1] }}", djset_id, dj_id);
t.init();
