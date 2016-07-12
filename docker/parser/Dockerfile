FROM centos:7

USER root

RUN yum -y update

RUN yum install -y \
    yum-utils \
    wget \
    tar \
    bzip2 \
    vim \
    nkf \
    gcc \
    gcc-c++ \
    make \
    gdb \
    emacs \
    patch \
    git \
    zlib-devel \
    bzip2-devel \
    readline-devel \
    sqlite-devel \
    libpng-devel \
    freetype-devel \
    openssl-devel

RUN echo "timeout=300" >> /etc/yum.conf \
 && echo "minrate=100" >> /etc/yum.conf \
 && debuginfo-install -y glibc-2.17-106.el7_2.6.x86_64 libgcc-4.8.5-4.el7.x86_64 libstdc++-4.8.5-4.el7.x86_64 zlib-1.2.7-15.el7.x86_64

RUN localedef -vc -i ja_JP -f UTF-8 ja_JP.UTF-8; exit 0

RUN echo "LANG=ja_JP.UTF-8" > /etc/locale.conf \
 && echo "export LANG=ja_JP.UTF-8" >> ~/.bashrc

RUN cp /usr/share/zoneinfo/Japan /etc/localtime \
 && echo "ZONE=\"Asia/Tokyo\"" > /etc/sysconfig/clock

# python
RUN curl -s https://www.python.org/ftp/python/2.7.11/Python-2.7.11.tgz | tar -xz -C . \
 && cd Python-2.7.11/ \
 && ./configure --with-threads --prefix=/usr/local \
 && make \
 && make install

RUN curl -kL https://bootstrap.pypa.io/get-pip.py | python

RUN pip install ipython \
 && pip install python-cdb

# JUMAN
RUN wget -O juman-7.01.tar.bz2 'http://nlp.ist.i.kyoto-u.ac.jp/DLcounter/lime.cgi?down=http://nlp.ist.i.kyoto-u.ac.jp/nl-resource/juman/juman-7.01.tar.bz2&name=juman-7.01.tar.bz2' \
 && tar jxf juman-7.01.tar.bz2 \
 && rm -f juman-7.01.tar.bz2 \
 && cd juman-7.01 \
 && ./configure CFLAGS="-g3 -O0" -prefix=/usr/local \
 && make \
 && make install \
 && ldconfig \
 && rm -f ../juman-7.01.tar.bz2

# KNP
RUN wget -O knp-4.16.tar.bz2 'http://nlp.ist.i.kyoto-u.ac.jp/DLcounter/lime.cgi?down=http://nlp.ist.i.kyoto-u.ac.jp/nl-resource/knp/knp-4.16.tar.bz2&name=knp-4.16.tar.bz2' \
 && tar jxf knp-4.16.tar.bz2 \
 && rm -f knp-4.16.tar.bz2 \
 && cd knp-4.16 \
 && ./configure CFLAGS="-g3 -O0" CXXFLAGS="-g3 -O0" --prefix=/usr/local --with-juman-prefix=/usr/local/ \
 && make \
 && rm -f ../knp-4.16.tar.bz2
# leak disk space... when continue command
RUN cd knp-4.16 \
 && make install
