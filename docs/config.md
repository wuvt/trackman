# Configuration Options

* `REDIS_URL` - URL to Redis instance used for key-value storage and cache
* `ARTISTS_PER_PAGE` - Number of items to display per page in artist-style listings
* `STATION_NAME` - Name of the station
* `DJ_TIMEOUT` - Session timeout used when a DJ is logged in
* `EXTENDED_DJ_TIMEOUT` - Session timeout used for "let me play longer songs"
* `NO_DJ_TIMEOUT` - Session timeout used when no DJ is active (i.e. to start automation)
* `CLAIM_TOKEN_TIMEOUT` - Timeout for DJ claim tokens
* `INTERNAL_IPS` - List of internal IP addresses that will bypass Trackman authentication
* `AUTOMATION_PASSWORD` - Password used by automation to log tracks
* `ICECAST_URL` - URL to Icecast instance
* `ICECAST_MOUNTS` - List of mounts on the Icecast instance (used to get a listener count)
* `TRACKMAN_NAME` - Name of the Trackman instance
* `TRACKMAN_ARTIST_PROHIBITED` - List of artists that are not allowed
* `TRACKMAN_LABEL_PROHIBITED` - List of labels that are not allowed
* `TRACKMAN_DJ_HIDE_AFTER_DAYS` - Number of days after which a DJ will be hidden from the list
* `ARCHIVE_URL_FORMAT` - URL format used to generate URLs to archived tracks
* `MUSICBRAINZ_HOSTNAME` - Hostname to use for MusicBrainz API
* `MUSICBRAINZ_RATE_LIMIT` - Rate limit for MusicBrainz API
* `MAIL_FROM` - Email address used for sending email
* `SMTP_SERVER` - SMTP server used for sending email
* `SMTP_PORT` - SMTP port used for sending email
* `CHART_MAIL` - Boolean indicating whether or not charts are enabled
* `CHART_MAIL_DEST` - Email address that will receive charts
* `PROXY_FIX` - Boolean indicating whether or not to process X-Forwarded-For headers
* `PROXY_FIX_NUM_PROXIES` - Number of proxies used for X-Forwarded-For headers
* `AUTH_SUPERADMINS` - List of OIDC subs that have access to everything
* `AUTH_ROLE_GROUPS` - Dictionary describing how application roles map to OIDC groups
* `OIDC_CLIENT_SECRETS` - Path to the OIDC `client_secrets.json` file
* `OIDC_SCOPES` - List of scopes used for OIDC (i.e. to also use groups)
* `AUTH_METHOD` - Should either be `google` or `oidc` depending on the method you want to use
* `GOOGLE_CLIENT_ID` - OAuth2 client ID for Google auth
* `GOOGLE_CLIENT_SECRET` - OAuth2 client secret for Google auth
* `GOOGLE_ALLOWED_DOMAINS` - List of allowed domains for Google auth; if not set or empty, all domains are allowed
* `GOOGLE_ADMIN_SUBJECT` - Needs to be the email address of a Google domain admin; this is required for obtaining user groups
* `GOOGLE_SERVICE_ACCOUNT_FILE` - Path to the Google service account file used for obtaining user groups

Additional configuration options are described in the documentation for [Flask](http://flask.pocoo.org/docs/1.0/config/#builtin-configuration-values), [Flask-SQLAlchemy](http://flask-sqlalchemy.pocoo.org/2.3/config/#configuration-keys), [Flask-WTF](https://flask-wtf.readthedocs.io/en/stable/config.html), and [Flask-OIDC](https://flask-oidc.readthedocs.io/en/latest/#settings-reference).
