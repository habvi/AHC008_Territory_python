## AHC008
Public : 2022.2/26 19:00以降  
https://atcoder.jp/contests/ahc008/tasks/ahc008_a
___

## results(PyPy)

| file | score | ranking  (暫定) | time | 何をしたか |
| ---- | ---- | ---- | ---- | ---- |
| 1.py | 2,041,399 | 最低点付近 | 141ms | 一旦全員300ターン何もしない |
| 2.py | 259,688,453 | 42/383人 | 768ms | randomな縦方向に移動してそこから横方向に壁を置いてただ横長長方形区間に分ける |
| 3.py | 266,928,006 | 61/419人 | 664ms | 2.pyのclass,関数をまとめた(内容変更なし) |
| 4.py | 532,947,033 | 293/876人 | 266ms | 4区間に分けて横に壁を置き,通路を上下に歩いて動物がいれば塞ぐ。まだ個別行動。中央はペアで同時に塞ぎたい。 |
| 5.py | 556,970,265 | 294/887人 | 314ms | 4.pyバグ修正。pet/humanが大きかったら3.pyを採用してみた。3.pyは運任せなのでほぼ変わらず。 |