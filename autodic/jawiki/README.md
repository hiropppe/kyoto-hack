#### WikipediaダンプからJUMAN辞書とKNP辞書を生成するツール

##### 概要
KNPの[論文](http://www.anlp.jp/proceedings/annual_meeting/2012/pdf_dir/C1-5.pdf "実テキスト解析をささえる語彙知識の自動獲得
")に基づいてWikipediaダンプからJUMAN辞書とKNP辞書を生成するツール

分布類似度の計算に基づく分類とかゴミ掃除とかいろいろ対応できてませんが、解析時に配布済みのWikipedia形態素辞書を有効にすることで、ある程度既存の形態素を守りつつ新しい語彙を追加することはできる（はず）

##### 環境
- Python 2.7.11
- pyknp==0.22
- jctconv==0.1.2
- mojimoji==0.0.5
- python-cdb==0.35
- python-Levenshtein==0.12.0

##### 入力ダンプのDownload
- jawiki-latest-abstract.xml
- jawiki-latest-page.sql.gz
- jawiki-latest-redirect.sql.gz
- jawiki-latest-pages-meta-current.xml.bz2 (上位下位関係抽出ツールで使用)

##### 上位語下位語の用語ペアの取得

事前に上位下位関係抽出ツールを使用して上位語下位語の用語ペアを取得しておく

https://alaginrc.nict.go.jp/hyponymy/

少し古いツールで動作環境の構築がめんどくさいので作業コンテナを容易してある

https://github.com/hiropppe/kyoto-hack/tree/master/docker/ex-hyponymy

出力からデータベースを作成

```
$ python hyponymy_cdb_make.py < res_*_withWD_posWD
```

##### 読みの取得

```
$ python reading_cdb_make.py < jawiki-latest-abstract.xml
```

##### 形態素と非形態素タイトルの振り分け
```
# juman_title.txt, knp_title.txt に振り分け
$ cat jawiki-latest-abstract.xml | grep '<title>' | python select_morph.py
```

##### 形態素辞書のビルド
```
# ソースの生成
$ cat juman_title.txt | python juman_make.py 1>jawiki.dic 2>jawiki.err
# コンパイル
$ /usr/local/libexec/juman/makeint jawiki.dic
$ /usr/local/libexec/juman/dicsort jawiki.int > jumandic.dat
$ /usr/local/libexec/juman/makepat jawiki.int
# 配布
$ mkdir /usr/local/share/juman/custom_wikipediadic
$ cp jumandic.* /usr/local/share/juman/custom_wikipediadic/
# 辞書エントリに追加
$ vim /usr/local/etc/jumanrc
 :
(辞書ファイル
        /usr/local/share/juman/dic
        /usr/local/share/juman/autodic
        /usr/local/share/juman/wikipediadic
        /usr/local/share/juman/custom_wikipediadic ; 追加
)
 :
```

##### 構文解析辞書のビルド
```
# ソースの生成
$ cat knp_title.txt | python knp_make.py 1>knpwork/jawiki.dic 2>knpwork/jawiki.err
# コンパイル
$ LANG=C sort auto.dat jawiki.dic | /usr/local/libexec/knp/make_db auto.db -append \|
# 配布
cp auto.db /usr/local/share/knp/dict/auto/auto.db
```


##### 解析例

```
$ juman | knp -anaphora -tab | grep ^+
掛川駅前に集合
```

[変更前]

```
+ 1D <文節内><係:文節内><文頭><地名><体言><名詞項候補><先行詞候補><SM-場所><正規化代表表記:掛川/かけがわ><NE:LOCATION:掛川><照応詞候補:掛川><EID:0>                                                            
+ 2D <地名><ニ><助詞><体言><係:ニ格><区切:0-0><格要素><連用要素><名詞項候補><先行詞候補><SM-場所><正規化代表表記:駅前/えきまえ><照応詞候補:掛川駅前><解析格:ニ><EID:1>                                         
+ -1D <文末><体言><用言:動><体言止><レベル:C><区切:5-5><ID:（文末）><裸名詞><提題受:30><主節><動態述語><サ変><名詞項候補><先行詞候補><サ変止><態:未定><正規化代表表記:集合/しゅうごう><用言代表表記:集合/しゅうごう><主題格:一人称優位><照応詞候補:集合><格関係1:ニ:駅前><格解析結果:集合/しゅうごう:動1:ガ/U/-/-/-/-;ヲ/U/-/-/-/-;ニ/C/駅前/1/0/1;ト/U/-/-/-/-;デ/U/-/-/-/-;カラ/U/-/-/-/-;ヨリ/U/-/-/-/-;マデ/U/-/-/-/-;ヘ/U/-/-/-/-;時間/U/-/-/-/-;外の関係/U/-/-/-/-;ノ/U/-/-/-/-;修飾/U/-/-/-/-;トスル/U/-/-/-/-;ヲフクメル/U/-/-/-/-;ニヨル/U/-/-/-/-;ヲハジメル/U/-/-/-/-;ヲノゾク/U/-/-/-/-;ニムケル/U/-/-/-/-;ニアワセル/U/-/-/-/-><EID:2><述語項構造:集合/しゅうごう:動1:ニ/C/掛川駅前/1>
```

[変更後]

```
+ 1D <文節内><係:文節内><文頭><地名><体言><名詞項候補><先行詞候補><SM-場所><正規化代表表記:掛川駅/かけがわえき><NE:LOCATION:掛川駅><Wikipedia上位語:駅><照応詞候補:掛川駅><EID:0>                              
+ 2D <相対名詞><地名><ニ><助詞><体言><係:ニ格><区切:0-0><格要素><連用要素><準用言><受:隣のみ><後方チ><一文字漢字><名詞項候補><先行詞候補><SM-場所><省略解析なし><正規化代表表記:前/まえ><照応詞候補:掛川駅前>< 解析格:ニ><EID:1>
+ -1D <文末><体言><用言:動><体言止><レベル:C><区切:5-5><ID:（文末）><裸名詞><提題受:30><主節><動態述語><サ変><名詞項候補><先行詞候補><サ変止><態:未定><正規化代表表記:集合/しゅうごう><用言代表表記:集合/しゅうごう><Wikipedia上位語:不明><Wikipediaエントリ:集合><主題格:一人称優位><照応詞候補:集合><格関係1:ニ:前><格解析結果:集合/しゅうごう:動1:ガ/U/-/-/-/-;ヲ/U/-/-/-/-;ニ/C/前/1/0/1;ト/U/-/-/-/-;デ/U/-/-/-/-;カラ/U/-/-/-/-;ヨリ/U/-/-/-/-;マデ/U/-/-/-/-;ヘ/U/-/-/-/-;時間/U/-/-/-/-;外の関係/U/-/-/-/-;ノ/U/-/-/-/-;修飾/U/-/-/-/-;トスル/U/-/-/-/-;ヲフクメル/U/-/-/-/-;ニヨル/U/-/-/-/-;ヲハジメル/U/-/-/-/-;ヲノゾク/U/-/-/-/-;ニムケル/U/-/-/-/-;ニアワセル/U/-/-/-/-><EID:2><述語項構造:集合/しゅうごう:動1:ニ/C/掛川駅前/1>
```
