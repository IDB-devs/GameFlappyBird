import pygame
import os
import random

TELA_LARGURA = 500
TELA_ALTURA = 800

IMAGEM_CANO = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'pipe.png'))) # carregando a imagem do cano e aumentando em 2x a imagem
IMAGEM_CHAO = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'base.png')))
IMAGEM_BACKGROUND = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bg.png')))
IMAGENS_PASSARO = [
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird1.png'))),
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird2.png'))),
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird3.png'))),
] 

pygame.font.init()
FONTE_PONTOS = pygame.font.SysFont('arial', 50) #pontuação


class Passaro:
    IMGS = IMAGENS_PASSARO
    # animações da rotação (parabola de animação)
    ROTACAO_MAXIMA = 25
    VELOCIDADE_ROTACAO = 20
    TEMPO_ANIMACAO = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angulo = 0 #angulo q o passaro começa
        self.velocidade = 0 
        self.altura = self.y 
        self.tempo = 0
        self.contagem_imagem = 0 # saber ql imagem utilizar no atual momento
        self.imagem = self.IMGS[0]

    def pular(self):
        self.velocidade = -10.5 # negativo pq o y para cima é negativo
        self.tempo = 0
        self.altura = self.y

    def mover(self):
        # calcular o deslocamento
        self.tempo += 1
        deslocamento = 1.5 * (self.tempo**2) + self.velocidade * self.tempo #formula S = so + vot + at²/2

        # restringir o deslocamento
        if deslocamento > 16:
            deslocamento = 16 #limitando o deslocamento a 16px 
        elif deslocamento < 0:
            deslocamento -= 2 #pular pouco qnd tiver apenas um toque na barra de espaço

        self.y += deslocamento #subir ou descer

        # o angulo de animação do passaro 
        if deslocamento < 0 or self.y < (self.altura + 50): # muda a animação do passaro para cair com delay
            if self.angulo < self.ROTACAO_MAXIMA: 
                self.angulo = self.ROTACAO_MAXIMA
        else:
            if self.angulo > -90: # angulo de queda
                self.angulo -= self.VELOCIDADE_ROTACAO

    def desenhar(self, tela): #animação do passaro
        # definir qual imagem do passaro vai usar
        self.contagem_imagem += 1

        if self.contagem_imagem < self.TEMPO_ANIMACAO:
            self.imagem = self.IMGS[0] # asa pra cima
        elif self.contagem_imagem < self.TEMPO_ANIMACAO*2:
            self.imagem = self.IMGS[1] # asa pro meio
        elif self.contagem_imagem < self.TEMPO_ANIMACAO*3:
            self.imagem = self.IMGS[2] # asa pra baixo
        elif self.contagem_imagem < self.TEMPO_ANIMACAO*4:
            self.imagem = self.IMGS[1] # asa pro meio
        elif self.contagem_imagem >= self.TEMPO_ANIMACAO*4 + 1:
            self.imagem = self.IMGS[0] # asa pra cima
            self.contagem_imagem = 0 # volta pro inicio


        # se o passaro tiver caindo eu não vou bater asa
        if self.angulo <= -80:
            self.imagem = self.IMGS[1]
            self.contagem_imagem = self.TEMPO_ANIMACAO*2

        # desenhar a imagem
        imagem_rotacionada = pygame.transform.rotate(self.imagem, self.angulo)
        pos_centro_imagem = self.imagem.get_rect(topleft=(self.x, self.y)).center
        retangulo = imagem_rotacionada.get_rect(center=pos_centro_imagem)
        tela.blit(imagem_rotacionada, retangulo.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.imagem) #pixel do passaro para avaliar colisao


class Cano:
    DISTANCIA = 230 #distancia entre os canos
    VELOCIDADE = 5

    def __init__(self, x):
        self.x = x
        self.altura = 0
        self.pos_topo = 0 # cano de cima
        self.pos_base = 0 # cano de baixo
        self.CANO_TOPO = pygame.transform.flip(IMAGEM_CANO, False, True) #imagem girada do cano
        self.CANO_BASE = IMAGEM_CANO
        self.passou = False # se o cano tiver passado
        self.definir_altura()

    def definir_altura(self): #onde ficara a abertura para passar
        self.altura = random.randrange(50, 450) # não passar desses pontos
        self.pos_topo = self.altura - self.CANO_TOPO.get_height()
        self.pos_base = self.altura + self.DISTANCIA

    def mover(self):
        self.x -= self.VELOCIDADE #movendo o cano 

    def desenhar(self, tela): # colocar os canos
        tela.blit(self.CANO_TOPO, (self.x, self.pos_topo))
        tela.blit(self.CANO_BASE, (self.x, self.pos_base))

    def colidir(self, passaro): 
        # pega as posicoes do passaro e dos canos
        passaro_mask = passaro.get_mask() 
        topo_mask = pygame.mask.from_surface(self.CANO_TOPO)
        base_mask = pygame.mask.from_surface(self.CANO_BASE)

        distancia_topo = (self.x - passaro.x, self.pos_topo - round(passaro.y))
        distancia_base = (self.x - passaro.x, self.pos_base - round(passaro.y))

        # verificando a colisao
        topo_ponto = passaro_mask.overlap(topo_mask, distancia_topo)
        base_ponto = passaro_mask.overlap(base_mask, distancia_base)

        if base_ponto or topo_ponto:
            return True
        else:
            return False


class Chao:
    VELOCIDADE = 5
    LARGURA = IMAGEM_CHAO.get_width() 
    IMAGEM = IMAGEM_CHAO

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.LARGURA # segunda imagem do chao para intercala-los na imagem da tela

    def mover(self):
        self.x1 -= self.VELOCIDADE
        self.x2 -= self.VELOCIDADE

        #intercalando entre iagem 1 do chao e imagem 2
        if self.x1 + self.LARGURA < 0:
            self.x1 = self.x2 + self.LARGURA
        if self.x2 + self.LARGURA < 0:
            self.x2 = self.x1 + self.LARGURA

    def desenhar(self, tela):
        tela.blit(self.IMAGEM, (self.x1, self.y))
        tela.blit(self.IMAGEM, (self.x2, self.y))


def desenhar_tela(tela, passaros, canos, chao, pontos):
    tela.blit(IMAGEM_BACKGROUND, (0, 0))
    for passaro in passaros:
        passaro.desenhar(tela)
    for cano in canos:
        cano.desenhar(tela)

    #pontuação do jogo
    texto = FONTE_PONTOS.render(f"Pontuação: {pontos}", 1, (255, 255, 255))
    tela.blit(texto, (TELA_LARGURA - 10 - texto.get_width(), 10)) # posicao onde irá ficar os pontos
    chao.desenhar(tela)
    pygame.display.update()


# executando o jogo
def main():
    passaros = [Passaro(230, 350)]
    chao = Chao(730)
    canos = [Cano(700)]
    tela = pygame.display.set_mode((TELA_LARGURA, TELA_ALTURA))
    pontos = 0
    relogio = pygame.time.Clock() #funcao de tempo utilizado no jogo

    rodando = True
    while rodando:
        relogio.tick(30) # quantos frames por segundo

        # interação com o usuário
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT: # se fechar a tela, sair do jogo
                rodando = False
                pygame.quit()
                quit()
            if evento.type == pygame.KEYDOWN: # se apertar espaço, pular
                if evento.key == pygame.K_SPACE:
                    for passaro in passaros:
                        passaro.pular()

        # mover as coisas
        for passaro in passaros:
            passaro.mover() 
        chao.mover()

        adicionar_cano = False
        remover_canos = []
        for cano in canos:
            for i, passaro in enumerate(passaros):
                if cano.colidir(passaro):
                    passaros.pop(i) #mata o passaro
                # se o passaro passou do cano
                if not cano.passou and passaro.x > cano.x:
                    cano.passou = True
                    adicionar_cano = True
            cano.mover()
            # se o cano sair da tela
            if cano.x + cano.CANO_TOPO.get_width() < 0:
                remover_canos.append(cano)

        if adicionar_cano:
            pontos += 1
            canos.append(Cano(600)) #criando novos canos
        for cano in remover_canos:
            canos.remove(cano)

        for i, passaro in enumerate(passaros):
            if (passaro.y + passaro.imagem.get_height()) > chao.y or passaro.y < 0:
                passaros.pop(i) #mata o passaro se ele cair ou for muito alto

        desenhar_tela(tela, passaros, canos, chao, pontos)


if __name__ == '__main__':
    main()
