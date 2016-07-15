#!/bin/bash

if [ $# -ne 1 ];then
  echo "make.sh <knp_src_dir>"
  exit 1
fi

KNP_SRC_DIR=${1}

MAKE=${BASH_SOURCE}
MAKE=`dirname ${MAKE}`
MAKE_DIR=`cd ${MAKE}; pwd`

BUILD_DIR=`mkdir -p ${MAKE_DIR}/build; cd ${MAKE_DIR}/build; pwd`
JUMAN_BUILD_DIR=`mkdir -p ${BUILD_DIR}/juman; cd ${BUILD_DIR}/juman; pwd`
KNP_BUILD_DIR=`mkdir -p ${BUILD_DIR}/knp; cd ${BUILD_DIR}/knp; pwd`

echo "Enter jawiki"
sh ${MAKE_DIR}/jawiki/make.sh
\cp -f ${MAKE_DIR}/jawiki/build/juman/*.dic ${JUMAN_BUILD_DIR}
\cp -f ${MAKE_DIR}/jawiki/build/knp/*.dic ${KNP_BUILD_DIR}

echo "Enter geodb"
sh ${MAKE_DIR}/geodb/make.sh
\cp -f ${MAKE_DIR}/geodb/build/juman/*.dic ${JUMAN_BUILD_DIR}
\cp -f ${MAKE_DIR}/geodb/build/knp/*.dic ${KNP_BUILD_DIR}

echo "Make juman auto dict"
cd ${JUMAN_BUILD_DIR}
cat *.dic > auto.dic
/usr/local/libexec/juman/makeint auto.dic 
/usr/local/libexec/juman/dicsort auto.int > jumandic.dat
/usr/local/libexec/juman/makepat auto.int

echo "Make knp auto dict" 
cd ${KNP_BUILD_DIR}
\cp -f ${KNP_SRC_DIR}/dict/auto/*.dat ${KNP_BUILD_DIR}
LANG=C sort auto.dat wikipedia.dat shop.dic geo.dic | /usr/local/libexec/knp/make_db auto.db -append \|
