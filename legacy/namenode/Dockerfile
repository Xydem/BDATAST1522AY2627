FROM apache/hadoop:3.3.6

ENV HADOOP_HOME=/opt/hadoop
ENV HADOOP_CONF_DIR=/opt/hadoop/etc/hadoop
ENV YARN_CONF_DIR=/opt/hadoop/etc/hadoop
ENV HADOOP_LOG_DIR=/opt/hadoop/logs

# default user from apache/hadoop:3.3.6 is hadoop:users

# Set the working directory
WORKDIR ${HADOOP_HOME}

USER hadoop

COPY config/core-site.xml ${HADOOP_CONF_DIR}/core-site.xml
COPY config/hdfs-site.xml ${HADOOP_CONF_DIR}/hdfs-site.xml

COPY config/log4j.properties ${HADOOP_CONF_DIR}/log4j.properties

# Create folder for storing name node data
RUN mkdir -p ${HADOOP_HOME}/data/name

RUN mkdir ${HADOOP_HOME}/scripts

COPY --chmod=765 scripts/entrypoint.sh ${HADOOP_HOME}/scripts/entrypoint.sh

# Following lines are commented because namenode format 
# is now moved to container startup time
# 
# # Format the name node data folder
# RUN echo "Formatting Hadoop name node folder (${HADOOP_HOME}/data/name)..."
# RUN hdfs namenode -format -force -nonInteractive


EXPOSE 8020 9870 9090

ENTRYPOINT ["/opt/hadoop/scripts/entrypoint.sh"]
