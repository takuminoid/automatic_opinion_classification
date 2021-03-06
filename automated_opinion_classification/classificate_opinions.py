import mojimoji as mj
import copy
import networkx as nx
import MeCab
from collections import Counter
import math
import os
base = os.path.dirname(os.path.abspath(__file__))
import sys
sys.path.append(base)
import preprocessing as pr
from stopwords import stopword_list

class ClassificateOpinions():
    '''
      概要：意見を入力すると，自動的に分類ラベルの予測，意見分類を行う
      Input: 意見のリスト　例）['こんにちは', '今日はいい天気ですね', '私は原発には反対です']
      Output: どのラベルに分類されたかのリスト，全ラベルのリスト　例）[
                                                                [[1], [0, 2], [0]],
                                                                [['原発'], ['賛成', '投票'], ['天気']]
                                                            ]
    '''

    def __init__(self, opinions):
        self.thres_opinion_words = 0
        self.thres_loop_extract_clique = 100000  # この値を減らすと，線形的に時間が短化

        self.ngwords, self.ngwords_origin = [], []
        self.important_words = []
        self.opinions = opinions
        self.create_stopwords_list()
        self.unique_words = [["児童", "クラブ"], ["イルカ", "クラブ"], ["セントラル", "開発"]]
        self.gr = nx.Graph()
        self.gr2 = nx.Graph()  # large_cliques
        self.node_buf = []
        self.mecab = MeCab.Tagger(
            "-Ochasen -d /usr/local/lib/mecab/dic/mecab-ipadic-neologd")
        self.clusters = []
        self.labels = []

    def classificate(self):  # main
        self.opinions = self.text_cleaning(self.opinions)
        self.create_graph(self.gr, self.opinions)  # 意見をノード化
        node_list, self.node_buf = list(self.gr.nodes), list(self.gr.nodes)
        tokenized_opinions = self.remove_stopwords(self.tokenize(node_list))
        self.remove_minority_opinions(tokenized_opinions)
        self.connect_edge(tokenized_opinions)
        maximal_cliques = self.extract_maximal_cliques()
        # large cliqueからクラスタを抽出
        self.create_clusters_from_larges(maximal_cliques)
        self.create_clusters_from_all(maximal_cliques)
        self.clusters, self.labels = self.combine_similar_clusters(
            self.clusters, self.labels)
        label_nums = self.data_shaping(
            self.opinions, self.clusters, self.labels)
        # return self.clusters, label_nums
        return [label_nums, self.labels]

    def text_cleaning(self, opinions):
        # splitted_opinions = self.text_splitter(self.opinions)  # 意見の分割
        # splitted_opinions = self.num_zen_to_han(splitted_opinions)  # 数字の全角を半角へ
        splitted_opinions = self.num_zen_to_han(opinions)
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

    def create_graph_index(self, gr, node):
        for i in range(len(node)):
            gr.add_node(i)

    def create_stopwords_list(self):
        ngwords = []
        stopwords = stopword_list  # SlothLib + etc
        for line in stopwords:
            ngwords.append(line.rstrip('\n'))
        for i in range(12353, 12436):  # 平仮名一文字
            ngwords.append(chr(i))
        for i in range(12449, 12533):  # 片仮名一文字
            ngwords.append(chr(i))
        for i in range(97, 97+26):  # アルファベット小文字
            ngwords.append(chr(i))
        for i in range(65, 65+26):  # アルファベット大文字
            ngwords.append(chr(i))
        self.ngwords, self.ngwords_origin = ngwords, copy.deepcopy(ngwords)

    def remove_stopwords(self, tokenized_opinions):
        words, res = [], []
        for t in tokenized_opinions:
            words.extend(t)
        for word, cnt in Counter(words).most_common():
            if (cnt <= math.floor(0.035*len(self.gr.nodes))) or (cnt >= math.ceil(0.6*len(self.gr.nodes))):
                self.ngwords.append(word)
            else:
                self.important_words.append(word)
        for t in tokenized_opinions:
            res.append([u for u in t if (not u in self.ngwords)])
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
            if len(tokenized_opinions[i]) <= self.thres_opinion_words:
                self.gr.remove_node(self.node_buf[i])

    def connect_edge(self, tokenized_opinions):
        self.mecab.parse("")
        for t1 in range(len(tokenized_opinions)-1):
            len_t1 = len(tokenized_opinions[t1])
            if len_t1 <= self.thres_opinion_words:
                continue
            for t2 in range(t1+1, len(tokenized_opinions)):
                if self.gr.has_edge(self.node_buf[t1], self.node_buf[t2]):
                    continue
                cnt, len_t2 = 0, len(tokenized_opinions[t2])
                if len_t2 <= self.thres_opinion_words:
                    continue
                t1_t2_and_list = set(tokenized_opinions[t1]) & set(
                    tokenized_opinions[t2])
                if len(t1_t2_and_list) == 0:
                    continue
                else:
                    for w in t1_t2_and_list:
                        count = tokenized_opinions[t1].count(
                            w) * tokenized_opinions[t2].count(w)
                        if self.mecab.parseToNode(w).next.feature.split(",")[0] == u'名詞':
                            cnt += 1*count
                        else:  # 動詞の場合
                            cnt += 0.7*count
                        if math.floor(cnt) >= round(math.sqrt(min(len_t1, len_t2))):
                            self.gr.add_edge(
                                self.node_buf[t1], self.node_buf[t2])
                            break
                # flag = False
                # for i in range(len_t1):
                #     if flag:
                #         break
                #     for j in range(len_t2):
                #         if tokenized_opinions[t1][i] == tokenized_opinions[t2][j]:
                #             if self.mecab.parseToNode(tokenized_opinions[t1][i]).next.feature.split(",")[0] == u'名詞':
                #                 cnt += 1
                #             else:  # 動詞の場合
                #                 cnt += 0.7
                #         if math.floor(cnt) >= round(math.sqrt(min(len_t1, len_t2))):
                #             self.gr.add_edge(
                #                 self.node_buf[t1], self.node_buf[t2])
                #             flag = True
                #             break

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
                if cnt_loop >= self.thres_loop_extract_clique:
                    break
            k = list_size.index(max(list_size))
            maximal_cliques.append(list_n[k])
        return maximal_cliques

    def create_clusters_from_larges(self, maximal_cliques):
        large_cliques = self.extract_large_cliques(maximal_cliques)
        self.create_graph_index(self.gr2, large_cliques)
        self.connect_edge_large(large_cliques)
        clusters = self.extract_clusters_large(self.gr2, large_cliques)
        tokenized_clusters = self.tokenize_clusters(clusters)
        self.check_words_in_cluster(clusters, tokenized_clusters)
        # return clusters

    def extract_large_cliques(self, maximal_cliques):
        large_cliques, buf = [], []
        floor = math.floor(len(self.gr.nodes)/6) \
            if (len(self.gr.nodes)/6) > 1 else 1
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

    def connect_edge_large(self, large_cliques):
        for q in range(0, len(large_cliques)-1):
            for p in range(q+1, len(large_cliques)):
                if self.gr2.has_edge(p, q):
                    continue
                cnt = 0
                q_p_and_list = set(large_cliques[q]) & set(large_cliques[p])
                per = round(len(q_p_and_list) * 100 /
                            min(len(large_cliques[q]), len(large_cliques[p])))
                # for k in range(len(large_cliques[q])):
                #     for l in range(len(large_cliques[p])):
                #         if large_cliques[q][k] == large_cliques[p][l]:
                #             cnt += 1
                #             break
                # per = round(cnt * 100 /
                #             min(len(large_cliques[q]), len(large_cliques[p])))
                if per >= 50:
                    self.gr2.add_edge(p, q)

    def extract_clusters_large(self, gr, large_cliques):  # Depth First Search
        visit, indexs, clusters = [], [], []
        for n in gr.nodes:
            visit.append(n)
            buf, stack = [n], []
            for to in nx.all_neighbors(gr, n):
                stack.append(to)
            while len(stack) > 0:
                to = stack.pop()
                if not to in visit:
                    visit.append(to)
                    buf.append(to)
                    for toto in nx.all_neighbors(gr, to):
                        if not toto in visit or not toto in buf:
                            stack.append(toto)
            indexs.append(buf)
        for index_list in indexs:
            buf = []
            if len(index_list) > 1:
                for i in index_list:
                    buf.extend(large_cliques[i])
                set1 = set(buf)
                clusters.append(list(set1))
        return clusters

    def tokenize_clusters(self, clusters):
        tokenized_clusters = []
        for i in range(len(clusters)):
            tokenized_cluster = []
            for s in clusters[i]:
                tokens = []
                self.mecab.parse("")
                split_c = self.mecab.parseToNode(pr.preprocessing(s))
                while split_c:
                    word = split_c.surface
                    hinshi = split_c.feature.split(",")[0]
                    if hinshi == u"名詞":  # 名詞のみ
                        if not word in self.ngwords_origin:
                            tokens.append(word)
                    split_c = split_c.next
                tokenized_cluster.append(tokens)
            tokenized_clusters.append(tokenized_cluster)
        for t in tokenized_clusters:
            for s in t:
                for i in range(len(s)-1):
                    if i >= len(s)-1:
                        break
                    for j in self.unique_words:
                        if s[i] == j[0] and s[i+1] == j[1]:
                            s[i] += s[i+1]
                            del s[i+1]
                            i -= 1
        for s in range(len(clusters)):
            for i in range(len(clusters[s])):
                cnt = clusters[s][i].count("退園")
                while cnt > 0:
                    tokenized_clusters[s][i].remove("園")
                    tokenized_clusters[s][i].append("退園")
                    cnt -= 1
                cnt = clusters[s][i].count("子供の家")
                while cnt > 0:
                    tokenized_clusters[s][i].remove("子供")
                    tokenized_clusters[s][i].append("子供の家")
                    cnt -= 1
        return tokenized_clusters

    def check_words_in_cluster(self, clusters, tokenized_clusters):
        for k in range(len(clusters)):
            words = []
            for j in range(len(tokenized_clusters[k])):
                for l in range(len(tokenized_clusters[k][j])):
                    words.append(tokenized_clusters[k][j][l])
            counter = Counter(words)
            for word, cnt in counter.most_common():
                if self.important_words[k] == word:
                    self.clusters.append(clusters[k])
        for i in range(len(self.clusters)):
            self.labels.append(self.important_words[i])

    def create_clusters_from_all(self, maximal_cliques):
        tokenized_cliques = self.tokenize_clusters(maximal_cliques)
        list_frequent_words = self.extract_most_frequenst_word(
            tokenized_cliques)
        self.combine_cliques_same_word(maximal_cliques, list_frequent_words)
        self.improve_cluster_by_labelwords()

    def extract_most_frequenst_word(self, tokenized_cliques):
        list_frequent_words = []
        for k in range(len(tokenized_cliques)):
            buf = []
            words = []
            for j in range(len(tokenized_cliques[k])):
                for l in range(len(tokenized_cliques[k][j])):
                    words.append(tokenized_cliques[k][j][l])
            counter = Counter(words)
            for word, cnt in counter.most_common():
                if not (word in self.ngwords):
                    buf.append(word)
                break
            list_frequent_words.append(buf)
        return list_frequent_words

    def combine_cliques_same_word(self, maximal_cliques, list_frequent_words):
        visited = copy.deepcopy(self.labels)
        # ccn_copy2 = copy.deepcopy(ccn)
        for i in range(len(list_frequent_words)-1):
            cnt = 1
            if (len(list_frequent_words[i]) <= 0) or (list_frequent_words[i][0] in visited):
                continue
            # labelsに直接appendしてOK?
            visited.append(list_frequent_words[i][0])
            for k in range(i+1, len(list_frequent_words)):
                if len(list_frequent_words[k]) <= 0:
                    continue
                if list_frequent_words[i][0] == list_frequent_words[k][0]:
                    cnt += 1
                    maximal_cliques[i].extend(maximal_cliques[k])
            if cnt >= math.floor(max(2, len(maximal_cliques)*0.25/100)):  # 一位の回数が1,2回しかない単語は除去
                set1 = set(maximal_cliques[i])
                self.clusters.append(list(set1))
                self.labels.append(list_frequent_words[i][0])

    def improve_cluster_by_labelwords(self):
        clusters = copy.deepcopy(self.clusters)
        for i in reversed(range(len(clusters))):
            cnt = 0
            for n in self.node_buf:
                if self.labels[i] in n:
                    flag = True
                    for c in clusters:
                        if n in c:
                            flag = False
                            break
                    if flag:
                        clusters[i].append(n)
            set1 = set(clusters[i])
            self.clusters[i] = copy.deepcopy(list(set1))

    def data_shaping(self, nodes, clusters, labels):
        label_nums = []
        labels.append(['その他'])  # ラベル結合処理を書いたら，リストに変更する
        for i in range(len(nodes)):
            buf = []
            for k in range(len(clusters)):
                if nodes[i] in clusters[k]:
                    buf.append(k)
            if len(buf) == 0:
                buf.append(len(labels)-1)
            label_nums.append(buf)
        return label_nums

    def combine_similar_clusters(self, clusters, labels):
        combined_labels = []
        for i in range(len(labels)):
            combined_labels.append([labels[i]])
        combined_clusters, combined_labels = self.check_and_combine(
            clusters, combined_labels, 20)
        combined_clusters, combined_labels = self.check_and_combine(
            combined_clusters, combined_labels, 30)
        return combined_clusters, combined_labels

    def check_and_combine(self, clusters, labels, threshold):
        stock_list = []
        for i in range(len(clusters)):
            stock = []
            for k in range(len(clusters)):
                cnt = 0
                if i == k:
                    continue
                for i2 in range(len(clusters[i])):
                    for k2 in range(len(clusters[k])):
                        if clusters[i][i2] == clusters[k][k2]:
                            cnt += 1
                            break
                if (2*cnt/(len(clusters[i])+len(clusters[k])-2*cnt)*100) >= threshold:
                    stock.append(labels[k])
            if len(stock) == 1:
                for l in stock:
                    stock_list.append(l)
            else:
                stock_list.append("NA")

        delete_list_clust, delete_list_label = [], []
        for i in range(len(stock_list)):
            if not stock_list[i] == "NA":
                if stock_list[i] in labels:
                    indec = labels.index(stock_list[i])
                    clusters[i].extend(clusters[indec])
                    labels[i].extend(stock_list[i])
                    labels[i] = list(set(labels[i]))
                    delete_list_clust.append(clusters[indec])
                    delete_list_label.append(stock_list[i])

        for i in range(len(delete_list_clust)):
            if (delete_list_clust[i] in clusters) and (delete_list_label[i] in labels):
                clusters.pop(clusters.index(delete_list_clust[i]))
                labels.pop(labels.index(delete_list_label[i]))
        for i in range(len(clusters)):
            labels[i] = list(set(labels[i]))

        for i in range(len(labels) - 1):  # 重複しているラベルを消していく
            for k in range(i, len(labels)):
                if i == k:
                    continue
                # setを用いることで順不同になる
                if set(labels[i]) == set(labels[k]) and len(labels[i]) == len(labels[k]):
                    clusters.pop(labels.index(labels[k]))
                    labels.pop(labels.index(labels[k]))

        # クラスタ内の要素の重複を解消したい
        for i in range(len(clusters)):
            clusters[i] = list(set(clusters[i]))
            labels[i] = list(set(labels[i]))
        return clusters, labels
