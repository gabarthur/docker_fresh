FROM fresh/debian
 
ARG VERSION
ARG SUBVERSION
ARG RELEASE
 
RUN --mount=type=bind,source=./distr,target=/tmp/distr_full \ 
    set -e && \
# Dependencies
    apt-get update -y && \
    apt-get -y install --no-install-recommends curl bzip2 gosu ca-certificates locales && \
# PostgreSQL
    mkdir /tmp/pgsql && \
    #curl -o /tmp/pgsql/postgresql.tar.bz2 https://s3.1c709.ru/postgresql/postgresql_${VERSION}.${SUBVERSION}_${RELEASE}_debian_13.0_x86_64_pa… && \
    tar -xf /tmp/distr_full/postgresql_17.8_1_debian_13.0_x86_64_package.tar.bz2 -C /tmp/pgsql && \
    apt-get install -y --allow-downgrades /tmp/pgsql/*.deb && \
# Clean up
    apt-get remove -y bzip2 && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/* /tmp/pgsql/*.deb && \
    rm -r /tmp/pgsql && \
# Russian locale
    unlink /etc/localtime && \
    ln -s /usr/share/zoneinfo/Europe/Moscow /etc/localtime && \
    dpkg-reconfigure -f noninteractive tzdata && \
    localedef -i ru_RU -c -f UTF-8 -A /usr/share/locale/locale.alias ru_RU.UTF-8
 
ENV LANG=ru_RU.utf8
ENV PATH=$PATH:/usr/lib/postgresql/${VERSION}/bin
ENV PGDATA=/var/lib/postgresql/data
 
VOLUME $PGDATA
 
COPY ./images/db/entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/entrypoint.sh
 
ENTRYPOINT ["entrypoint.sh"]
CMD ["postgres"]