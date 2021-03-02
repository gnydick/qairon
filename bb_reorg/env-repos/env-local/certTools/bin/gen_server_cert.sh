#!/bin/bash
# Generate a server certificate
ulimit -c unlimited
if [ $# -ne 3 ]; then
  echo "Usage: `basename $0` CaName ServerHostName KeystorePassword"
  exit -1
fi
CA_NAME=${1}
SERVER_HOSTNAME=${2}
PASSWD=${3}
ROOT_DIR=`echo $0 | sed -e "s|\(.*\)/bin/[^\.]*.sh$|\1|"`
OPENSSL="/usr/bin/openssl"
if [ ! -f "${ROOT_DIR}/server/index.txt" ]; then
  touch ${ROOT_DIR}/server/index.txt
fi
if [ ! -f "${ROOT_DIR}/server/serial" ]; then
  echo '01' > ${ROOT_DIR}/server/serial
fi
${OPENSSL} genrsa -out ${ROOT_DIR}/server/${SERVER_HOSTNAME}.key 2048
if [ ! $? -eq 0 ]; then
  echo "Working directory: `pwd`"
  echo "Error generating the server key from command: openssl genrsa -out ${ROOT_DIR}/server/${SERVER_HOSTNAME}.key 2048"
  exit -1
fi
sed -e "s/__HOSTNAME__/${SERVER_HOSTNAME}/g" ${ROOT_DIR}/conf/server_config_template.txt | sed -e "s|__ROOT_DIR__|${ROOT_DIR}|g" > ${ROOT_DIR}/conf/server_config.txt
${OPENSSL} req -new -days 3650 -key ${ROOT_DIR}/server/${SERVER_HOSTNAME}.key -out ${ROOT_DIR}/server/${SERVER_HOSTNAME}.csr -config ${ROOT_DIR}/conf/server_config.txt -verbose -batch
if [ ! $? -eq 0 ]; then
  echo "Working directory: `pwd`"
  echo "Error generating the server signing request from command: openssl req -new -days 3650 -key ${ROOT_DIR}/server/${SERVER_HOSTNAME}.key -out ${ROOT_DIR}/server/${SERVER_HOSTNAME}.csr -config ${ROOT_DIR}/conf/server_config.txt -verbose -batch"
  exit -1
fi
${OPENSSL} ca -days 3650 -keyfile ${ROOT_DIR}/ca/ca.key -cert ${ROOT_DIR}/ca/${CA_NAME}.pem -out ${ROOT_DIR}/server/${SERVER_HOSTNAME}.pem -config ${ROOT_DIR}/conf/server_config.txt -verbose -batch -infiles ${ROOT_DIR}/server/${SERVER_HOSTNAME}.csr
if [ ! $? -eq 0 ]; then
  echo "Working directory: `pwd`"
  echo "Error generating the server certificate from command: openssl ca -days 3650 -keyfile ${ROOT_DIR}/ca/ca.key -cert ${ROOT_DIR}/ca/${CA_NAME}.pem -out ${ROOT_DIR}/server/${SERVER_HOSTNAME}.pem -config ${ROOT_DIR}/conf/server_config.txt -verbose -batch -infiles ${ROOT_DIR}/server/${SERVER_HOSTNAME}.csr"
  exit -1
fi
${OPENSSL} pkcs12 -export -in ${ROOT_DIR}/server/${SERVER_HOSTNAME}.pem -inkey ${ROOT_DIR}/server/${SERVER_HOSTNAME}.key -out ${ROOT_DIR}/server/${SERVER_HOSTNAME}.p12 -name ${SERVER_HOSTNAME} -passout stdin <<EOF
${PASSWD}
EOF
if [ ! $? -eq 0 ]; then
  echo "Working directory: `pwd`"
  echo "Error exporting the server certificate to the pkcs12 format: openssl pkcs12 -export -in ${ROOT_DIR}/server/${SERVER_HOSTNAME}.pem -inkey ${ROOT_DIR}/server/${SERVER_HOSTNAME}.key -out ${ROOT_DIR}/server/${SERVER_HOSTNAME}.p12 -name ${SERVER_HOSTNAME} -passout stdin"
  exit -1
fi
keytool -importkeystore -destkeystore ${ROOT_DIR}/server/.keystore -deststorepass ${PASSWD} -destkeypass ${PASSWD} -alias ${SERVER_HOSTNAME} -srckeystore ${ROOT_DIR}/server/${SERVER_HOSTNAME}.p12 -srcstoretype PKCS12 <<EOF
${PASSWD}
EOF
if [ ! $? -eq 0 ]; then
  echo "Working directory: `pwd`"
  echo "Error generating the key store Java Keystore from command: keytool -importkeystore -destkeystore ${ROOT_DIR}/server/.keystore -deststorepass ${PASSWD} -destkeypass ${PASSWD} -alias ${SERVER_HOSTNAME} -srckeystore ${ROOT_DIR}/server/${SERVER_HOSTNAME}.p12 -srcstoretype PKCS12"
  exit -1
else
  echo "SUCCESS"
fi
