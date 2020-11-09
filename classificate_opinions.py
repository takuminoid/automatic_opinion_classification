



# classificate_opinions = ClassificateOpinions()
class ClassificateOpinions():
  '''
    概要：意見を入力すると，自動的に分類ラベルの予測，意見分類を行う
    Input: 意見のリスト　例）['こんにちは', '今日はいい天気ですね', '私は原発には反対です']
    Output: どのラベルに分類されたかのリスト，全ラベルのリスト　例）{
                                                            label_num: [1, 2, 0],
                                                            labels: ['[原発]', '[賛成]', '[天気]'],
                                                            }
  '''
  def __init__(self, opinions):
    self.opinions = opinions

  def classificate(self):
    out = self.text_splitter(self.opinions)
    pass

  def text_cleaning(self, opinions):
    pass

  def text_splitter(self, opinions):
    splitted_opinions = []
    split_list = ['。・', '？・']
    split_list2 = ['②', '③', '④', '⑤', '⑥', '⑦', '⑧', '⑨']
    for opinion in opinions:
      flag = False
      if '①' in opinion:
        for spliter in split_list2:
          if spliter in opinion:
            opinion_buf = opinion.split(spliter)
            splitted_opinions.append(opinion_buf[0][1:])
            opinion = opinion_buf[1]
            flag = True
        splitted_opinions.append(opinion)
      if not flag:
        for spliter in split_list:
          if spliter in opinion:
            splitted_opinions.extend(opinion.split(spliter))
            flag = True
      if not flag:
        splitted_opinions.append(opinion)
    return splitted_opinions
