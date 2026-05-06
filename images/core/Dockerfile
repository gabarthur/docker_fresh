FROM fresh/debian
 
ENV DEBIAN_FRONTEND=noninteractive
 
ARG DISTR_VERSION
 
COPY entrypoint.sh /entrypoint.sh
 
RUN \
    set -e ;\
    mkdir /tmp/core ;\
    cd /tmp/core ;\
    wget --no-verbose http://ftp.debian.org/debian/pool/contrib/m/msttcorefonts/ttf-mscorefonts-installer_3.8_all.deb ;\
    wget --no-verbose https://oscript.io/downloads/1_7_0/x64/onescript-engine_1.7.0_all.deb ;\
    #wget --no-verbose https://s3.1c709.ru/builds/executor_server/latest.zip ;\
    #mkdir /executor-server ;\
    #unzip -qq latest.zip -d /executor-server ;\
    apt-get --allow-releaseinfo-change update ;\
    apt -y upgrade ;\
    apt-get -y update ;\
    apt-get -y install apache2 xvfb x11vnc sudo nano python3 libodbc1 odbc-postgresql net-tools icewm xfce4 gdb libxt6 libglib2.0-0 libgtk-3-0 libsoup-gnome2.4-1 libenchant-2-2 libgstreamer-gl1.0-0 libharfbuzz-icu0 iproute2 libwebkit2gtk-4.0-37 chromium python3-selenium dbus wmctrl ;\
    #curl -o ./bellsoft-jre11-linux-amd64.deb https://s3.1c709.ru/liberica/bellsoft-jre11.0.28+12-linux-amd64-full.deb;\
    #apt-get -y install ./bellsoft-jre11-linux-amd64.deb;\
    #rm ./bellsoft-jre11-linux-amd64.deb;\
    apt-get -y remove xscreensaver ;\
    apt-get -y install ssh imagemagick gstreamer1.0-plugins-bad ./*.deb ;\
    #chmod +x /tmp/core/setup-full-$DISTR_VERSION-x86_64.run ;\
    /main_dir/setup-full-$DISTR_VERSION-x86_64.run --mode unattended --enable-components client_full,server,ws,ru,uk,pl,vi,it,ro ;\
    update-ca-certificates ;\
    opm install deployka ;\
    a2enmod headers ;\
    apt-get -y autoremove ;\
    apt-get -y clean ;\
    localedef -i ru_RU -f UTF-8 ru_RU ;\
    rm -rf /tmp/core ;\
    ln -s /opt/1cv8/x86_64/$DISTR_VERSION /opt/1c ;\
    if [ ! -f /usr/lib/x86_64-linux-gnu/libenchant.so.1 ]; then ln -s /usr/lib/x86_64-linux-gnu/libenchant-2.so.2 /usr/lib/x86_64-linux-gnu/libenchant.so.1;fi ;\
    touch /etc/sudoers.d/www-data ;\
    echo "www-data ALL =NOPASSWD: /usr/sbin/apachectl graceful" >> /etc/sudoers.d/www-data ;\
    echo "www-data ALL =NOPASSWD: /usr/sbin/apachectl graceful-stop" >> /etc/sudoers.d/www-data ;\
    echo "www-data ALL =NOPASSWD: /usr/sbin/apachectl start" >> /etc/sudoers.d/www-data ;\
    echo "www-data ALL =NOPASSWD: /opt/1c/webinst" >> /etc/sudoers.d/www-data ;\
    echo "Defaults:www-data !requiretty" >> /etc/sudoers.d/www-data ;\
    chmod 0440 /etc/sudoers.d/www-data ;\
    touch /etc/sudoers.d/usr1cv8 ;\
    echo "usr1cv8 ALL =NOPASSWD: /usr/sbin/apachectl graceful" >> /etc/sudoers.d/usr1cv8 ;\
    echo "usr1cv8 ALL =NOPASSWD: /usr/sbin/apachectl graceful-stop" >> /etc/sudoers.d/usr1cv8 ;\
    echo "usr1cv8 ALL =NOPASSWD: /usr/sbin/apachectl start" >> /etc/sudoers.d/usr1cv8 ;\
    echo "usr1cv8 ALL =NOPASSWD: /opt/1c/webinst" >> /etc/sudoers.d/usr1cv8 ;\
    echo "Defaults:usr1cv8 !requiretty" >> /etc/sudoers.d/usr1cv8 ;\
    cp /usr/bin/chromium /usr/bin/chromium-real ;\
    chmod 0440 /etc/sudoers.d/usr1cv8 ;\
    chmod +x /entrypoint.sh
 
#ADD ./apache2.conf /etc/apache2/apache2.conf
#ADD ./logcfg.xml /opt/1cv8/conf/logcfg.xml
 
ENV LANG=ru_RU.UTF-8
ENV PATH=$PATH:/opt/1c
ENV COREDATA=/var/lib/1c/data
ENV LIC_DATA=/var/1C/licenses
ENV VOLUMES_PATH=/volumes
ENV MNT_PATH=/mnt
ENV DUMP_PATH=/var/dumps
ENV CORELOGS=/var/log/1c
ENV EXECUTOR_HOME=/opt/executor
ENV EXECUTOR_DATA=/executor-server
ENV FRESH=/var/www/fresh

ENTRYPOINT [ "/entrypoint.sh" ]
 