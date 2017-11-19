import nltk
from nltk import Nonterminal, Production
from nltk.corpus import floresta
from nltk.grammar import induce_pcfg
nltk.download('floresta')

def filter_errors(trees):
    retorno = []
    for t in trees:
        try:
            t.chomsky_normal_form()
            retorno += [t]
        except AttributeError:
            pass
    return retorno

initial_symbols = []
productions = []
trees = filter_errors(floresta.parsed_sents())
test = trees[:int(len(trees)*0.75)]
for t in test:
    initial_symbols += [t.productions()[0].lhs()]
    t.chomsky_normal_form()
    productions += t.productions()

roots = []
ROOT = Nonterminal('ROOT')
initial_symbols = list(set(initial_symbols))
for t in initial_symbols:
    roots += [Production(ROOT,[t])]

productions = list(set(productions))
productions += roots

# print(productions)
print("pcfg...")
pcfg = induce_pcfg(ROOT, productions)
print(pcfg)
    
# print(filter_errors())