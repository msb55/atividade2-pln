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
    print("FILTER ERRORS...")
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
    
    print("FIM FILTER ERRORS...", count)


def make_list_evaluation(tree,list_eval,index):
    simbol = tree.label()
   
    inicio = index;
    if tree.height() > 2:
        print(len(tree))
        for i in range(0,len(tree)):
            index = make_list_evaluation(tree[i],list_eval, index)
            
        list_eval += [(simbol, inicio, index)]
        return index;
    else:
        return index+1;

def do_cky(grammar):
    global test

    print("CKY...",len(test))
    
    viterbi = ViterbiParser(grammar)
    
    sent = test[0].leaves()
    ssent = []
    saida = []
    list_eval_val = []
    list_evel_test = []
    for s in sent:
        try:
            grammar.check_coverage([s])
            ssent.append(s)
        except ValueError:
            ssent.append("UNK")
    print(ssent)
    for t in viterbi.parse(ssent):
        # print(t)
        saida.append(t)
    make_list_evaluation(saida[0][0],list_evel_test,0)
    make_list_evaluation(test[0],list_eval_val,0)

    print(saida[0])
    print(test[0])
    print(list_evel_test)
    print(list_eval_val)
    saida[0].draw()
    test[0].draw()

    print("FINISH")

filter_errors(floresta.parsed_sents())

roots = []
ROOT = Nonterminal('ROOT')
print("adicionando simbolos iniciais")
initial_symbols = list(set(initial_symbols)) # remover repetidos
for t in initial_symbols:
    roots += [Production(ROOT,[t])]

productions += roots
productions += [Production(Nonterminal("n"), ["UNK"])]

print("pcfg iniciado...", len(productions), len(test))
pcfg = induce_pcfg(ROOT, productions)
print("pcfg finalizado...")
do_cky(pcfg)