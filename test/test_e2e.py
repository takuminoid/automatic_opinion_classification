import os
import sys
import elsx_to_list
import time
sys.path.append('./')
from classificate_opinions import ClassificateOpinions


list_detail = []
list_detail = elsx_to_list.input(
    2, "Detail", os.path.abspath("test/data/test_data.xlsx"))

print(len(list_detail))

start = time.time()
c = ClassificateOpinions(list_detail)
clusters, labels = c.classificate()
elapsed_time = time.time() - start

print(len(clusters))
print(len(labels))
print(labels)
print("time: ", elapsed_time, "(sec)", end = "\n")

