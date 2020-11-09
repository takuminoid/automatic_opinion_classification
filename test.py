from classificate_opinions import ClassificateOpinions

c = ClassificateOpinions(['こんにちは。・おはよう', 'こんばんは'])
out = c.text_spliter(['こんにちは。・おはよう', 'こんばんは'])
if out == ['こんにちは', 'おはよう', 'こんばんは']:
  print('ok')
else:
  print('error1')
