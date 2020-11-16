import mojimoji as mj
import copy
import networkx as nx
from lib import preprocessing as pr
import MeCab
from collections import Counter
import math


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
        self.thres_minority_opinion_words = 0
        self.thres_loop_extract_clique = 1000000

        self.ngwords, ngwords_origin = "", ""
        self.opinions = opinions
        self.create_stopwords_list()
        self.unique_words = [["児童", "クラブ"], ["イルカ", "クラブ"], ["セントラル", "開発"]]
        self.gr = nx.Graph()
        self.gr2 = nx.Graph() # large_cliques
        self.node_buf = []
        self.mecab = MeCab.Tagger(
            "-Ochasen -d /usr/local/lib/mecab/dic/mecab-ipadic-neologd")

    def classificate(self):  # main
        self.opinions = self.text_cleaning(self.opinions)
        self.create_graph(self.gr, self.opinions)  # 意見をノード化
        node_list, self.node_buf = list(self.gr.nodes), list(self.gr.nodes)
        tokenized_opinions = self.remove_stopwords(self.tokenize(node_list))
        self.remove_minority_opinions(tokenized_opinions)
        self.connect_edge(tokenized_opinions)
        maximal_cliques = self.extract_maximal_cliques()
        self.create_clusters_from_larges(maximal_cliques)
        pass

    def text_cleaning(self, opinions):
        splitted_opinions = self.text_splitter(self.opinions)  # 意見の分割
        splitted_opinions = self.num_zen_to_han(splitted_opinions)  # 数字の全角を半角へ
        return splitted_opinions

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

    def create_graph(self, gr, node):
        for i in range(len(node)):
            # 空白が"\u3000"として読み込まれてしまうので削除しておく
            gr.add_node(node[i].replace('\\u3000', ''))

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
        self.ngwords, self.ngwords_origin = ngwords, ngwords

    def remove_stopwords(self, tokenized_opinions):
        words, important_words, res = [], [], []
        for t in tokenized_opinions:
            words.extend(t)
        for word, cnt in Counter(words).most_common():
            if cnt <= math.floor(0.035*len(self.gr.nodes)) or cnt >= math.ceil(0.6*len(self.gr.nodes)):
                self.ngwords.append(word)
            else:
                important_words.append(word)
        for t in tokenized_opinions:
            res.append([u for u in t if not u in self.ngwords])
        return res

    def tokenize(self, node):
        tokenized_opinions = []
        for i in range(len(node)):
            node[i] = pr.preprocessing(node[i])

            self.mecab.parse("")
            list_splitted_n = []
            splitted_n = self.mecab.parseToNode(node[i])
            while splitted_n:
                word = splitted_n.feature.split(",")[6]
                clas = splitted_n.feature.split(",")[0]
                if clas == u"名詞" or clas == u"動詞":  # 名詞と動詞のみを抽出
                    if not word in self.ngwords_origin:
                        list_splitted_n.append(word)
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
            cnt = node[i].count("退園")
            while cnt > 0:
                if "退る" in tokenized_opinions[i]:
                    tokenized_opinions[i].remove("退る")
                tokenized_opinions[i].remove("園")
                tokenized_opinions[i].append("退園")
                cnt -= 1
            cnt = node[i].count("子供の家")
            while cnt > 0:
                tokenized_opinions[i].remove("子供")
                tokenized_opinions[i].append("子供の家")
                cnt -= 1
        return tokenized_opinions

    def remove_minority_opinions(self, tokenized_opinions):
        for i in range(len(tokenized_opinions)):
            if len(tokenized_opinions[i]) <= self.thres_minority_opinion_words:
                self.gr.remove_node(self.node_buf[i])

    def connect_edge(self, tokenized_opinions):
        self.mecab.parse("")
        for t1 in range(len(tokenized_opinions)-1):
            len_t1 = len(tokenized_opinions[t1])
            if len_t1 <= self.thres_minority_opinion_words:
                continue
            for t2 in range(t1+1, len(tokenized_opinions)):
                if self.gr.has_edge(self.node_buf[t1], self.node_buf[t2]):
                    continue
                cnt, flag, len_t2 = 0, False, len(tokenized_opinions[t2])
                if len_t2 <= self.thres_minority_opinion_words:
                    continue
                for i in range(len_t1):
                    if flag:
                        break
                    for j in range(len_t2):
                        if math.floor(cnt) >= round(math.sqrt(min(len_t1, len_t2))):
                            self.gr.add_edge(
                                self.node_buf[t1], self.node_buf[t2])
                            flag = True
                            break
                        elif tokenized_opinions[t1][i] == tokenized_opinions[t2][j]:
                            if self.mecab.parseToNode(tokenized_opinions[t1][i]).next.feature.split(",")[0] == u'名詞':
                                cnt += 1
                            else:  # 動詞の場合
                                cnt += 0.7

    def extract_maximal_cliques(self):
        maximal_cliques = []
        for n in self.gr.nodes:
            cnt_loop = 0
            list_n, list_size, buf, stack, depth = [[n]], [1], [n], [], []
            for to in nx.all_neighbors(self.gr, n):
                stack.append(to)
                depth.append(len(buf))
            while len(stack) > 0:
                to, dep = stack.pop(), depth.pop()
                while True:  # bufをdepと同じ長さになるまで消してく
                    if len(buf) < dep:
                        print("error")
                    if len(buf) == dep:
                        break
                    buf.pop()
                flag = True
                for i in buf:  # 今出き上がっているbufのノードと全て繋がっているかをみる
                    if not self.gr.has_edge(to, i):  # to -> i に辺があるかを見る
                        flag = False
                        break
                if flag:  # 全てと隣接していたらbufにアペンド
                    buf.append(to)
                    for toto in nx.all_neighbors(self.gr, to):
                        if not toto in buf:
                            stack.append(toto)
                            depth.append(len(buf))
                    cp_buf = copy.deepcopy(buf)
                    list_n.append(cp_buf)
                    list_size.append(len(buf))
                cnt_loop += 1
                if cnt_loop > self.thres_loop_extract_clique:
                    break
            k = list_size.index(max(list_size))
            maximal_cliques.append(list_n[k])
        return maximal_cliques

    def create_clusters_from_larges(self, maximal_cliques):
        large_cliques = extract_large_cliques(maximal_cliques)
        self.create_graph(self.gr2, large_cliques)
        self.connect_edge_large(large_cliques)
    
    def extract_large_cliques(self, maximal_cliques):
        large_cliques, buf = [], []
        floor = math.floor(len(self.gr.nodes)/6) if (len(self.gr.nodes)/6) > 1 else 1
        for i in range(floor):
            mac = 0
            if len(buf) == len(maximal_cliques):
                break
            for j in range(len(maximal_cliques)):
                if j in buf:
                    continue
                mac = max(mac, len(maximal_cliques[j]))
                if mac == len(maximal_cliques[j]):
                    l = j
            large_cliques.append(maximal_cliques[l])
            buf.append(l)
        return large_cliques

    def connect_edge_large(self, maximal_cliques):
        for q in range(0, len(maximal_cliques)-1):
            for p in range(q+1, len(maximal_cliques)):
                if self.gr2.has_edge(p, q):
                    continue
                cnt = 0
                for k in range(len(maximal_cliques[q])):
                    for l in range(len(maximal_cliques[p])):
                        if maximal_cliques[q][k] == maximal_cliques[p][l]:
                            cnt += 1
                            break
                per = cnt * 100 / min(len(maximal_cliques[q]), len(maximal_cliques[p]))
                if per >= 50:
                    self.gr2.add_edge(p, q)
