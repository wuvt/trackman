FROM debian:12-slim as builder
# following on the approach described in
# https://github.com/GoogleContainerTools/distroless/issues/863#issuecomment-949723748
RUN cd /tmp && \
    apt-get update && \
    apt-get download  debconf zlib1g libelf1 libbpf1 libmd0 libbsd0 libcap2 \
        libcap2-bin libdb5.3 libmnl0 libpcre2-8-0 libselinux1 libcom-err2 \
        libkrb5support0 libk5crypto3 libkeyutils1 libkrb5-3 libgssapi-krb5-2 \
        libtirpc-common libtirpc3 libxtables12 iproute2 libcrypt1 nginx-common \
        nginx libnginx-mod-http-echo nginx-light libnginx-mod-nchan && \
    mkdir /dpkg && \
    for deb in *.deb; do dpkg --extract $deb /dpkg; done

FROM gcr.io/distroless/base-debian12:nonroot
USER root
COPY --from=builder /dpkg /
RUN --mount=type=bind,from=builder,target=/mnt ["/mnt/bin/ln", "-sf", "/dev/stdout", "/var/log/nginx/access.log"]
RUN --mount=type=bind,from=builder,target=/mnt ["/mnt/bin/ln", "-sf", "/dev/stderr", "/var/log/nginx/error.log"]

COPY nginx/nginx.conf /etc/nginx/nginx.conf
COPY trackman/static /srv/http/static

EXPOSE 80

CMD ["/usr/sbin/nginx", "-g", "daemon off;"]
