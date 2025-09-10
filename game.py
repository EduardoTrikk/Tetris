import pygame, random
from config import LARGURA, ALTURA, TAMANHO_BLOCO, COLUNAS, LINHAS, TETROMINOS, CORES

class TetrisGame:
    def __init__(self):
        pygame.init()
        self.tela = pygame.display.set_mode((LARGURA, ALTURA))
        pygame.display.set_caption("Tetris")
        self.clock = pygame.time.Clock()

        # Pontuacao e Pause
        self.pontuacao = 0
        self.pausado = False

        # Musica 8-bit
        try:
            pygame.mixer.init()
            pygame.mixer.music.load("assets/sounds/music.mp3")
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(-1)
        except Exception as e:
            print("Música não carregada:", e)

        # Efeitos sonoros (carregar separadamente)
        try:
            self.sound_clear = pygame.mixer.Sound("assets/sounds/point.mp3")
        except Exception as e:
            print("Erro ao carregar som de clear:", e)
            self.sound_clear = None
        try:
            self.sound_gameover = pygame.mixer.Sound("assets/sounds/lose.mp3")
        except Exception as e:
            print("Erro ao carregar som de gameover:", e)
            self.sound_gameover = None

        # Criar canais fixos (nao recriar a cada som)
        try:
            self.channel_clear = pygame.mixer.Channel(1)
            self.channel_gameover = pygame.mixer.Channel(2)
        except Exception:
            self.channel_clear = None
            self.channel_gameover = None

        # Estado inicial
        self.grid = [[0]*COLUNAS for _ in range(LINHAS)]
        self.peca = self.nova_peca()
        self.x, self.y = COLUNAS//2 - 2, 0
        self.game_over = False
        self.velocidade_base = 500
        self.velocidade = self.velocidade_base
        self.tempo_queda = pygame.time.get_ticks()

        # Controle de repeticao das setas (sensibilidade)
        self.tempo_move = 0          # ultimo movimento em ms
        self.delay_move = 150        # delay entre movimentos em ms

    # ---------------- FUNCOES DO JOGO ---------------- #
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

        # tocar som (usa canal pre-criado)
        if removidas > 0 and self.sound_clear is not None:
            try:
                if self.channel_clear:
                    self.channel_clear.play(self.sound_clear)
                else:
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
        # Titulo
        fonte = pygame.font.SysFont("Arial", 48, bold=True)
        texto = fonte.render("PAUSE", True, (255, 255, 0))
        texto_rect = texto.get_rect(center=(LARGURA//2, ALTURA//2 - 40))
        self.tela.blit(texto, texto_rect)

        # Linhas de instrucao separadas
        fonte2 = pygame.font.SysFont("Arial", 20)
        lines = ["P: continuar", "ENTER: reiniciar", "ESC: sair"]

        # Ajuste de espaçamento entre linhas (em pixels)
        line_spacing = 28
        start_y = ALTURA//2 + 10  # y da primeira linha

        for i, linha in enumerate(lines):
            surf = fonte2.render(linha, True, (200,200,200))
            rect = surf.get_rect(center=(LARGURA//2, start_y + i * line_spacing))
            self.tela.blit(surf, rect)

    # ---------------- LOOP PRINCIPAL ---------------- #
    def run(self):
        rodando = True

        while rodando:
            now = pygame.time.get_ticks()

            # ---- eventos ----
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    rodando = False
                elif evento.type == pygame.KEYDOWN:
                    # Toggle pause
                    if evento.key == pygame.K_p:
                        self.pausado = not self.pausado
                        # ao despausar, resetar o timer de queda para evitar queda imediata
                        if not self.pausado:
                            self.tempo_queda = pygame.time.get_ticks()
                    # sair do jogo (sempre)
                    elif evento.key == pygame.K_ESCAPE:
                        rodando = False
                    # reiniciar direto do pause com ENTER
                    elif evento.key == pygame.K_RETURN and self.pausado:
                        self.__init__()  # reinicia o estado do jogo
                        # continuar loop com novo estado
                    # rotacao (apenas quando nao pausado e nao terminou)
                    elif evento.key == pygame.K_SPACE and not self.pausado and not self.game_over:
                        nova_forma = self.rotacionar(self.peca["forma"])
                        if not self.colide(nova_forma, self.x, self.y):
                            self.peca["forma"] = nova_forma

            # Se game over foi acionado, sair do loop principal para mostrar a tela de game over
            if self.game_over:
                break

            # ---- Se pausado, desenhar menu de pausa e pular logica ----
            if self.pausado:
                self.tela.fill((0,0,0))
                self.desenhar_grid()
                self.desenhar_peca()
                self.desenhar_pontuacao()
                self.desenhar_pause()
                pygame.display.flip()
                self.clock.tick(10)
                continue

            # ---- logica de movimento continuo (com sensibilidade) ----
            keys = pygame.key.get_pressed()

            # esquerda/direita com delay
            if keys[pygame.K_LEFT] and now - self.tempo_move > self.delay_move and not self.colide(self.peca["forma"], self.x-1, self.y):
                self.x -= 1
                self.tempo_move = now
            if keys[pygame.K_RIGHT] and now - self.tempo_move > self.delay_move and not self.colide(self.peca["forma"], self.x+1, self.y):
                self.x += 1
                self.tempo_move = now

            # queda acelerada enquanto segura ↓ (usar delay menor)
            if keys[pygame.K_DOWN] and now - self.tempo_move > 50:
                if not self.colide(self.peca["forma"], self.x, self.y+1):
                    self.y += 1
                else:
                    self.fixar_peca()
                self.tempo_move = now

            # queda automatica
            if now - self.tempo_queda > self.velocidade:
                if not self.colide(self.peca["forma"], self.x, self.y+1):
                    self.y += 1
                else:
                    self.fixar_peca()
                self.tempo_queda = now

            # ---- renderizacao ----
            self.tela.fill((0,0,0))
            self.desenhar_grid()
            self.desenhar_peca()
            self.desenhar_pontuacao()
            pygame.display.flip()
            self.clock.tick(30)

        # ---- SHOW GAME OVER (aparece imediatamente quando self.game_over=True) ----
        if self.game_over:
            # tocar game over apenas uma vez
            try:
                if self.channel_gameover and self.sound_gameover:
                    self.channel_gameover.play(self.sound_gameover)
                elif self.sound_gameover:
                    self.sound_gameover.play()
            except:
                pass

            # preparar textos/overlay
            fonte = pygame.font.SysFont("Arial", 48, bold=True)
            texto = fonte.render("GAME OVER", True, (255, 0, 0))
            texto_rect = texto.get_rect(center=(LARGURA//2, ALTURA//2 - 60))

            fonte2 = pygame.font.SysFont("Arial", 26, bold=True)
            score_text = fonte2.render(f"Pontuação: {self.pontuacao}", True, (255, 255, 255))
            score_rect = score_text.get_rect(center=(LARGURA//2, ALTURA//2 - 10))

            instr = pygame.font.SysFont("Arial", 20)
            msg = instr.render("ENTER: Reiniciar", True, (200,200,200))
            msg_rect = msg.get_rect(center=(LARGURA//2, ALTURA//2 + 30))
            msg2 = instr.render("ESC: Sair", True, (200,200,200))
            msg2_rect = msg2.get_rect(center=(LARGURA//2, ALTURA//2 + 60))

            exibindo = True
            while exibindo:
                for evento in pygame.event.get():
                    if evento.type == pygame.QUIT:
                        exibindo = False
                    elif evento.type == pygame.KEYDOWN:
                        if evento.key == pygame.K_RETURN:
                            # reiniciar jogo
                            self.__init__()
                            self.run()
                            return
                        elif evento.key == pygame.K_ESCAPE:
                            exibindo = False

                # desenhar grid original por baixo, overlay e textos (aparece sem precisar apertar nada)
                self.tela.fill((0,0,0))
                self.desenhar_grid()

                overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 180))
                self.tela.blit(overlay, (0,0))

                self.tela.blit(texto, texto_rect)
                self.tela.blit(score_text, score_rect)
                self.tela.blit(msg, msg_rect)
                self.tela.blit(msg2, msg2_rect)

                pygame.display.flip()
                self.clock.tick(30)

        pygame.quit()