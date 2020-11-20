import sys
sys.path.append('./')
from classificate_opinions import ClassificateOpinions


def res(num, out, ans):
    if out == ans:
        print(num, 'ok')
    else:
        print(num, 'error')
        print('expected is ', ans, ', your out is', out)


if __name__ == "__main__":
    # opinions = ['今日で子供の家を退園します', '児童クラブを増やして欲しい', 'あ']
    opinions = ['保育園の数が少なく入れるか不安', '保育園の数を増やしてください！', '学童を増やして欲しいです', 'あ']
    c = ClassificateOpinions(opinions)
    # c.classificate()

    # _def text_spiliter
    out = c.text_splitter(['こんにちは。・おはよう', '①こんばんは②そうなのですか'])
    ans = ['こんにちは', 'おはよう', 'こんばんは', 'そうなのですか']
    res(1, out, ans)

    # _def num_zen_to_han
    out = c.num_zen_to_han(['12おはよう', '３４です', 'おは５6'])
    ans = ['12おはよう', '34です', 'おは56']
    res(2, out, ans)

    # def create_graph
    out = len(c.gr.nodes)
    ans = 0
    res(3, out, ans)

    c.create_graph(c.gr, c.opinions)
    out = len(c.gr.nodes)
    ans = len(opinions)
    res(4, out, ans)

    c.node_buf = list(c.gr.nodes)

    # _def create_stopwords_list
    out = len(c.ngwords)
    ans = 560
    res(5, out, ans)

    # _def tokenize
    out = c.tokenize(['保育園の数が少なく入れるか不安', '保育園の数を増やして！', '学童を増やして欲しいです'])
    ans = [['保育園', '入れる', '不安'], ['保育園', '増やす'], ['学童', '増やす']]
    res(6, out, ans)

    # _def remove_stopwords
    out = c.remove_stopwords([['今日', '今日', '明日'], ['今日', '昨日']])
    ans = [['明日'], ['昨日']]
    res(7, out, ans)

    # def remove_minority_opinions
    c.remove_minority_opinions(
        [['保育園', '入れる', '不安'], ['保育園', '増やす'], ['学童', '増やす'], []])
    out = len(c.gr.nodes)
    ans = 3
    res(8, out, ans)

    # def connect_edge
    c.connect_edge([['保育園', '入れる', '不安'], ['保育園', '増やす'], ['学童', '増やす']])
    out = len(c.gr.edges)
    ans = 1
    res(9, out, ans)

    # def extract_maximul_cliques
    out = c.extract_maximal_cliques()
    ans = [['保育園の数が少なく入れるか不安', '保育園の数を増やしてください！'], [
        '保育園の数を増やしてください！', '保育園の数が少なく入れるか不安'], ['学童を増やして欲しいです']]
    res(10, out, ans)

    # _def extract_large_cliques
    out = c.extract_large_cliques([
        ['a', 'b'], ['a', 'c', 'b'], ['c'],
        ['a'], ['a', 'b'], ['a', 'c', 'b', 'd'],
        ])
    ans = [['a', 'c', 'b', 'd']] # 最も大きいリストが帰ってくる
    res(11, out, ans)

    # __def create_graph
    out = len(c.gr2.nodes)
    ans = 0
    res(12, out, ans)

    ex_large_cliques = [
        ['a', 'b'], ['c', 'd', 'e'], ['f'],
        ['g'], ['h', 'i'], ['j', 'k', 'l', 'm'],
        ['n', 'o'], ['p', 'q', 'r'], ['s'],
        ['t'], ['a', 'b'], ['w', 'y', 'z', 'a'],
        ]
    c.create_graph_index(c.gr2, ex_large_cliques)
    out = len(c.gr2.nodes)
    ans = 12
    res(13, out, ans)

    # __def connect_edge_large
    c.connect_edge_large(ex_large_cliques)
    out = len(c.gr2.edges) 
    ans = 3 # (0,10), (0, 11), (10, 11)
    res(14, out, ans)

    # __def extract_clusters_large
    out = c.extract_clusters_large(c.gr2, ex_large_cliques)
    ans = [['a', 'w', 'y', 'z', 'b']]
    res(15, set(out[0]), set(ans[0])) # リストの中身は順不同

    out = c.data_shaping(c.node_buf, [['保育園の数が少なく入れるか不安', '保育園の数を増やしてください！'], ['保育園の数が少なく入れるか不安'], ['学童を増やして欲しいです']], ['a', 'i', 'u'])
    print(out)