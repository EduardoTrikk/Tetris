import pygame, random
from config import LARGURA, ALTURA, TAMANHO_BLOCO, COLUNAS, LINHAS, TETROMINOS, CORES

class TetrisGame:
    def __init__(self):
        pygame.init()
        self.tela = pygame.display.set_mode((LARGURA, ALTURA))
        pygame.display.set_caption("Tetris")
        self.clock = pygame.time.Clock()

        # Pontuação & Pause
        self.pontuacao = 0
        self.pausado = False

        # Música 8-bit
        try:
            pygame.mixer.init()
            pygame.mixer.music.load("assets/sounds/music.mp3")
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(-1)
        except Exception as e:
            print("Música não carregada:", e)

        # Efeitos sonoros
        try:
            self.sound_clear = pygame.mixer.Sound("assets/sounds/music.mp3")
            self.sound_gameover = pygame.mixer.Sound("assets/sounds/music.mp3")
        except Exception as e:
            print("Erro ao carregar efeitos sonoros:", e)

        # Estado inicial
        self.grid = [[0]*COLUNAS for _ in range(LINHAS)]
        self.peca = self.nova_peca()
        self.x, self.y = COLUNAS//2 - 2, 0
        self.game_over = False
        self.velocidade_base = 500
        self.velocidade = self.velocidade_base
        self.tempo_queda = pygame.time.get_ticks()

    # ---------------- FUNÇÕES DO JOGO ---------------- #
    def nova_peca(self):
        indice = random.randint(0, len(TETROMINOS)-1)
        return {"forma": [row[:] for row in TETROMINOS[indice]], "cor": CORES[indice]}

    def colide(self, forma, x, y):
        for i, linha in enumerate(forma):
            for j, valor in enumerate(linha):
                if valor:
                    if x+j < 0 or x+j >= COLUNAS or y+i >= LINHAS:
                        return True
                    if y+i >= 0 and self.grid[y+i][x+j]:
                        return True
        return False

    def fixar_peca(self):
        for i, linha in enumerate(self.peca["forma"]):
            for j, valor in enumerate(linha):
                if valor and 0 <= self.y+i < LINHAS and 0 <= self.x+j < COLUNAS:
                    self.grid[self.y+i][self.x+j] = self.peca["cor"]
        linhas_removidas = self.limpar_linhas()
        self.atualizar_pontuacao(linhas_removidas)
        self.ajustar_velocidade()

        self.peca = self.nova_peca()
        self.x, self.y = COLUNAS//2 - 2, 0
        if self.colide(self.peca["forma"], self.x, self.y):
            self.game_over = True

    def limpar_linhas(self):
        linhas_restantes = []
        removidas = 0
        for linha in self.grid:
            if any(v == 0 for v in linha):
                linhas_restantes.append(linha)
            else:
                removidas += 1

        for _ in range(removidas):
            linhas_restantes.insert(0, [0]*COLUNAS)
        self.grid = linhas_restantes

        if removidas > 0:
            try:
                self.sound_clear.play()
            except:
                pass

        return removidas

    def atualizar_pontuacao(self, removidas):
        
        if removidas == 1: self.pontuacao += 100
        elif removidas == 2: self.pontuacao += 300
        elif removidas == 3: self.pontuacao += 500
        elif removidas == 4: self.pontuacao += 800

    def ajustar_velocidade(self):
        nivel = self.pontuacao // 1000
        self.velocidade = max(120, self.velocidade_base - 40 * nivel)

    def rotacionar(self, forma):
        return [list(row) for row in zip(*forma[::-1])]

    def desenhar_grid(self):
        for y in range(LINHAS):
            for x in range(COLUNAS):
                cor = self.grid[y][x] if self.grid[y][x] else (30,30,30)
                pygame.draw.rect(self.tela, cor, (x*TAMANHO_BLOCO, y*TAMANHO_BLOCO, TAMANHO_BLOCO-1, TAMANHO_BLOCO-1))

    def desenhar_peca(self):
        for i, linha in enumerate(self.peca["forma"]):
            for j, valor in enumerate(linha):
                if valor:
                    pygame.draw.rect(
                        self.tela, self.peca["cor"],
                        ((self.x+j)*TAMANHO_BLOCO, (self.y+i)*TAMANHO_BLOCO, TAMANHO_BLOCO-1, TAMANHO_BLOCO-1)
                    )

    def desenhar_pontuacao(self):
        fonte = pygame.font.SysFont("Arial", 24)
        texto = fonte.render(f"Pontos: {self.pontuacao}", True, (255,255,255))
        self.tela.blit(texto, (10, 10))

    def desenhar_pause(self):
        fonte = pygame.font.SysFont("Arial", 48, bold=True)
        texto = fonte.render("PAUSE", True, (255, 255, 0))
        texto_rect = texto.get_rect(center=(LARGURA//2, ALTURA//2))
        self.tela.blit(texto, texto_rect)

        fonte2 = pygame.font.SysFont("Arial", 20)

        dica = fonte2.render("Pressione P para continuar", True, (200,200,200))
        dica_rect = dica.get_rect(center=(LARGURA//2, ALTURA//2 + 40))
        self.tela.blit(dica, dica_rect)

        sair = fonte2.render("Pressione ESC para sair", True, (200,200,200))
        sair_rect = sair.get_rect(center=(LARGURA//2, ALTURA//2 + 70))
        self.tela.blit(sair, sair_rect)

    # ---------------- LOOP PRINCIPAL ---------------- #
    def run(self):
        rodando = True
        gameover_tocado = False

        while rodando and not self.game_over:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    rodando = False
                elif evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_p:
                        self.pausado = not self.pausado
                    elif evento.key == pygame.K_ESCAPE:
                        rodando = False
                    elif not self.pausado and evento.key == pygame.K_SPACE:
                        nova_forma = self.rotacionar(self.peca["forma"])
                        if not self.colide(nova_forma, self.x, self.y):
                            self.peca["forma"] = nova_forma

            keys = pygame.key.get_pressed()
        # BLOCO DE PAUSE
            if self.pausado:
                self.tela.fill((0,0,0))
                self.desenhar_grid()
                self.desenhar_peca()
                self.desenhar_pontuacao()
                self.desenhar_pause()
                pygame.display.flip()
                self.clock.tick(10)
                continue

            # CONTROLES MOVIMENTO
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] and not self.colide(self.peca["forma"], self.x-1, self.y):
                self.x -= 1
            if keys[pygame.K_RIGHT] and not self.colide(self.peca["forma"], self.x+1, self.y):
                self.x += 1
            if keys[pygame.K_DOWN] and pygame.time.get_ticks() - self.tempo_queda > 50:
                if not self.colide(self.peca["forma"], self.x, self.y+1):
                    self.y += 1
                else:
                    self.fixar_peca()
                self.tempo_queda = pygame.time.get_ticks()

            # Queda automatica da peca
            if pygame.time.get_ticks() - self.tempo_queda > self.velocidade:
                if not self.colide(self.peca["forma"], self.x, self.y+1):
                    self.y += 1
                else:
                    self.fixar_peca()
                self.tempo_queda = pygame.time.get_ticks()

            # Renderização normal
            self.tela.fill((0,0,0))
            self.desenhar_grid()
            self.desenhar_peca()
            self.desenhar_pontuacao()
            pygame.display.flip()
            self.clock.tick(30)

            # Game Over
            if self.game_over:
                try:
                    if not gameover_tocado:
                        self.sound_gameover.play()
                        gameover_tocado = True
                except:
                    pass

                # Tela de Game Over
                fonte = pygame.font.SysFont("Arial", 32, bold=True)
                texto = fonte.render("GAME OVER", True, (255, 0, 0))
                texto_rect = texto.get_rect(center=(LARGURA//2, ALTURA//2 - 20))

                fonte2 = pygame.font.SysFont("Arial", 16)
                msg = fonte2.render("Pressione ENTER para reiniciar | ESC para sair", True, (255,255,255))
                msg_rect = msg.get_rect(center=(LARGURA//2, ALTURA//2 + 40))

                pygame.display.flip()
                exibindo = True
                while exibindo:
                    for evento in pygame.event.get():
                        if evento.type == pygame.QUIT:
                            exibindo = False
                        elif evento.type == pygame.KEYDOWN:
                            if evento.key == pygame.K_RETURN:
                                self.__init__()
                                self.run()
                                return
                            elif evento.key == pygame.K_ESCAPE:
                                exibindo = False
                    self.tela.fill((0,0,0))
                    self.desenhar_grid()
                    self.tela.blit(texto, texto_rect)
                    self.tela.blit(msg, msg_rect)
                    pygame.display.flip()
                    self.clock.tick(30)


        pygame.quit()