# remove special character
import re


def preprocessing(remark):

    remark = re.sub(r'\\s', '', remark)  # \s
    remark = re.sub(r'\\n', '', remark)  # \n
    remark = re.sub(r'\\u', '', remark)  # \u
    remark = re.sub('\(', '', remark)  # (
    remark = re.sub('\（', '', remark)  # (
    remark = re.sub('\）', '', remark)  # )
    remark = re.sub('\,\)', '', remark)  # ,)
    remark = re.sub('\'', '', remark)  # "
    remark = re.sub('、', '', remark)  # 、
    remark = re.sub('。', '', remark)  # 。
    # remark = re.sub('・', '', remark)#・
    remark = re.sub('※', '', remark)  # ※
    remark = re.sub('！', '', remark)  # ！
    remark = re.sub('あづけ', '預け', remark)
    remark = re.sub('ギモン', '疑問', remark)
    remark = re.sub('子ども', '子供', remark)
    remark = re.sub('こども', '子供', remark)
    remark = re.sub('smartphone', 'スマートフォン', remark)
    remark = re.sub('smart phone', 'スマートフォン', remark)
    remark = re.sub('スマホ', 'スマートフォン', remark)
    remark = re.sub('スマートホン', 'スマートフォン', remark)

    return remark
