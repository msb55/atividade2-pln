import nltk
from nltk import Nonterminal, Production
from nltk.corpus import floresta
from nltk.grammar import induce_pcfg
from nltk.parse import ViterbiParser

nltk.download('floresta')

initial_symbols = []
productions = []
test = []
posx = 0

# remover informacoes sintaticas
def simplify_tag(t):
    if "+" in t:
        return t[t.rfind("+")+1:]
    else:
        return t

# percorrer pela arvore para remover informacoes sintaticas
def simplify_tree(tree):
    tree.set_label(simplify_tag(tree.label()))
    if tree.height() > 2:
        for i in range(0,len(tree)):
            simplify_tree(tree[i])

# processamento da base de dados floresta
def filter_errors(trees):
    global initial_symbols
    global productions
    global test

    limite = int(len(trees)*0.75) # divisao dos 75% para treinamento
    for tree in trees[:limite]:
        try:
            simplify_tree(tree) # remover informacoes sintaticas
            initial_symbols.append(tree.productions()[0].lhs()) # capturar os simbolos iniciais de cada arvore
            productions += tree.productions() # conjunto de todas regras
        except AttributeError: # para casos de arvores mal formadas
            pass

    # 25% da base para teste
    for tree in trees[limite:]:
        try:
            simplify_tree(tree) # remover informacoes sintaticas
            test.append(tree) # conjunto das arvores de teste
        except AttributeError: # para casos de arvores mal formadas
            pass

# realizar avaliacao da arvore
def make_tree_evaluation(tree,list_eval,list_tag,index):
    global posx
    simbol = tree.label() # guarda o simbolo do nao-terminal atual
    inicio = index # guarda a posicao da palavra na arvore (0 word_0 1 word_1 2...)
    if tree.height() > 2: # caso ela tenha filhos nao-terminais
        posicao = posx # guarda a ordem que foi visitado (primeiro, segundo...)
        posx += 1
        for i in range(0,len(tree)): # realiza busca em profundidade
            index = make_tree_evaluation(tree[i],list_eval,list_tag, index)
            
        list_eval += [(simbol, inicio, index, posicao)] # salva o simbolo apos a visitacao de sua sub-arvore
        return index
    else:
        list_tag.append(simbol) # salva o nao-terminal que gerou o terminal (word)
        return index+1

# realiza a chamada ao parser (ViterbiParser)
def do_cky(grammar):
    global test
    global posx
    
    viterbi = ViterbiParser(grammar) # inicializa o parser com a gramatica (PCFG)
    resultados = []
    for t in test[:1]: # para cada sentenca da base de teste
        try:
            sent = t.leaves() # pega a frase

            if len(sent) <= 18: # filtro para palavras com até 18 palavras (incluindo pontuação)
                ssent = []
                for s in sent: # checar a cobertura da gramatica para cada palavra
                    try:
                        grammar.check_coverage([s])
                        ssent.append(s)
                    except ValueError: # para os casos de palavras desconhecidas
                        ssent.append("UNK")

                saida = []
                for i in viterbi.parse(ssent): # utiliza o parser para a sentenca de teste
                    saida.append(i)

                # lista para o resultado das duas vertentes: descobrir os não-terminais que original os terminais; e identificar os não-terminais que derivam as palavras
                list_eval_val = []
                list_eval_test = []
                list_tag_val = []
                list_tag_test = []
                
                posx = 0
                make_tree_evaluation(saida[0][0],list_eval_test,list_tag_test,0) # realiza a avalicao para o resultado do parser
                posx = 0
                make_tree_evaluation(t,list_eval_val,list_tag_val, 0) # realiza a avalicao para a arvore da base de teste
                
                # ordena pela ordem de visitacao
                list_eval_test.sort(key=lambda tup: tup[3])
                list_eval_val.sort(key=lambda tup: tup[3])

                # quantidade de acertos
                acertos = len(set(list_eval_test).intersection(set(list_eval_val)))
                # labeled precision
                lp = acertos/len(list_eval_test)
                # labeled recall
                lr = acertos/len(list_eval_val)
                # f1
                f1 = 0
                if lp > 0 and lr > 0:
                    f1 = 2*lp*lr/(lp+lr)
                # tagging accuracy
                ta = 0
                ta = len([i for i, j in zip(list_tag_test, list_tag_val) if i == j])
                ta /= len(list_tag_val)
                
                # armazena o resultado
                r = {'lp':lp, 'lr': lr, 'f1':f1, 'ta':ta}
                resultados.append(r)
            else:
                print("Sentença com mais de 18 palavras.")
        except Exception:
            print("Árvore mal formada.")

    # realiza o calculo da media para cada metrica
    media_lp = sum(item['lp'] for item in resultados)/len(resultados)
    media_lr = sum(item['lr'] for item in resultados)/len(resultados)
    media_f1 = sum(item['f1'] for item in resultados)/len(resultados)
    media_ta = sum(item['ta'] for item in resultados)/len(resultados)
    print("media_lp",media_lp,"media_lr",media_lr,"media_f1",media_f1,"media_ta",media_ta)

# extrai as arvores da base de dados floresta, com suas respectivas tags
filter_errors(floresta.parsed_sents())

roots = []
ROOT = Nonterminal('ROOT') # nao-terminal representado o simbolo inicial da gramatica
initial_symbols = list(set(initial_symbols)) # remover repetidos
for t in initial_symbols:
    roots += [Production(ROOT,[t])] # unificar a gramatica para apenas um simbolo inicial

productions += roots
productions += [Production(Nonterminal("n"), ["UNK"])] # regra para palavras desconhecidas (substantivo)

pcfg = induce_pcfg(ROOT, productions) # cria a PCFG informando o simbolo inicial e as regras
do_cky(pcfg) # aplica o algoritmo CKY (ViterbiParser)