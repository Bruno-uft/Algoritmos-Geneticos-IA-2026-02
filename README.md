# 🧬 Labirinto Genético — Encontrar o Caminho em um Labirinto
Projeto em Python que utiliza um **Algoritmo Genético** para encontrar um caminho entre a entrada `S` e a saída `E` de um labirinto.

O indivíduo é uma sequência de movimentos (cromossomo) que é simulada no labirinto, avaliada por fitness, selecionada, cruzada e mutada ao longo das gerações até encontrar a solução (fitness = 1000).

## 🎬 Explicação em Vídeo

> 📺 **Assista à explicação do projeto:**

<iframe width="560" height="315" src="https://www.youtube.com/embed/aXQ17p9docE?si=JkYpR5rsbyOzDYrk" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

[![Assistir no YouTube](https://img.shields.io/badge/YouTube-Assistir%20ao%20v%C3%ADdeo-red?style=for-the-badge&logo=youtube)](https://www.youtube.com/watch?v=aXQ17p9docE)

---

## 📁 Estrutura do Projeto

```
LabirintoGenetico/
├── main.py               # Ponto de entrada: carrega config, cria população e roda evolução
├── ambiente.py           # Classes Configuracao e Labirinto (carregamento, BFS, simulação, fitness)
├── algoritmo_genetico.py # Classes e operadores genéticos (Individuo, seleção, crossover, mutação)
├── config.ini            # Parâmetros do experimento
├── labirinto.txt         # Mapa do labirinto
├── experimento.csv       # Log gerado (geracao;fitness;cromossomo)
└── README.md             # Este arquivo
```

## ⚙️ Requisitos

* Python 3 (sem dependências externas, só biblioteca padrão: `random`, `sys`, `os`, `collections`, `math`)

## 🚀 Como Executar

```bash
cd LabirintoGenetico
python3 main.py
```

O programa:

1. Lê `config.ini`
2. Lê `labirinto.txt`
3. Calcula a distância mínima (BFS) entre `S` e `E`
4. Cria a população inicial
5. Executa o loop evolutivo geração a geração
6. Salva o log em `experimento.csv` (caminho definido em `saida_log`)
7. Se encontrar a solução, imprime a simulação do caminho no terminal

## 🗺️ Formato do Labirinto (`labirinto.txt`)

Primeira linha: `<linhas> <colunas>`

Depois: o mapa com os caracteres:

| Símbolo | Significado |
|---------|-------------|
| `#` | Parede (colisão) |
| ` ` (espaço) | Caminho livre |
| `S` | Início |
| `E` | Saída / objetivo |
| `@` | Caminho percorrido (só na simulação impressa) |

Exemplo usado no projeto (9x10):

```
9 10
##########
#    ## E#
# ##    ##
# #   ## #
# # ##  ##
# #   #  #
# #S# ## #
#        #
##########
```

## 🔧 Configuração (`config.ini`)

Arquivo simples no formato `chave:valor`:

```ini
taxa_elitismo:0.9
taxa_mutacao:0.2
tamanho_populacao:10
geracoes: 100
tipo_geracao:aleatorio
saida_log:experimento.csv
```

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `taxa_elitismo` | float 0–1 | Fração da população preservada intacta (clonada) a cada geração. Ex: `0.9` com pop 10 = 9 elites. |
| `taxa_mutacao` | float 0–1 | Probabilidade de cada gene sofrer mutação. Ex: `0.2` = 20% por gene. |
| `tamanho_populacao` | int | Número de indivíduos por geração. |
| `geracoes` | int | Número máximo de gerações. Para antes se fitness = 1000. |
| `tipo_geracao` | `aleatorio` ou `movimentos_validos` | Estratégia de criação do cromossomo inicial e fórmula do fitness (ver abaixo). |
| `saida_log` | string | Caminho do CSV de log gerado. |

Para trocar de modo, basta editar a linha:

```ini
tipo_geracao:movimentos_validos
```

## 🧬 Como Funciona o Algoritmo Genético

### 1. Representação — Cromossomo

Cada indivíduo (`Individuo` em `algoritmo_genetico.py`) tem um `cromossomo`: lista de genes, cada gene um movimento:

| Gene | Movimento |
|------|-----------|
| `C` | Cima (`i-1`) |
| `B` | Baixo (`i+1`) |
| `E` | Esquerda (`j-1`) |
| `D` | Direita (`j+1`) |

Tamanho do cromossomo: `dist_manhattan + random(1, dist_manhattan)`, onde `dist_manhattan` aqui é na verdade a **distância mínima real calculada por BFS** em `Labirinto.distancia_minima()`.

Existem duas formas de gerar:

* **`aleatorio`** (`criar_cromossomo_aleatorio`): escolhe cada gene uniformemente entre `C, B, E, D`.
* **`movimentos_validos`** (`gerar_cromossomo_valido`): simula passo a passo a partir do `S` e, a cada posição, escolhe aleatoriamente apenas entre os vizinhos que não são parede (`#`) nem fora do mapa (`x`). Se estiver encurralado, coloca um movimento aleatório. Gera população inicial muito melhor.

### 2. Avaliação — Fitness

`Labirinto.simular_caminho(cromossomo)` percorre os movimentos a partir de `S`:

* Se bater em `#` ou sair do mapa → `colisoes += 1` e **para** a simulação.
* Se chegar em `E` → para com sucesso.
* Marca o caminho com `@` para impressão.

`Labirinto.calcular_fitness()` usa distância de Manhattan do ponto final até o objetivo (`dx + dy`):

* Modo `movimentos_validos`:
  ```
  fitness = 1000 - dist * 100
  ```
* Modo `aleatorio`:
  ```
  fitness = 1000 - dist * 50 - colisoes * 50
  ```

**Solução perfeita = fitness 1000** (distância 0 e, no modo aleatório, sem colisão). É o critério de parada em `loop_evolutivo()`.

### 3. Seleção — Roleta

`selecao_roleta(populacao)`: seleciona `len(populacao) // 2` pais com probabilidade proporcional ao fitness. Soma todos os fitness e sorteia um número; o indivíduo cujo fitness acumulado ultrapassar o sorteio é escolhido. Se a soma for 0, pega o primeiro.

### 4. Crossover (1 ponto central)

`crossover(pai1, pai2)`:

```
filho = pai1[:len(pai1)//2] + pai2[len(pai2)//2:]
```

Simples, sem corte simétrico — concatena a primeira metade do pai1 com a segunda metade do pai2.

### 5. Mutação

`mutacao(indv, taxa)`: para cada gene, com probabilidade `taxa_mutacao`, troca por uma direção aleatória (`C, B, E, D`).

### 6. Elitismo + Loop Evolutivo

`loop_evolutivo()` em `algoritmo_genetico.py`:

1. Ordena população por fitness (maior primeiro).
2. Registra o melhor no CSV e imprime no terminal.
3. Se `fitness == 1000` → sucesso, encerra.
4. Aplica roleta para selecionar pais.
5. Copia `int(taxa_elitismo * tamanho_populacao)` melhores como clones para a próxima geração.
6. Completa o resto com filhos de crossover + mutação, já avaliados.
7. Repete até `geracoes` ou solução.

Exemplo de saída no terminal:

```
-> Geracao 1:
Melhor individuo:
Cromossomo: CEEBDEEDEBCC
Tamanho: 12
Fitness: 500
----------------
...
Solucao encontrada!

-> Simulacao da solucao:
##########
#    ##@E#
...
Fitness: 1000
```

## 📊 Log do Experimento (`experimento.csv`)

Cabeçalho `geracao;fitness;cromossomo`, separado por `;`:

```csv
geracao;fitness;cromossomo
1;500;CEEBDEEDEBCC
2;500;CEEBDEEDEBCC
4;550;CDECEEECDCECE
```

Serve para plotar curva de convergência (geração x fitness) ou analisar diversidade dos cromossomos.

## 👨‍💻 Arquivos em Detalhe

* **`ambiente.py`**: `Configuracao` (parser do `config.ini`) e `Labirinto` (`get`, `distancia_minima` via BFS com `deque`, `simular_caminho`, `calcular_fitness`, `imprimir_simulacao`).
* **`algoritmo_genetico.py`**: `Individuo`, `criar_cromossomo_aleatorio`, `gerar_cromossomo_valido`, `selecao_roleta`, `crossover`, `mutacao`, `avaliar_individuo`, `loop_evolutivo`.
* **`main.py`**: orquestra tudo, trata erros de arquivo, cria `experimento.csv` e imprime a simulação final com `mostrar=True`.
