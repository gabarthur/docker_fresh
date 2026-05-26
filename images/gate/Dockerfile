FROM eclipse-temurin:26-jre-noble

RUN --mount=type=bind,source=./distr,target=/tmp/distr_full \
# Dependencies
    apt-get update -y && \
    apt-get install -y --no-install-recommends unzip && \
# Gate install
    #unzip /tmp/distr_full/appgate_1.1.3_1.zip -d /tmp/gate && \
    #unzip /tmp/distr_full/appgate.zip -d /tmp/gate && \
    unzip /tmp/distr_full/appgate-1.1.3-2-all.zip -d /tmp/gate && \
    apt-get install -y /tmp/gate/*.deb && \
# Cleanup
    rm -rf /tmp/gate && \
    apt-get remove -y unzip && \
    apt-get autoremove -y && \
# Gate settings
    echo export PATH=$PATH:/usr/local/openjdk-8/bin > /etc/profile.d/add_java.sh && \
    chmod +x /etc/profile.d/add_java.sh && \
    echo export PATH=$PATH:JAVA_HOME=/usr/local/openjdk-8 > /etc/profile.d/add_java_home.sh && \
    chmod +x /etc/profile.d/add_java_home.sh
    #/opt/1C/1cfresh/appgate/setAuth.sh appgate 12345Qwer

EXPOSE 8080 9090

CMD java $JAVA_OPTS -jar /usr/share/appgate/appgate.jar