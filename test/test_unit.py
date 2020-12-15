import unittest
import sys
sys.path.append('./')
from classificate_opinions import ClassificateOpinions

class TestClassificateOpinions(unittest.TestCase):
    
    def setUp(self):
        opinions = ['保育園の数が少なく入れるか不安', '保育園の数を増やしてください！', '学童を増やして欲しいです', 'あ']
        self.c = ClassificateOpinions(opinions)
        self.c.create_graph(self.c.gr, self.c.opinions)

    def test_text_splitter(self):
        out = self.c.text_splitter(['こんにちは。・おはよう', '①こんばんは②そうなのですか'])
        ans = ['こんにちは', 'おはよう', 'こんばんは', 'そうなのですか']
        self.assertEqual(out, ans)
    
    def test_num_zen_to_jan(self):
        out = self.c.num_zen_to_han(['12おはよう', '３４です', 'おは５6'])
        ans = ['12おはよう', '34です', 'おは56']
        self.assertEqual(out, ans)

    def test_create_graph(self):
        out = len(self.c.gr.nodes)
        ans = len(self.c.opinions)
        self.assertEqual(out, ans)

    def test_create_stopwords_list(self):
        out = len(self.c.ngwords)
        ans = 560
        self.assertEqual(out, ans)

    def test_tokenize(self):
        out = self.c.tokenize(['保育園の数が少なく入れるか不安', '保育園の数を増やして！', '学童を増やして欲しいです'])
        ans = [['保育園', '入れる', '不安'], ['保育園', '増やす'], ['学童', '増やす']]
        self.assertEqual(out, ans)

    def test_remove_stopwords(self):
        out = self.c.remove_stopwords([['今日', '今日', '明日'], ['今日', '昨日']])
        ans = [['明日'], ['昨日']]
        self.assertEqual(out, ans)

    def test_extract_large_cliques(self):
        out = self.c.extract_large_cliques([
            ['a', 'b'], ['a', 'c', 'b'], ['c'],
            ['a'], ['a', 'b'], ['a', 'c', 'b', 'd'],
            ])
        ans = [['a', 'c', 'b', 'd']] # 最も大きいリストが帰ってくる
        self.assertEqual(out, ans)

if __name__=="__main__":
    unittest.main()