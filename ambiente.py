import os
from collections import deque
import math

class Configuracao:
    def __init__(self, filename):
        self.taxa_elitismo = None
        self.taxa_mutacao = None
        self.tamanho_populacao = None
        self.geracoes = None
        self.tipo_geracao = None
        self.saida_log = None
        
        self._load(filename)
        
    def _load(self, filename):
        if not os.path.exists(filename):
            raise FileNotFoundError(f"Erro: Arquivo de configuração '{filename}' não encontrado.")
            
        with open(filename, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    if key == "taxa_elitismo":
                        self.taxa_elitismo = float(value)
                    elif key == "taxa_mutacao":
                        self.taxa_mutacao = float(value)
                    elif key == "tamanho_populacao":
                        self.tamanho_populacao = int(value)
                    elif key == "geracoes":
                        self.geracoes = int(value)
                    elif key == "tipo_geracao":
                        self.tipo_geracao = value
                    elif key == "saida_log":
                        self.saida_log = value

class Labirinto:
    def __init__(self, filename):
        self.linhas = 0
        self.colunas = 0
        self.matriz = []
        self.inicio_i = -1
        self.inicio_j = -1
        self.fim_i = -1
        self.fim_j = -1
        
        self._load(filename)
        
    def _load(self, filename):
        if not os.path.exists(filename):
            raise FileNotFoundError(f"Arquivo de labirinto '{filename}' não encontrado.")
            
        with open(filename, 'r') as f:
            lines = f.readlines()
            
        #primeira linha tem linhas e colunas
        dims = lines[0].strip().split()
        if len(dims) >= 2:
            self.linhas = int(dims[0])
            self.colunas = int(dims[1])
        
        #o resto é a matriz do labirinto
        maze_lines = [list(line.replace('\n', '').replace('\r', '')) for line in lines[1:] if line.strip() or ' ' in line]
        
        for i in range(min(self.linhas, len(maze_lines))):
            row = []
            for j in range(min(self.colunas, len(maze_lines[i]))):
                char = maze_lines[i][j]
                row.append(char)
                if char == 'S':
                    self.inicio_i = i
                    self.inicio_j = j
                elif char == 'E':
                    self.fim_i = i
                    self.fim_j = j
            self.matriz.append(row)
            
    def get(self, i, j):
        if 0 <= i < self.linhas and 0 <= j < self.colunas:
            return self.matriz[i][j]
        return 'x'
        
    def distancia_minima(self):
        dx = [1, -1, 0, 0]
        dy = [0, 0, 1, -1]
        
        fila = deque([(self.inicio_i, self.inicio_j, 0)])
        visitado = set([(self.inicio_i, self.inicio_j)])
        
        while fila:
            i, j, dist = fila.popleft()
            
            if i == self.fim_i and j == self.fim_j:
                return dist
                
            for k in range(4):
                ni = i + dx[k]
                nj = j + dy[k]
                
                if self.get(ni, nj) != '#' and (ni, nj) not in visitado:
                    visitado.add((ni, nj))
                    fila.append((ni, nj, dist + 1))
                    
        return 1
        
    def simular_caminho(self, cromossomo):
        i, j = self.inicio_i, self.inicio_j
        colisoes = 0
        mapa_sim = [row[:] for row in self.matriz]
        
        for mov in cromossomo:
            ni, nj = i, j
            if mov == 'C': ni -= 1
            elif mov == 'B': ni += 1
            elif mov == 'E': nj -= 1
            elif mov == 'D': nj += 1
            
            c = self.get(ni, nj)
            if c == 'x' or c == '#':
                colisoes += 1
                break
                
            i, j = ni, nj
            
            if mapa_sim[i][j] == ' ':
                mapa_sim[i][j] = '@'
                
            if self.matriz[i][j] == 'E':
                break
                
        return i, j, colisoes, mapa_sim
        
    def calcular_fitness(self, final_i, final_j, colisoes, config):
        dx = abs(self.fim_i - final_i)
        dy = abs(self.fim_j - final_j)
        dist = dx + dy
        
        if config.tipo_geracao == "movimentos_validos":
            return int(1000 - dist * 100)
        else:
            return int(1000 - dist * 50 - colisoes * 50)
            
    def imprimir_simulacao(self, mapa_sim, fitness):
        for row in mapa_sim:
            print("".join(row))
        print(f"Fitness: {fitness}\n")
