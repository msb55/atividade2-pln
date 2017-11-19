import nltk
from nltk import Nonterminal, Production, ProbabilisticProduction
from nltk.corpus import floresta
from nltk.grammar import PCFG
from nltk.parse import pchart, ViterbiParser

nltk.download('floresta')

initial_symbols = []
productions = []
test = []

def filter_errors(trees):
    print("FILTER ERRORS...")
    global initial_symbols
    global productions
    global test

    count = 0
    limite = int(len(trees)*0.75)
    
    for t in trees:
        try:
            t.chomsky_normal_form()
            if count < limite:
                initial_symbols.append(t.productions()[0].lhs())
                productions += t.productions()
            else:
                test += [t]
                
            count += 1
        except AttributeError:
            pass

# Count(a -> b) / Count(a)
def get_pcfg(root, productions):
    print("GET_PCFG...")
    heads = {}
    prods = {}
    for p in productions:
        if p in prods:
            prods[p] += 1
        else:
            prods[p] = 1

        if p.lhs() in heads:
            heads[p.lhs()] += 1
        else:
            heads[p.lhs()] = 1
    
    rules = []
    for p in list(prods.keys()):
        prob = prods[p]/heads[p.lhs()]
        rules.append(ProbabilisticProduction(p.lhs(),p.rhs(),prob=prob))
    
    pcfg = PCFG(root, rules)
    return pcfg

def do_cky(grammar, test):
    print("CKY...")
    viterbi = ViterbiParser(grammar)
    sent = test[0].leaves()
    print(sent)
    for t in viterbi.parse(sent):
        print(t)

    print("FINISH")

filter_errors(floresta.parsed_sents())

roots = []
ROOT = Nonterminal('ROOT')
initial_symbols = list(set(initial_symbols)) # remover repetidos
for t in initial_symbols:
    roots += [Production(ROOT,[t])]

productions += roots

pcfg = get_pcfg(ROOT, productions)
print("pcfg finalizado...")
do_cky(pcfg, test)

# inicio 