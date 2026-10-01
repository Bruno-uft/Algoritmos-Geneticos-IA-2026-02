import random

class Individuo:
    def __init__(self, cromossomo=None):
        self.cromossomo = cromossomo if cromossomo else []
        self.fitness = 0
        
    def __str__(self):
        return f"Cromossomo: {''.join(self.cromossomo)}\nTamanho: {len(self.cromossomo)}\nFitness: {self.fitness}"

def criar_cromossomo_aleatorio(dist_manhattan):
    tam_cromo = dist_manhattan + random.randint(1, dist_manhattan)
    direcoes = ['C', 'B', 'E', 'D']
    return [random.choice(direcoes) for _ in range(tam_cromo)]

def gerar_cromossomo_valido(labirinto, dist_manhattan):
    tam_cromo = dist_manhattan + random.randint(1, dist_manhattan)
    direcoes = ['C', 'B', 'E', 'D']
    di = [-1, 1, 0, 0]
    dj = [0, 0, -1, 1]
    
    i, j = labirinto.inicio_i, labirinto.inicio_j
    cromossomo = []
    
    for _ in range(tam_cromo):
        direcoes_validas = []
        for d in range(4):
            ni = i + di[d]
            nj = j + dj[d]
            c = labirinto.get(ni, nj)
            if c != '#' and c != 'x':
                direcoes_validas.append(d)
                
        if direcoes_validas:
            mov = random.choice(direcoes_validas)
            cromossomo.append(direcoes[mov])
            i += di[mov]
            j += dj[mov]
        else:
            cromossomo.append(random.choice(direcoes))
            
    return cromossomo

def selecao_roleta(populacao):
    soma_fitness = sum(ind.fitness for ind in populacao)
    selecionados = []
    
    for _ in range(len(populacao) // 2):
        if soma_fitness == 0:
            roleta = 0
        else:
            roleta = random.randint(0, soma_fitness)
            
        acumulado = 0
        for ind in populacao:
            acumulado += ind.fitness
            if acumulado >= roleta:
                selecionados.append(ind)
                break
                
    return selecionados

def crossover(pai1, pai2):
    ponto1 = len(pai1.cromossomo) // 2
    ponto2 = len(pai2.cromossomo) // 2
    
    filho_cromossomo = pai1.cromossomo[:ponto1] + pai2.cromossomo[ponto2:]
    return Individuo(filho_cromossomo)

def mutacao(indv, taxa):
    direcoes = ['C', 'B', 'E', 'D']
    for i in range(len(indv.cromossomo)):
        if random.random() < taxa:
            indv.cromossomo[i] = random.choice(direcoes)

def avaliar_individuo(indv, labirinto, config, mostrar=False):
    final_i, final_j, colisoes, mapa_sim = labirinto.simular_caminho(indv.cromossomo)
    indv.fitness = labirinto.calcular_fitness(final_i, final_j, colisoes, config)
    if mostrar:
        labirinto.imprimir_simulacao(mapa_sim, indv.fitness)
    return indv.fitness

def loop_evolutivo(populacao, labirinto, config, log_file=None):
    solucao_encontrada = False
    
    for ger in range(1, config.geracoes + 1):
        populacao.sort(key=lambda x: x.fitness, reverse=True)
        melhor = populacao[0]
        
        cromo_str = ''.join(melhor.cromossomo)
        if log_file:
            log_file.write(f"{ger};{melhor.fitness};{cromo_str}\n")
            log_file.flush()
            
        print(f"\n-> Geracao {ger}:")
        print("Melhor individuo:")
        print(melhor)
        print("----------------")
        
        if melhor.fitness == 1000:
            solucao_encontrada = True
            print("Solucao encontrada!")
            break
            
        selecionados = selecao_roleta(populacao)
        if not selecionados:
            print("Erro na selecao por roleta")
            break
            
        nova_pop = []
        n_elite = int(config.taxa_elitismo * len(populacao))
        
        #elitismo
        for i in range(min(n_elite, len(populacao))):
            #clonar o indivíduo para não referenciar o mesmo objeto sofrendo mutação
            nova_pop.append(Individuo(list(populacao[i].cromossomo)))
            nova_pop[-1].fitness = populacao[i].fitness
            
        #cruzamento e mutação
        selecionados_size = len(selecionados)
        while len(nova_pop) < config.tamanho_populacao:
            if selecionados_size == 0:
                break
                
            pai1 = selecionados[random.randint(0, selecionados_size - 1)]
            pai2 = selecionados[random.randint(0, selecionados_size - 1)]
            
            filho = crossover(pai1, pai2)
            mutacao(filho, config.taxa_mutacao)
            avaliar_individuo(filho, labirinto, config)
            nova_pop.append(filho)
            
        populacao = nova_pop
        
    return solucao_encontrada, populacao
