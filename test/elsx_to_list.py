import pandas as pd
import mojimoji as mj


def input(sheet_num, column_name, path):

    for j in range(sheet_num):
        if j == 0:
            df = pd.read_excel(path, sheet_name=j, usecols=[1, 2])
        else:
            df2 = pd.read_excel(path, sheet_name=j, usecols=[1, 2])
            df = pd.concat([df, df2])
    df = df.dropna(how='any')

    split_list = ['。・', '？・']
    split_list2 = ['②', '③', '④', '⑤', '⑥', '⑦', '⑧', '⑨']
    list_detail = []
    for s in zip(df[column_name]):
        s = (str)(s)
        flag = False
        if '①' in s:  # 文中に①がある場合は，②以降も同じ話題である可能性が高いと感じる
            for sl in split_list2:
                if sl in s:
                    s_buf = s.split(sl)
                    list_detail.append(s_buf[0])
                    s = s_buf[1]
                    flag = True
            list_detail.append(s)
        if not flag:
            for sl in split_list:
                if sl in s:
                    list_detail.extend(s.split(sl))
                    flag = True
        if not flag:
            list_detail.append(s)

    # 数字を半角に統一
    for i in range(len(list_detail)):
        list_detail[i] = mj.zen_to_han(list_detail[i], kana=False, ascii=False)

    return list_detail
