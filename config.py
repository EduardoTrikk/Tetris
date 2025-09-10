LARGURA, ALTURA = 300, 600
TAMANHO_BLOCO = 30
COLUNAS, LINHAS = LARGURA // TAMANHO_BLOCO, ALTURA // TAMANHO_BLOCO

# Definição das peças (Tetrominos)
TETROMINOS = [
    [[1,1,1,1]],           # I
    [[1,1],[1,1]],         # O
    [[0,1,0],[1,1,1]],     # T
    [[1,1,0],[0,1,1]],     # S
    [[0,1,1],[1,1,0]],     # Z
    [[1,0,0],[1,1,1]],     # L
    [[0,0,1],[1,1,1]]      # J
]

CORES = [
    (0,255,255), (255,255,0), (128,0,128),
    (0,255,0), (255,0,0), (255,165,0), (0,0,255)
]