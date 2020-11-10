import mojimoji as mj
import copy


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
        self.create_stopwords_list()

    def classificate(self):
        self.opinions = self.text_cleaning(self.opinions)
        pass

    def text_cleaning(self, opinions):
        splitted_opinions = self.text_splitter(self.opinions)  # 意見の分割
        splitted_opinions = self.num_zen_to_han(splitted_opinions)  # 数字の全角を半角へ
        return splitted_opinions
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

    def num_zen_to_han(self, opinions):
        for i in range(len(opinions)):
            opinions[i] = mj.zen_to_han(opinions[i], kana=False, ascii=False)
        return opinions

    def create_stopwords_list(self):
        ngwords = []
        stopwords = open('stopwords.txt', 'r')  # SlothLib + etc
        for line in stopwords:
            ngwords.append(line.rstrip('\n'))
        stopwords.close()
        for i in range(12353, 12436):  # 平仮名一文字
            ngwords.append(chr(i))
        for i in range(12449, 12533):  # 片仮名一文字
            ngwords.append(chr(i))
        for i in range(97, 97+26):  # アルファベット小文字
            ngwords.append(chr(i))
        for i in range(65, 65+26):  # アルファベット大文字
            ngwords.append(chr(i))
        ngwords_origin = copy.deepcopy(ngwords)
        self.ngwords = ngwords
        self.ngwords_origin = ngwords