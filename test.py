from classificate_opinions import ClassificateOpinions

c = ClassificateOpinions(['こんにちは。・おはよう', 'こんばんは'])
out = c.text_splitter(['こんにちは。・１２おはよう１２', '①こんばんは②そうなのですか'])
ans = ['こんにちは', '12おはよう12', 'こんばんは', 'そうなのですか']
if out == ans:
  print('ok1')
else:
  print('error1')
  print('expected is ',ans, ', your out is', out)
