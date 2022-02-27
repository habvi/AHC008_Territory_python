# MC Digital プログラミングコンテスト2022<br>(AtCoder Heuristic Contest 008)
Public : 2022.2/26 19:00以降  

初めて中期(2週間)ヒューリスティックコンテスト [AHC008](https://atcoder.jp/contests/ahc008/tasks/ahc008_a) に参加した記録です。  
色々勉強しながらトータルで関わった時間は50時間くらい、実装自体はおそらく22時間くらい。  
markdown記法の練習も兼ねて色々書いています。

<br>

## 最終結果
score : 13,595,910,450 (1000 testcase)  
ranking : 314 / 934 人  
performance : 1358 (水)  
Rating : 616 -> 846 (緑)

<br>

## 作成した簡易的なBash Script (要勉強)
### 機能
- `tester.exe` を使用して指定pythonファイルを実行し、スコアの合計を出力
- スコアを実際に集計するのは `calc_total_score.py` にお任せ
- `in/xxxx.txt` の数字は自動で4桁に0埋め
- 実行中の進行状況を `[ 18 / 100 ]` のように出力
- 公式が用意してくださったwindows用コンパイル済みバイナリ `tester.exe` と `in/` とpythonファイルが同ディレクトリにある設定です

<br>

### `calc_selected_seed.sh`
特定の入力ファイル `in/xxxx.txt` に対して `filename` を指定回数(`times`回)実行する  

```bash
bash calc_selected_seed.sh filename x times
```

ex ) `main.py` で `in/0014.txt` を5回実行
```bash
bash calc_selected_seed.sh main.py 14 5
```

<br>

### `calc_multi_seed.sh`
`in/0000.txt ~ in/xxxx.txt` までを1回ずつ実行する  
```bash
bash calc_multi_seed.sh filename x
```

ex ) `main.py` で `in/0000.txt ~ in/0099.txt` を実行

```bash
bash calc_multi_seed.sh main.py 100
```

<br>

## Results
100 testcase (PyPy)

| file | score | ranking<br>(暫定) | time | 何をしたか |
| ---- | ---- | ---- | ---- | ---- |
| [1.py](01.py) | 2,041,399 | 最低点ライン | 141ms | 一旦全員300ターン何もしない |
| [2.py](02.py) | 259,688,453 | 42/383人 | 768ms | randomな縦方向に移動してそこから横方向に壁を置いてただ横長長方形区間に分ける |
| [3.py](03.py) | 266,928,006 | 61/419人 | 664ms | 2.pyのclass,関数をまとめた(内容変更なし) |
| [4.py](04.py) | 532,947,033 | 293/876人 | 266ms | 4区間に分けて横に壁を置き,通路を上下に歩いて動物がいれば塞ぐ。まだ個別行動。中央はペアで同時に塞ぎたい。 |
| [5.py](05.py) | 556,970,265 | 294/887人 | 314ms | 4.pyバグ修正。pet/humanが大きかったら3.pyを採用。3.pyは運任せなのでほぼ変わらず。 |
| [6.py](06.py) | 565,646,643 | 293/888人 | 317ms | 5.pyのparam 2.4 -> 2.5にしただけ。誤差。 |
| [7.py](07.py) | 543,552,052 | 293/888人 | 342ms | 3.pyを使わないで4.pyのバグ修正しただけのもの。何点かcheck |
| [8.py](08.py) | 574,764,086 | 295/888人 | 339ms | 5.pyのparam 2.4 -> 2.6にして試し。 |
| [9.py](09.py) | 569,958,925 | 314/902人 | 321ms | 5.pyのparam 2.4 -> 2.7にして試し。 |
| [10.py](10.py) | 571,457,204 | 335/926人 | 386ms | 中央をペアで挟んで塞ぐコードのバグが取れず8.pyを一旦最終提出。 |
| [11.py](11.py) | - | - | - | 中央をペアで挟んで塞ぐ追加機能の途中まで。 |