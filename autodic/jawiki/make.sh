#!/bin/bash

MAKE=${BASH_SOURCE}
MAKE=`dirname ${MAKE}`
MAKE_DIR=`cd ${MAKE}; pwd`
SCRIPTS_DIR=`cd ${MAKE_DIR}/scripts; pwd`

ts=`date +'%Y%m%d%H%M%S'`
JUMANRC=${MAKE_DIR}/jumanrc
JUMANRC_ORIG=jumanrc.backup_for_rebuild_dic.${ts}
cp /usr/local/etc/jumanrc /usr/local/etc/${JUMANRC_ORIG}
if [ $? -ne 0 ]; then
  exit 1
fi
\cp -f ${MAKE_DIR}/jumanrc /usr/local/etc/

DATA_DIR=`mkdir -p ${MAKE_DIR}/../data; cd ${MAKE_DIR}/../data; pwd`

BUILD_DIR=`mkdir -p ${MAKE_DIR}/build; cd ${MAKE_DIR}/build; pwd`
JUMAN_BUILD_DIR=`mkdir -p ${BUILD_DIR}/juman; cd ${BUILD_DIR}/juman; pwd`
KNP_BUILD_DIR=`mkdir -p ${BUILD_DIR}/knp; cd ${BUILD_DIR}/knp; pwd`

JAWIKI_ABSTRACT_DUMP=jawiki-latest-abstract.xml
JAWIKI_PAGE_DUMP=jawiki-latest-page.sql.gz
JAWIKI_REDIRECT_DUMP=jawiki-latest-redirect.sql.gz

JAWIKI_BASE=latest

JAWIKI_ABSTRACT_PATH=${DATA_DIR}/${JAWIKI_ABSTRACT_DUMP}
JAWIKI_PAGE_PATH=${DATA_DIR}/${JAWIKI_PAGE_DUMP}
JAWIKI_REDIRECT_PATH=${DATA_DIR}/${JAWIKI_REDIRECT_DUMP}

HYPONYMY_PATH=${DATA_DIR}/res_def_jawiki-latest_withWD_posWD
READING_DICT_PATH=${DATA_DIR}/reading.cdb
HYPONYMY_DICT_PATH=${DATA_DIR}/hyponymy.cdb

SINGLE_MORPH_PATH=${BUILD_DIR}/single_morph.txt
MULTIPLE_MORPH_PATH=${BUILD_DIR}/multiple_morph.txt

JUMAN_DIC_PATH=${JUMAN_BUILD_DIR}/jawiki.dic
KNP_DIC_PATH=${KNP_BUILD_DIR}/jawiki.dic

echo "Downloading Wikipedia dumps"
if [ ! -e ${JAWIKI_ABSTRACT_PATH} ]; then
  wget -O ${JAWIKI_ABSTRACT_PATH} https://dumps.wikimedia.org/jawiki/${JAWIKI_BASE}/${JAWIKI_ABSTRACT_DUMP}
else
  echo "${JAWIKI_ABSTRACT_PATH} exists. Skip to download dump"
fi

if [ ! -e ${JAWIKI_PAGE_PATH} ]; then
  wget -O ${JAWIKI_PAGE_PATH} https://dumps.wikimedia.org/jawiki/${JAWIKI_BASE}/${JAWIKI_PAGE_DUMP}
else
  echo "${JAWIKI_PAGE_PATH} exists. Skip to download dump"
fi

if [ ! -e ${JAWIKI_REDIRECT_PATH} ]; then
  wget -O ${JAWIKI_REDIRECT_PATH} https://dumps.wikimedia.org/jawiki/${JAWIKI_BASE}/${JAWIKI_REDIRECT_DUMP}
else
  echo "${JAWIKI_REDIRECT_PATH} exists. Skip to download dump"
fi

echo "Make reading.cdb"
cat ${JAWIKI_ABSTRACT_PATH} | python ${SCRIPTS_DIR}/reading_cdb_make.py -d ${READING_DICT_PATH}
if [ $? -ne 0 ]; then
  echo "reading_cdb_make.py returns not-zero status"
  exit 1
fi

echo "Make hyponymy.cdb"
if [ ! -e ${HYPONYMY_PATH} ]; then
  echo "Wikipedia Hyponymy Definition not found !"
  exit 1 
else
  cat ${HYPONYMY_PATH} | python ${SCRIPTS_DIR}/hyponymy_cdb_make.py -d ${HYPONYMY_DICT_PATH}
  if [ $? -ne 0 ]; then
    echo "hyponymy_cdb_make.py returns not-zero status"
    exit 1
  fi
fi

echo "Detecting morph or not for all title and redirect"
cat ${JAWIKI_ABSTRACT_PATH} | grep '<title>' | python ${SCRIPTS_DIR}/select_morph.py -d ${DATA_DIR} -o ${BUILD_DIR}

echo "Make juman wikipedia seed dictionary"
cat ${SINGLE_MORPH_PATH} | python ${SCRIPTS_DIR}/juman_make.py -d ${DATA_DIR} 1>${JUMAN_DIC_PATH} 2>${JUMAN_DIC_PATH}.err

echo "Make knp wikipedia seed  dictionary" 
cat ${MULTIPLE_MORPH_PATH} | python ${SCRIPTS_DIR}/knp_make.py -d ${DATA_DIR} 1>${KNP_DIC_PATH} 2>${KNP_DIC_PATH}.err

\cp -f /usr/local/etc/${JUMANRC_ORIG} /usr/local/etc/jumanrc
