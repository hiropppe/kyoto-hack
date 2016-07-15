#!/bin/bash

MAKE=${BASH_SOURCE}
MAKE=`dirname ${MAKE}`
MAKE_DIR=`cd ${MAKE}; pwd`
SCRIPTS_DIR=`cd ${MAKE_DIR}/scripts; pwd`

FB_DIR=`cd ${MAKE_DIR}/fb; pwd`

BUILD_DIR=`mkdir -p ${MAKE_DIR}/build; cd ${MAKE_DIR}/build; pwd`
JUMAN_BUILD_DIR=`mkdir -p ${BUILD_DIR}/juman; cd ${BUILD_DIR}/juman; pwd`
KNP_BUILD_DIR=`mkdir -p ${BUILD_DIR}/knp; cd ${BUILD_DIR}/knp; pwd`

ts=`date +'%Y%m%d%H%M%S'`
JUMANRC=${MAKE_DIR}/jumanrc
JUMANRC_ORIG=jumanrc.backup_for_rebuild_dic.${ts}
cp /usr/local/etc/jumanrc /usr/local/etc/${JUMANRC_ORIG}
if [ $? -ne 0 ]; then
  exit 1
fi
\cp -f ${MAKE_DIR}/jumanrc /usr/local/etc/

echo "Make shop dict seed"
python ${FB_DIR}/make_shop_dict.py 1>${JUMAN_BUILD_DIR}/shop.dic 2>${KNP_BUILD_DIR}/shop.dic 

echo "Make geo dict seed"
python ${SCRIPTS_DIR}/make_geo_dict.py > ${KNP_BUILD_DIR}/geo.dic

\cp -f /usr/local/etc/${JUMANRC_ORIG} /usr/local/etc/jumanrc
