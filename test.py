from classificate_opinions import ClassificateOpinions

c = ClassificateOpinions(['こんにちは。・おはよう', 'こんばんは'])

# def text_spiliter
out = c.text_splitter(['こんにちは。・おはよう', '①こんばんは②そうなのですか'])
ans = ['こんにちは', 'おはよう', 'こんばんは', 'そうなのですか']
if out == ans:
    print('ok1')
else:
    print('error1')
    print('expected is ', ans, ', your out is', out)

# def num_zen_to_han
out = c.num_zen_to_han(['12おはよう', '３４です', 'おは５6'])
ans = ['12おはよう', '34です', 'おは56']
if out == ans:
    print('ok2')
else:
    print('error2')
    print('expected is ', ans, ', your out is', out)
