#!/bin/bash
# Generate a self-signed RSA certificate authority key pair
ulimit -c unlimited
if [ $# -ne 2 ]; then
  echo "Usage: `basename $0` CaName TruststorePassword"
  exit -1
fi
CA_NAME=$1
PASSWD=$2
ROOT_DIR=`echo $0 | sed -e "s|\(.*\)/bin/[^\.]*.sh$|\1|"`
OPENSSL="/usr/bin/openssl"
if [ ! -f "${ROOT_DIR}/ca/index.txt" ]; then
  touch ${ROOT_DIR}/ca/index.txt
fi
if [ ! -f "${ROOT_DIR}/ca/serial" ]; then
  echo '01' > ${ROOT_DIR}/ca/serial
fi
${OPENSSL} genrsa -out ${ROOT_DIR}/ca/ca.key 2048
if [ ! $? -eq 0 ]; then
  echo "Working directory: `pwd`"
  echo "Error generating the ca key from command: openssl genrsa -out ${ROOT_DIR}/ca/ca.key 2048"
  exit -1
fi
${OPENSSL} req -new -x509 -days 3650 -key ${ROOT_DIR}/ca/ca.key -out ${ROOT_DIR}/ca/${CA_NAME}.pem -config ${ROOT_DIR}/conf/ca_config.txt -batch -verbose
if [ ! $? -eq 0 ]; then
  echo "Working directory: `pwd`"
  echo "Error generating the ca certificate from command: openssl req -new -x509 -days 3650 -key ${ROOT_DIR}/ca/ca.key -out ${ROOT_DIR}/ca/${CA_NAME}.pem -config $ROOT_DIR/conf/ca_config.txt -batch -verbose"
  exit -1
fi
keytool -import -keystore ${ROOT_DIR}/ca/.truststore -storepass ${PASSWD} -alias ${CA_NAME} -file ${ROOT_DIR}/ca/${CA_NAME}.pem <<EOF
yes
EOF
if [ ! $? -eq 0 ]; then
  echo "Working directory: `pwd`"
  echo "Error generating the trust store Java Keystore from command: keytool -import -keystore ${ROOT_DIR}/ca/.truststore -storepass $PASSWD -alias ${CA_NAME} -file ${ROOT_DIR}/ca/${CA_NAME}.pem"
  exit -1
else
  echo "SUCCESS"
fi
