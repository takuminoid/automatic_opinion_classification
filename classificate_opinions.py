import mojimoji as mj
import copy
import networkx as nx
from lib import preprocessing as pr
import MeCab


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
        self.unique_words = [["児童", "クラブ"], ["イルカ", "クラブ"], ["セントラル", "開発"]]

    def classificate(self):
        self.opinions = self.text_cleaning(self.opinions)
        # Detailをノード化
        gr = nx.Graph()
        for i in range(len(self.opinions)):
            # 空白が"\u3000"として読み込まれてしまうので削除しておく
            gr.add_node(list_detail[i].replace('\\u3000', ''))
        node_list = node_buf = list(gr.nodes)
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
        stopwords = open('data/stopwords.txt', 'r')  # SlothLib + etc
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

    def tokenize(self, node):
        tokenized_opinions = []
        for i in range(len(node)):
            node[i] = pr.preprocessing(node[i])

            # 形態素解析
            # mecab = MeCab.Tagger("-Ochasen -d /usr/lib/mecab/dic/mecab-ipadic-neologd")
            mecab = MeCab.Tagger(
                "-Ochasen -d /usr/local/lib/mecab/dic/mecab-ipadic-neologd")
            mecab.parse("")

            list_splitted_n = []
            splitted_n = mecab.parseToNode(node[i])
            while splitted_n:
                word = splitted_n.feature.split(",")[6]
                clas = splitted_n.feature.split(",")[0]
                if clas == u"名詞" or clas == u"動詞":  # 名詞と動詞のみを抽出
                    if not word in self.ngwords_origin:
                        if not word == "子":
                            list_splitted_n.append(word)
                        else:
                            list_splitted_n.append("子供")
                splitted_n = splitted_n.next
            tokenized_opinions.append(list_splitted_n)

            for j in range(len(tokenized_opinions[i]) - 1):
                if j > len(tokenized_opinions[i]) - 1:
                    break
                for w in self.unique_words:
                    if tokenized_opinions[i][j] == w[0] and tokenized_opinions[i][j+1] == w[1]:
                        tokenized_opinions[i][j] += tokenized_opinions[i][j+1]
                        del tokenized_opinions[i][j+1]
                        j -= 1
            cnt = node[i].count("退園")  # ”退園”を形態素解析すると”園”になってしまう問題
            while cnt > 0:
                if "退る" in tokenized_opinions[i]:
                    tokenized_opinions[i].remove("退る")
                tokenized_opinions[i].remove("園")
                tokenized_opinions[i].append("退園")
                cnt -= 1
            cnt = node[i].count("子供の家")  # ”子供の家”を形態素解析すると”子供”になってしまう問題
            while cnt > 0:
                tokenized_opinions[i].remove("子供")
                tokenized_opinions[i].append("子供の家")
                cnt -= 1
        return tokenized_opinions
