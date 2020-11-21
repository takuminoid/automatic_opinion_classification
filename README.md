# automatic_opinion_classification

自然言語処理を用いた，意見の自動分類です．

# 概要

意見を入力すると，自動的に分類ラベルの予測，意見分類を行う

**Input**

意見のリスト　

` 例）['私は賛成です', '緑が多い街', '木を植えるのが良いと思います'] `

**Output** 

どの分類ラベルに分類されたかのインデックスのリスト と 全分類ラベルのリスト

``` 
    例）[ 
            [[0], [1,2], [1]], 
            [['賛成'], ['木', '植える'], ['緑', '街']] 
        ]
```

**使用例**

```
from classificate_opinion import ClassificateOpinion

c = ClassificationOpinions(input_list)
output = c.classificate()

label_nums = output[0]
labels = output[1]
```

**実行時間**

`classificate_opinions.py`内の`thres_loop_extract_clique`という値を調整することで実行時間を変更できる．値を小さくすれば実行時間は短くなるが，精度は落ちる．



| データ数=1395|  thres_loop_extract_clique  |  time  |
| ---- | ---- | ---- |
|      |  10  |  10 sec  |
|      |  100,000 (デフォルト)  |  300 sec  |
