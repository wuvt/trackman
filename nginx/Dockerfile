FROM debian:11-slim as builder
# following on the approach described in
# https://github.com/GoogleContainerTools/distroless/issues/863#issuecomment-949723748
RUN cd /tmp && \
    apt-get update && \
    apt-get download iproute2 debconf perl-base libcrypt1 libbpf0 libelf1 \
        zlib1g libbsd0 libmd0 libcap2 libcap2-bin libdb5.3 libmnl0 \
        libselinux1 libpcre2-8-0 libxtables12 libnginx-mod-http-echo \
        nginx-common lsb-base libpcre3 nginx-light libnginx-mod-nchan && \
    mkdir /dpkg && \
    for deb in *.deb; do dpkg --extract $deb /dpkg; done

FROM gcr.io/distroless/base-debian11:nonroot
USER root
COPY --from=builder /dpkg /
RUN --mount=type=bind,from=builder,target=/mnt ["/mnt/bin/ln", "-sf", "/dev/stdout", "/var/log/nginx/access.log"]
RUN --mount=type=bind,from=builder,target=/mnt ["/mnt/bin/ln", "-sf", "/dev/stderr", "/var/log/nginx/error.log"]

COPY nginx/nginx.conf /etc/nginx/nginx.conf
COPY trackman/static /srv/http/static

EXPOSE 80

CMD ["/usr/sbin/nginx", "-g", "daemon off;"]
