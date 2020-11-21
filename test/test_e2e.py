import os
import sys
import elsx_to_list
import time
sys.path.append('./')
from classificate_opinions import ClassificateOpinions


def check(ans, out):
    return 'ok' if out == ans else 'error'


if __name__ == "__main__":
    list_detail = []
    list_detail = elsx_to_list.input(
        2, "Detail", os.path.abspath("test/data/test_data.xlsx"))

    print(len(list_detail))

    start = time.time()
    c = ClassificateOpinions(list_detail)
    outputs = c.classificate()
    elapsed_time = time.time() - start

    # loop=10 時
    ans_len_gredges = 163724
    ans_len_gr2edges = 11187
    ans_len_clusters = 38
    ans_len_labels = 38 + 1
    ans_len_label_nums = len(list_detail)

    # gr エッジ数
    ans, out = ans_len_gredges, len(c.gr.edges)
    print("len(gr.edges): ", out, check(ans, out))
    # gr2 エッジ数
    ans, out = ans_len_gr2edges, len(c.gr2.edges)
    print("len(gr2.edges): ", out, check(ans, out))
    # クラスター数
    ans, out = ans_len_clusters, len(c.clusters)
    print("len(clusters): ", out, check(ans, out))
    # label数
    ans, out = ans_len_labels, len(c.labels)
    print("len(labels): ", out, check(ans, out))
    # label_num数
    ans, out = ans_len_label_nums, len(outputs[0])
    print("len(label_nums): ", out, check(ans, out))

    print("labels: ", outputs[1])
    # 意見ごとのラベル表示
    # for i in label_nums:
    #     print('[', end='')
    #     for l in i:
    #         print(c.labels[l], end=', ')
    #     print(']', end=', ')
    print("time: ", elapsed_time, "(sec)", end="\n")
    # データ数 1395
    # loop=10 => 10 sec 程度
    # loop=100,000 => 300 sec 程度

    # print(outputs)
