## `python/tool/ministry_tbl.txt`
[法令IDについて](https://laws.e-gov.go.jp/file/LawIdNamingConvention.pdf)の
（別紙）府省令 ビット定義
に記載されている、
M1からM6までの、
各bitの情報をテキストにコピーしたもの。

このファイルを元に、
`python/ministry_bit_tbl.json`を生成する。

## `python/tool/make_mini.py`
`python/tool/ministry_tbl.txt`を読み出し、
LSBからMSBに並び替え、
未記載のMSB側を「（空き）」で埋めて、
M1〜M6の各28bitに対応する文字列の2重リストを生成する。
結果は、`../ministry_bit_tbl.json`に出力する。
