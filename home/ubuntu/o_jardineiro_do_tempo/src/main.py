import pygame
import sys
import random

# --- Configurações Globais ---
TITULO = "O Jardineiro do Tempo"
LARGURA_TELA = 640
ALTURA_TELA = 480
FPS = 60
COR_FUNDO = (20, 20, 30) # Cor de fundo escura

# Configurações da Grade
TAMANHO_CELULA = 30
GRID_LARGURA = 16
GRID_ALTURA = 16
MARGEM_X = (LARGURA_TELA - GRID_LARGURA * TAMANHO_CELULA) // 2
MARGEM_Y = (ALTURA_TELA - GRID_ALTURA * TAMANHO_CELULA) // 2

# Cores
COR_SOLO = (100, 60, 40)
COR_SEMENTE = (150, 150, 0)
COR_CRESCENDO = (0, 180, 0)
COR_MADURO = (255, 0, 255) # Flor roxa
COR_MURCHO = (50, 50, 50)
COR_ERVA_DANINHA = (100, 100, 0)
COR_PRAGA = (255, 0, 0) # Vermelho para a praga

# --- Inicialização do Pygame ---
pygame.init()
TELA = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
pygame.display.set_caption(TITULO)
RELOGIO = pygame.time.Clock()

# --- Fontes ---
try:
    FONTE_PEQUENA = pygame.font.Font(None, 24)
    FONTE_MEDIA = pygame.font.Font(None, 36)
except pygame.error:
    print("Aviso: Não foi possível carregar a fonte padrão. Usando fallback.")
    FONTE_PEQUENA = pygame.font.SysFont(None, 24)
    FONTE_MEDIA = pygame.font.SysFont(None, 36)

# --- Classes do Jogo ---

class Tile:
    """Representa uma célula do jardim."""
    def __init__(self, x, y):
        self.grid_x = x
        self.grid_y = y
        self.rect = pygame.Rect(
            MARGEM_X + x * TAMANHO_CELULA,
            MARGEM_Y + y * TAMANHO_CELULA,
            TAMANHO_CELULA,
            TAMANHO_CELULA
        )
        self.estado = "vazio" # "vazio", "semente", "crescendo", "maduro", "murcho"
        self.tem_erva_daninha = False
        self.tempo_crescimento = 0 # Contador para o crescimento
        self.tempo_max_crescimento = 100 # Tempo (em ticks) para atingir a maturidade
        self.tempo_murchar = 150 # Tempo (em ticks) para murchar após a maturidade
        self.contador_erva_daninha = 0
        self.limite_erva_daninha = 300 # Tempo para a erva daninha aparecer e se espalhar

    def aplicar_efeito_tempo(self, fator):
        """
        Aplica o efeito de manipulação temporal.
        fator > 1: Acelerar (crescimento mais rápido)
        fator < 1: Reverter (crescimento mais lento/reversão)
        """
        if self.estado == "semente" or self.estado == "crescendo":
            self.tempo_crescimento += fator * 5 # Acelera/reverte o contador
            if self.tempo_crescimento >= self.tempo_max_crescimento:
                self.estado = "maduro"
                self.tempo_crescimento = self.tempo_max_crescimento
            elif self.tempo_crescimento < 0:
                self.estado = "vazio"
                self.tempo_crescimento = 0
        
        elif self.estado == "maduro":
            self.tempo_crescimento += fator * 5
            if self.tempo_crescimento > self.tempo_murchar:
                self.estado = "murcho"
            elif self.tempo_crescimento < self.tempo_max_crescimento:
                self.estado = "crescendo" # Reverte de maduro para crescendo

        # Efeito nas ervas daninhas
        if self.tem_erva_daninha:
            if fator > 0: # Acelerar: mata a erva daninha
                self.tem_erva_daninha = False
                self.contador_erva_daninha = 0
            elif fator < 0: # Reverter: faz a erva daninha regredir
                self.contador_erva_daninha -= fator * 5
                if self.contador_erva_daninha < 0:
                    self.tem_erva_daninha = False
                    self.contador_erva_daninha = 0

    def update(self):
        """Atualização natural do tempo (crescimento e murchamento)."""
        if self.estado == "semente" or self.estado == "crescendo":
            self.tempo_crescimento += 1
            if self.tempo_crescimento >= self.tempo_max_crescimento:
                self.estado = "maduro"
                self.tempo_crescimento = self.tempo_max_crescimento
        
        elif self.estado == "maduro":
            self.tempo_crescimento += 1
            if self.tempo_crescimento > self.tempo_murchar:
                self.estado = "murcho"
        
        # Lógica de crescimento de ervas daninhas
        if self.estado != "vazio" and not self.tem_erva_daninha:
            self.contador_erva_daninha += 1
            if self.contador_erva_daninha > self.limite_erva_daninha:
                self.tem_erva_daninha = True
                self.contador_erva_daninha = 0 # Reset para espalhar

    def desenhar(self, superficie):
        # Desenha o solo
        pygame.draw.rect(superficie, COR_SOLO, self.rect, 1)

        # Desenha o estado da planta
        cor_planta = None
        if self.estado == "semente":
            cor_planta = COR_SEMENTE
        elif self.estado == "crescendo":
            cor_planta = COR_CRESCENDO
        elif self.estado == "maduro":
            cor_planta = COR_MADURO
        elif self.estado == "murcho":
            cor_planta = COR_MURCHO
        
        if cor_planta:
            # O tamanho do círculo representa o estágio de crescimento
            raio = int(TAMANHO_CELULA * (self.tempo_crescimento / self.tempo_murchar) / 2)
            pygame.draw.circle(superficie, cor_planta, self.rect.center, raio)
        
        # Desenha a erva daninha
        if self.tem_erva_daninha:
            pygame.draw.rect(superficie, COR_ERVA_DANINHA, self.rect, 2) # Borda amarela/verde ao redor da célula

class Jardineiro(pygame.sprite.Sprite):
    """Representa o jogador, o Jardineiro do Tempo."""
    def __init__(self):
        super().__init__()
        self.tamanho = 30
        self.image = pygame.Surface([self.tamanho, self.tamanho])
        self.image.fill((0, 150, 0)) # Verde para o jardineiro
        self.rect = self.image.get_rect()
        self.rect.center = (LARGURA_TELA // 2, ALTURA_TELA // 2)
        self.velocidade = 3
        self.energia_temporal = 100 # Recurso para usar a ferramenta
        self.max_energia = 100

    def update(self):
        """Processa a entrada do teclado para movimento e regenera energia."""
        keys = pygame.key.get_pressed()
        movendo = False
        
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= self.velocidade
            movendo = True
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += self.velocidade
            movendo = True
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.rect.y -= self.velocidade
            movendo = True
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.rect.y += self.velocidade
            movendo = True

        # Regeneração de energia quando não está se movendo
        if not movendo and self.energia_temporal < self.max_energia:
            self.energia_temporal += 0.5
        
        # Mantém o jardineiro dentro dos limites da tela
        self.rect.clamp_ip(TELA.get_rect())

    def get_grid_pos(self):
        """Retorna a posição do jardineiro na grade."""
        grid_x = (self.rect.centerx - MARGEM_X) // TAMANHO_CELULA
        grid_y = (self.rect.centery - MARGEM_Y) // TAMANHO_CELULA
        return grid_x, grid_y

    def tentar_plantar(self, grid):
        """Tenta plantar uma semente na célula atual."""
        gx, gy = self.get_grid_pos()
        if 0 <= gx < GRID_LARGURA and 0 <= gy < GRID_ALTURA:
            tile = grid[gy][gx]
            if tile.estado == "vazio":
                tile.estado = "semente"
                tile.tempo_crescimento = 1
                return True
        return False

    def tentar_remover_erva_daninha(self, grid):
        """Tenta remover a erva daninha na célula atual."""
        gx, gy = self.get_grid_pos()
        if 0 <= gx < GRID_LARGURA and 0 <= gy < GRID_ALTURA:
            tile = grid[gy][gx]
            if tile.tem_erva_daninha:
                tile.tem_erva_daninha = False
                tile.contador_erva_daninha = 0
                return True
        return False

    def tentar_colher(self, grid, jogo):
        """Tenta colher uma planta madura na célula atual."""
        gx, gy = self.get_grid_pos()
        if 0 <= gx < GRID_LARGURA and 0 <= gy < GRID_ALTURA:
            tile = grid[gy][gx]
            if tile.estado == "maduro":
                tile.estado = "vazio"
                tile.tempo_crescimento = 0
                jogo.pontuacao += 10 # Ganha 10 pontos por colheita
                jogo.medidor_beleza = min(jogo.max_beleza, jogo.medidor_beleza + 5) # Aumenta a beleza
                return True
        return False

class Praga(pygame.sprite.Sprite):
    """Representa uma praga que se move e come plantas."""
    def __init__(self, grid_x, grid_y):
        super().__init__()
        self.tamanho = 15
        self.image = pygame.Surface([self.tamanho, self.tamanho])
        self.image.fill(COR_PRAGA)
        self.rect = self.image.get_rect()
        self.grid_x = grid_x
        self.grid_y = grid_y
        self._atualizar_posicao_tela()
        self.tempo_vida = 100 # Tempo de vida da praga (em ticks)
        self.velocidade_movimento = 60 # Move a cada 60 ticks

    def _atualizar_posicao_tela(self):
        """Calcula a posição na tela a partir da posição na grade."""
        tile_x = MARGEM_X + self.grid_x * TAMANHO_CELULA
        tile_y = MARGEM_Y + self.grid_y * TAMANHO_CELULA
        self.rect.center = (tile_x + TAMANHO_CELULA // 2, tile_y + TAMANHO_CELULA // 2)

    def aplicar_efeito_tempo(self, fator):
        """Acelerar mata, reverter rejuvenesce/move para trás."""
        self.tempo_vida -= fator * 5 # Acelerar diminui, reverter aumenta
        if self.tempo_vida <= 0:
            self.kill() # Morre de velhice
        elif self.tempo_vida > 200:
            self.tempo_vida = 200 # Limite de vida

    def update(self, grid, jogo):
        """Atualização natural (movimento e alimentação)."""
        self.tempo_vida -= 1
        if self.tempo_vida <= 0:
            self.kill()
            return

        # Pragas diminuem a beleza
        jogo.medidor_beleza = max(0, jogo.medidor_beleza - 0.01)

        # Movimento lento
        if pygame.time.get_ticks() % self.velocidade_movimento == 0:
            direcoes = [(0, 1), (0, -1), (1, 0), (-1, 0)]
            dx, dy = random.choice(direcoes)
            
            novo_gx = self.grid_x + dx
            novo_gy = self.grid_y + dy

            if 0 <= novo_gx < GRID_LARGURA and 0 <= novo_gy < GRID_ALTURA:
                self.grid_x = novo_gx
                self.grid_y = novo_gy
                self._atualizar_posicao_tela()
                
                # Alimentação: come a planta
                tile = grid[self.grid_y][self.grid_x]
                if tile.estado != "vazio":
                    tile.estado = "vazio"
                    tile.tempo_crescimento = 0
                    print("Praga comeu a planta!")

class Jogo:
    """Classe principal para gerenciar o loop do jogo."""
    def __init__(self):
        self.rodando = True
        self.todos_sprites = pygame.sprite.Group()
        self.pragas = pygame.sprite.Group()
        self.jardineiro = Jardineiro()
        self.todos_sprites.add(self.jardineiro)
        self.grid = self._inicializar_grid()
        self.custo_temporal = 5 # Custo de energia por uso da ferramenta
        self.contador_praga = 0
        self.limite_praga = 500 # Tempo para uma nova praga aparecer
        self.medidor_beleza = 50.0 # Começa com 50/100 (float para precisão)
        self.max_beleza = 100.0
        self.pontuacao = 0 # Pontuação total (colheitas)

    def _inicializar_grid(self):
        """Cria a matriz de objetos Tile."""
        grid = []
        for y in range(GRID_ALTURA):
            linha = []
            for x in range(GRID_LARGURA):
                linha.append(Tile(x, y))
            grid.append(linha)
        return grid

    def _aplicar_efeito_temporal(self, fator):
        """Aplica o efeito temporal em uma área 3x3 ao redor do jardineiro."""
        if self.jardineiro.energia_temporal >= self.custo_temporal:
            self.jardineiro.energia_temporal -= self.custo_temporal
            
            gx, gy = self.jardineiro.get_grid_pos()
            
            # Itera sobre a área 3x3
            for y in range(gy - 1, gy + 2):
                for x in range(gx - 1, gx + 2):
                    if 0 <= x < GRID_LARGURA and 0 <= y < GRID_ALTURA:
                        self.grid[y][x].aplicar_efeito_tempo(fator)
            return True
        return False

    def processar_eventos(self):
        """Processa todos os eventos do Pygame (fechar janela, teclado, etc.)."""
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                self.rodando = False
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    self.rodando = False
                
                # Interação (Plantar/Colher)
                if evento.key == pygame.K_e:
                    if self.jardineiro.tentar_colher(self.grid, self):
                        print("Colheita!")
                    elif self.jardineiro.tentar_remover_erva_daninha(self.grid):
                        print("Erva Daninha Removida!")
                    elif self.jardineiro.tentar_plantar(self.grid):
                        print("Plantio!")

                # Acelerar Tempo (K_z)
                if evento.key == pygame.K_z:
                    if self._aplicar_efeito_temporal(10): # Fator de aceleração alto
                        print("Tempo Acelerado!")
                
                # Reverter Tempo (K_x)
                if evento.key == pygame.K_x:
                    if self._aplicar_efeito_temporal(-10): # Fator de reversão alto
                        print("Tempo Revertido!")

    def atualizar(self):
        """Atualiza o estado de todos os objetos do jogo."""
        self.todos_sprites.update()
        self.pragas.update(self.grid, self) # Passa a grade e o objeto Jogo para a praga interagir
        
        # Atualiza a grade (tempo natural)
        for linha in self.grid:
            for tile in linha:
                tile.update()
                # Lógica de perda/ganho de beleza por tile
                if tile.estado == "murcho" or tile.tem_erva_daninha:
                    self.medidor_beleza = max(0, self.medidor_beleza - 0.005)
                elif tile.estado == "maduro":
                    self.medidor_beleza = min(self.max_beleza, self.medidor_beleza + 0.001)
        
        # Lógica de surgimento de pragas
        self.contador_praga += 1
        if self.contador_praga > self.limite_praga:
            self.contador_praga = 0
            # Tenta criar uma praga em uma célula aleatória
            gx = random.randint(0, GRID_LARGURA - 1)
            gy = random.randint(0, GRID_ALTURA - 1)
            nova_praga = Praga(gx, gy)
            self.pragas.add(nova_praga)
            # Não adicionamos ao todos_sprites para evitar o erro de argumento no update()
            print("Nova Praga apareceu!")

    def desenhar(self):
        """Desenha todos os elementos na tela."""
        TELA.fill(COR_FUNDO)
        
        # 1. Desenha a área de efeito temporal (3x3 ao redor do jardineiro)
        gx, gy = self.jardineiro.get_grid_pos()
        for y in range(gy - 1, gy + 2):
            for x in range(gx - 1, gx + 2):
                if 0 <= x < GRID_LARGURA and 0 <= y < GRID_ALTURA:
                    tile_rect = self.grid[y][x].rect
                    # Desenha um contorno suave para indicar a área de efeito
                    pygame.draw.rect(TELA, (255, 255, 255), tile_rect, 2) # Sem alpha, Pygame não suporta alpha em draw.rect simples

        # 2. Desenha a grade
        for linha in self.grid:
            for tile in linha:
                tile.desenhar(TELA)

        # 3. Desenha o jardineiro e as pragas
        self.todos_sprites.draw(TELA) # Desenha o Jardineiro
        self.pragas.draw(TELA) # Desenha as Pragas

        # 4. Desenha a UI
        # Energia Temporal
        energia_texto = FONTE_PEQUENA.render(f"Energia: {int(self.jardineiro.energia_temporal)}/{int(self.jardineiro.max_energia)}", True, (255, 255, 255))
        TELA.blit(energia_texto, (10, 10))
        
        # Medidor de Beleza
        beleza_texto = FONTE_PEQUENA.render(f"Beleza: {int(self.medidor_beleza)}%", True, (255, 255, 255))
        TELA.blit(beleza_texto, (LARGURA_TELA - 150, 10))
        
        # Barra de Beleza (Visual)
        pygame.draw.rect(TELA, (100, 100, 100), (LARGURA_TELA - 150, 35, 140, 10))
        largura_beleza = int(140 * (self.medidor_beleza / self.max_beleza))
        pygame.draw.rect(TELA, (0, 255, 0), (LARGURA_TELA - 150, 35, largura_beleza, 10))

        # Pontuação
        pontuacao_texto = FONTE_PEQUENA.render(f"Pontos: {self.pontuacao}", True, (255, 255, 255))
        TELA.blit(pontuacao_texto, (10, 40))

        # Instruções
        instrucoes_texto = FONTE_PEQUENA.render("Mover: WASD | Interagir: E | Acelerar: Z | Reverter: X", True, (200, 200, 200))
        TELA.blit(instrucoes_texto, (LARGURA_TELA // 2 - instrucoes_texto.get_width() // 2, ALTURA_TELA - 30))
        
        pygame.display.flip()

    def rodar(self):
        """O loop principal do jogo."""
        while self.rodando:
            self.processar_eventos()
            self.atualizar()
            self.desenhar()
            RELOGIO.tick(FPS)

        pygame.quit()
        sys.exit()

# --- Execução do Jogo ---
if __name__ == "__main__":
    jogo = Jogo()
    jogo.rodar()
