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
    c = ClassificateOpinions(['こんにちは。・おはよう', 'こんばんは'])
    c.classificate()

    # def text_spiliter
    out = c.text_splitter(['こんにちは。・おはよう', '①こんばんは②そうなのですか'])
    ans = ['こんにちは', 'おはよう', 'こんばんは', 'そうなのですか']
    res(1, out, ans)

    # def num_zen_to_han
    out = c.num_zen_to_han(['12おはよう', '３４です', 'おは５6'])
    ans = ['12おはよう', '34です', 'おは56']
    res(2, out, ans)

    # def create_stopwords_list
    out = len(c.ngwords)
    ans = 560
    res(3, out, ans)

    # def tokenize
    out = c.tokenize(['今日で子供の家を退園します', '児童クラブを増やして欲しい'])
    ans = [['今日', '退園', '子供の家'], ['児童クラブ', '増やす']]
    res(4, out, ans)

    # def remove_stopwords
    out = c.remove_stopwords([['今日', '今日', '明日'], ['今日', '昨日']])
    ans = [['明日'], ['昨日']]
    res(5, out, ans)
