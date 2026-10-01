import random
import sys
from ambiente import Configuracao, Labirinto
from algoritmo_genetico import (
    Individuo,
    criar_cromossomo_aleatorio,
    gerar_cromossomo_valido,
    avaliar_individuo,
    loop_evolutivo
)

def main():
    #inicialização aleatória
    random.seed()
    
    print("Iniciando Algoritmo Genético para Resolução de Labirinto...")
    
    #carregar config.ini
    try:
        config = Configuracao("config.ini")
    except Exception as e:
        print(f"Erro ao carregar configuracao: {e}")
        sys.exit(1)
        
    print(f"-> Tipo de geracao atual: {config.tipo_geracao}")
    
    #carregar labirinto
    try:
        labirinto = Labirinto("labirinto.txt")
    except Exception as e:
        print(f"Erro ao carregar labirinto: {e}")
        sys.exit(1)
        
    #calcular distância mínima
    dist_manhattan = labirinto.distancia_minima()
    print(f"\n-> Distancia minima calculada: {dist_manhattan}")
    
    #criar população inicial
    populacao = []
    for _ in range(config.tamanho_populacao):
        if config.tipo_geracao == "movimentos_validos":
            cromo = gerar_cromossomo_valido(labirinto, dist_manhattan)
        else:
            cromo = criar_cromossomo_aleatorio(dist_manhattan)
            
        indv = Individuo(cromo)
        avaliar_individuo(indv, labirinto, config)
        populacao.append(indv)
        
    #preparar arquivo de log
    try:
        log_file = open(config.saida_log, "w")
        log_file.write("geracao;fitness;cromossomo\n")
    except IOError:
        print("Erro ao criar arquivo de log")
        log_file = None
        
    #executar o processo evolutivo
    solucao_encontrada, populacao = loop_evolutivo(populacao, labirinto, config, log_file)
    
    #processar resultado final
    if solucao_encontrada:
        populacao.sort(key=lambda x: x.fitness, reverse=True)
        melhor_final = populacao[0]
        print("\n-> Simulacao da solucao:")
        avaliar_individuo(melhor_final, labirinto, config, mostrar=True)
    else:
        print("Solucao nao encontrada")
        
    if log_file:
        log_file.close()

if __name__ == "__main__":
    main()
