import nltk
from nltk import Nonterminal, Production, ProbabilisticProduction
from nltk.corpus import floresta
from nltk.grammar import PCFG, induce_pcfg
from nltk.parse import pchart, ViterbiParser
# import numpy as np

nltk.download('floresta')

initial_symbols = []
productions = []
test = []
x = 0

def simplify_tag(t):
    if "+" in t:
        return t[t.rfind("+")+1:]
    else:
        return t

def metodo(tree):
    tree.set_label(simplify_tag(tree.label()))
    if tree.height() > 2:
        for i in range(0,len(tree)):
            metodo(tree[i])

def filter_errors(trees):
    # print("FILTER ERRORS...")
    global initial_symbols
    global productions
    global test

    limite = int(len(trees)*0.75)
    count=0
    for tree in trees[:limite]:
        try:
            metodo(tree)
            initial_symbols.append(tree.productions()[0].lhs())
            productions += tree.productions()
            count +=1
        except AttributeError:
            pass

    for tree in trees[limite:]:
        try:
            metodo(tree)
            test.append(tree)
        except AttributeError:
            pass
    
    # print("FIM FILTER ERRORS...", count)


def make_list_evaluation(tree,list_eval,list_tag,index):
    global x
    simbol = tree.label()   
    inicio = index
    if tree.height() > 2:
        posicao = x
        x += 1
        for i in range(0,len(tree)):
            index = make_list_evaluation(tree[i],list_eval,list_tag, index)
            
        list_eval += [(simbol, inicio, index, posicao)]
        return index
    else:
        list_tag.append(simbol)
        return index+1

def do_cky(grammar):
    global test
    global x
    print("CKY...",len(test))
    
    viterbi = ViterbiParser(grammar)
    resultados = []
    for t in test:
        try:
            sent = t.leaves()

            if len(sent) <= 18:
                ssent = []        
                for s in sent:
                    try:
                        grammar.check_coverage([s])
                        ssent.append(s)
                    except ValueError:
                        ssent.append("UNK")
                print(sent)
                print(ssent)

                saida = []
                for i in viterbi.parse(ssent):
                    saida.append(i)

                list_eval_val = []
                list_eval_test = []
                list_tag_val = []
                list_tag_test = []
                # saida[0][0].draw()
                # t.draw()
                x = 0
                make_list_evaluation(saida[0][0],list_eval_test,list_tag_test,0)
                x = 0
                make_list_evaluation(t,list_eval_val,list_tag_val, 0)    
                
                list_eval_test.sort(key=lambda tup: tup[3])
                list_eval_val.sort(key=lambda tup: tup[3])

                # print('test',list_eval_test,'val',list_eval_val)
                acertos = len(set(list_eval_test).intersection(set(list_eval_val)))
                # print(acertos)
                # labeled precision
                lp = acertos/len(list_eval_test)
                # print(lp)
                # labeled recall
                lr = acertos/len(list_eval_val)
                # print(lp)
                # f1
                f1 = 0
                if lp > 0 and lr > 0:
                    f1 = 2*lp*lr/(lp+lr)
                # tagging accuracy
                # print('test',list_tag_test,'val',list_tag_val)
                ta = 0
                ta = len([i for i, j in zip(list_tag_test, list_tag_val) if i == j])
                ta /= len(list_tag_val)
                print(ta)
                r = {'lp':lp, 'lr': lr, 'f1':f1, 'ta':ta}
                print('r',r)
                resultados.append(r)
            else:
                print("PULOU")
        except Exception:
            print("excecao")

    # print(resultados)
    media_lp = sum(item['lp'] for item in resultados)/len(resultados)
    media_lr = sum(item['lr'] for item in resultados)/len(resultados)
    media_f1 = sum(item['f1'] for item in resultados)/len(resultados)
    media_ta = sum(item['ta'] for item in resultados)/len(resultados)
    print("media_lp",media_lp,"media_lr",media_lr,"media_f1",media_f1,"media_ta",media_ta)
    print("FINISH")

filter_errors(floresta.parsed_sents())

roots = []
ROOT = Nonterminal('ROOT')
# print("adicionando simbolos iniciais")
initial_symbols = list(set(initial_symbols)) # remover repetidos
for t in initial_symbols:
    roots += [Production(ROOT,[t])]

productions += roots
productions += [Production(Nonterminal("n"), ["UNK"])]

print("pcfg iniciado...", len(productions))#, test[20:40])
pcfg = induce_pcfg(ROOT, productions)
print("pcfg finalizado...")
do_cky(pcfg)