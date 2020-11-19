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
    clusters, labels = c.classificate()
    elapsed_time = time.time() - start

    ans_len_gredges = 160670
    ans_len_gr2edges = 11799
    ans_len_clusters = 42
    ans_len_labels = 42

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

    print("labels: ",labels)
    print("time: ", elapsed_time, "(sec)", end = "\n")
