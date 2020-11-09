from classificate_opinions import ClassificateOpinions

c = ClassificateOpinions(['こんにちは。・おはよう', 'こんばんは'])
out = c.text_splitter(['こんにちは。・おはよう', '①こんばんは②そうなのですか'])
if out == ['こんにちは', 'おはよう', 'こんばんは', 'そうなのですか']:
  print('ok')
else:
  print('error1')
  print('out is', out)
