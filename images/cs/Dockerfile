FROM eclipse-temurin:26-jre-noble

RUN --mount=type=bind,source=./distr,target=/tmp/distr_full \
    apt-get update && \
    apt-get -y install --no-install-recommends ca-certificates locales curl gosu gawk postgresql postgresql-contrib && \
    mkdir /tmp/cs && \
    tar -xvf /tmp/distr_full/1c_cs_27.0.42_linux_x86_64.tar.gz -C /tmp/cs && \
    /tmp/cs/1ce-installer-cli install --ignore-signature-warnings 1c-cs --components 1c-cs-server-small,1c-cs-hazelcast,1c-cs-elasticsearch,1c-enterprise-ring && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/* && \
    rm -rf /tmp/cs && \
    unlink /etc/localtime && \
    ln -s /usr/share/zoneinfo/Europe/Moscow /etc/localtime && \
    dpkg-reconfigure -f noninteractive tzdata && \
    localedef -i ru_RU -c -f UTF-8 -A /usr/share/locale/locale.alias ru_RU.UTF-8 && \
    useradd -m usr1ce && \
    chown -R usr1ce /opt

ENV LANG=ru_RU.utf8
ENV PATH=$PATH:/opt/1C/1CE/components/1c-enterprise-ring-0.19.5+12-x86_64/:/usr/lib/postgresql/13/bin/
ENV INSTANCE=/var/cs
ENV PGDATA=$INSTANCE/pgdata

VOLUME $INSTANCE

EXPOSE 9094

COPY ./images/cs/entrypoint.sh /
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]

HEALTHCHECK CMD curl -f http://localhost:8087/rs/health || exit 1
