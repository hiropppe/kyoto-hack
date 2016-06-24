FROM centos:6

USER root

RUN yum -y update

RUN yum install -y \
    vim \
    wget \
    tar \
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
    openssl-devel \
    yum-utils

#RUN echo "timeout=300" >> /etc/yum.conf \
# && echo "minrate=100" >> /etc/yum.conf \
# && debuginfo-install glibc-2.12-1.166.el6_7.7.x86_64 libgcc-4.4.7-16.el6.x86_64 libstdc++-4.4.7-16.el6.x86_64 zlib-1.2.3-29.el6.x86_64

# JST
RUN cp /usr/share/zoneinfo/Japan /etc/localtime \
 && echo "ZONE=\"Asia/Tokyo\"" > /etc/sysconfig/clock

# system python
RUN curl -s https://www.python.org/ftp/python/2.7.11/Python-2.7.11.tgz | tar -xz -C . \
 && cd Python-2.7.11/ \
 && ./configure --with-threads --enable-shared --prefix=/usr/local \
 && make \
 && make altinstall

RUN ln -s /usr/local/lib/libpython2.7.so.1.0 /lib64/ \
 && echo "/usr/local/lib" >> /etc/ld.so.conf \
 && ldconfig \
 && ln -s /usr/local/bin/python2.7 /usr/local/bin/python \
 && ln -s /usr/local/bin/python2.7 /usr/local/bin/python2

RUN curl -kL https://bootstrap.pypa.io/get-pip.py | python

RUN pip install ipython \
 && pip install python-cdb

# Ruby 1.8.7
COPY ossl_pkey_ec.c.patch /tmp/

RUN curl -s ftp://ftp.ruby-lang.org/pub/ruby/1.8/ruby-1.8.7-p374.tar.gz | tar -xz -C . \
 && cd ruby-1.8.7-p374 \
 && patch -u ext/openssl/ossl_pkey_ec.c < /tmp/ossl_pkey_ec.c.patch \
 && ./configure \
 && make \
 && make install

# JUMAN
RUN wget -O juman-7.01.tar.bz2 'http://nlp.ist.i.kyoto-u.ac.jp/DLcounter/lime.cgi?down=http://nlp.ist.i.kyoto-u.ac.jp/nl-resource/juman/juman-7.01.tar.bz2&name=juman-7.01.tar.bz2' \
 && tar jxf juman-7.01.tar.bz2 \
 && rm -f juman-7.01.tar.bz2 \
 && cd juman-7.01 \
 && ./configure CFLAGS="-g3 -O0" -prefix=/usr/local \
 && make \
 && make install \
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
 && make install \
 && ldconfig

# MeCab
RUN curl -s https://mecab.googlecode.com/files/mecab-0.996.tar.gz | tar -xz -C . \
 && cd mecab-0.996 \
 && ./configure \
 && make \
 && make check \
 && make install \
 && ldconfig

RUN curl -s https://mecab.googlecode.com/files/mecab-ipadic-2.7.0-20070801.tar.gz | tar -xz -C . \
 && cd ../mecab-ipadic-2.7.0-20070801 \
 && ./configure --with-charset=utf8 \
 && make \
 && make install

# MeCab-Ruby
COPY MeCab_wrap.cpp.patch /tmp/

RUN curl -s http://mecab.googlecode.com/files/mecab-ruby-0.996.tar.gz | tar -xz -C . \
 && cd mecab-ruby-0.996 \
 && patch -u MeCab_wrap.cpp < /tmp/MeCab_wrap.cpp.patch \
 && ruby extconf.rb \
 && make \
 && make install

# darts-clone
RUN curl -s https://storage.googleapis.com/google-code-archive-downloads/v2/code.google.com/darts-clone/darts-clone-0.32g.tar.gz | tar xz -C . \
 && cd darts-clone-0.32g \
 && ./configure \
 && make \
 && make check \
 && make install

# pecco
RUN curl -s http://www.tkl.iis.u-tokyo.ac.jp/~ynaga/pecco/pecco-latest.tar.gz | tar -xz -C . \
 && cd pecco-2015-10-05 \
 && ./configure --with-trie-impl=darts-clone --enable-float \
 && make install

# Hyponymy extraction tool
COPY ex-hyponymy-1.0-pecco.patch /tmp/

RUN wget -O ex-hyponymy-1.0.tar.gz https://alaginrc.nict.go.jp/hyponymy/cgi-bin/dl.1.0.cgi \
 && tar xzf ex-hyponymy-1.0.tar.gz \
 && cd ex-hyponymy-1.0 \
 && patch -u script/ex_hyponymy.sh < /tmp/ex-hyponymy-1.0-pecco.patch \
 && rm -f ../ex-hyponymy-1.0.tar.gz

RUN echo 'export LANG=ja_JP.UTF-8' >> ~/.bash_profile
