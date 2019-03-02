FROM meroje/alpine-nchan:1.1.15
COPY nginx/nginx.conf /etc/nginx/nginx.conf
COPY trackman/static /srv/http/static
RUN install -d -m 0700 /var/cache/nginx/trackman
