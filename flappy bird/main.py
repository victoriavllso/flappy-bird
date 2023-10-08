import pygame #criação de jogos
import os #integrar o código com os arquivos do computador
import random #geração de numeros aleatórios (por conta dos canos)

#########CONSTANTES###########

LARGURA = 500
ALTURA = 750
TITULO_JOGO = 'FLAPPYZINHO'
IMAGEM_INICIO = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'fundoi.png')))
IMAGEM_CANO = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'cano.png')))
IMAGEM_CHAO = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'base.png')))
IMAGEM_FUNDO = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'piramide.jpg')))
IMAGENS_PASSARO = [
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird1.png'))),
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird2.png'))),
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird3.png'))),
]

pygame.display.set_caption(TITULO_JOGO)
pygame.font.init()
FONTE_PONTOS = pygame.font.SysFont('comicsansms', 50)



class Passaro:
    IMAGENS = IMAGENS_PASSARO #usando como cte dentro da variavel
     ##### animações das rotações:
    ROTACAO_MAXIMA = 15 #angulo max. do passaro
    VELOCIDADE_ROTACAO = 20
    TEMPO_ANIMACAO = 5
### atributos do passaro:
    def __init__(self, x, y): #FUNÇÃO QUE CRIA O PASSARO
        self.x = x
        self.y = y #pos vertical dele
        self.angulo = 0
        self.velocidade = 0 #velocidade p cima e p baixo
        self.altura = self.y
        self.tempo = 0 #para o movimento do passaro ser parabólico (sorvete), criar a animação
        self.contagem_imagem = 0
        self.imagem = self.IMAGENS[0]

    def pular(self): #o passaro desloca apenas no eixo y
        self.velocidade = -10.5 #negativo, pois no pygame, a direção para cima é negativo
        self.tempo = 0 
        self.altura = self.y #só tualizo a altura quando ele pular

    def mover(self):
        ###calculo do deslocamento
        self.tempo += 1
        deslocamento = 1.6 * (self.tempo**2) + self.velocidade * self.tempo

        ### restrição do deslocamento para ele não acelerar infinitamente p baixou ou p cima
        if deslocamento > 16: #deslocamento máximo será de 16px
            deslocamento = 16
        self.y += deslocamento #pego a posição em y e somo com o deslocamento (de fato desloco ele)

        if deslocamento <0 or self.y < (self.altura + 50): #se estiver deslocando p cima ou se a posição y estiver abaixo da altura (que só é atualizada quando ele pula)
            if self.angulo < self.ROTACAO_MAXIMA: #se ele não estiver virado p cima
                self.angulo = self.ROTACAO_MAXIMA #deixo ele virado p cima
            


    def desenhar(self, tela):
        # definir qual imagem do passaro vai usar
        self.contagem_imagem += 1

        if self.contagem_imagem < self.TEMPO_ANIMACAO: #asa p cima
            self.imagem = self.IMAGENS[0]
        elif self.contagem_imagem < self.TEMPO_ANIMACAO*2: #menor que 10
            self.imagem = self.IMAGENS[1]
        elif self.contagem_imagem < self.TEMPO_ANIMACAO*3: #menor que 15
            self.imagem = self.IMAGENS[2]
        elif self.contagem_imagem < self.TEMPO_ANIMACAO*4:
            self.imagem = self.IMAGENS[1]
        elif self.contagem_imagem >= self.TEMPO_ANIMACAO*4 + 1 :
            self.imagem = self.IMAGENS[0]
            self.contagem_imagem = 0


        # se o passaro tiver caindo eu não vou bater asa
        if self.angulo <= -80:
            self.imagem = self.IMAGENS[1]
            self.contagem_imagem = self.TEMPO_ANIMACAO*2

        # desenhar a imagem (código padrão)
        imagem_rotacionada = pygame.transform.rotate(self.imagem, self.angulo)
        centro_imagem = self.imagem.get_rect(topleft=(self.x, self.y)).center
        retangulo = imagem_rotacionada.get_rect(center=centro_imagem) #pega a imagem e desenha um retangulo na rela, dps pega o retangulo e coloca na tela
        tela.blit(imagem_rotacionada, retangulo.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.imagem) #avaliando a colisão com a função mask.from_surface (analisa os pixels de forma precisa ao invés de pegar um retangulo)


class Cano:
    DISTANCIA = 220 #distancia entre o cano de cima e o de baixp
    VELOCIDADE = 5

    def __init__(self, x):
        self.x = x
        self.altura = 0
        self.pos_cano_cima = 0
        self.pos_cano_baixo = 0
        self.CANO_TOPO = pygame.transform.flip(IMAGEM_CANO, False, True) #é a imagem do cano invertida (flipada), no eixo y (true)
        self.CANO_BASE = IMAGEM_CANO
        self.passou = False
        self.definir_altura()

    def definir_altura(self):
        self.altura = random.randrange(50, 450)
        self.pos_cano_cima = self.altura - self.CANO_TOPO.get_height()
        self.pos_cano_baixo = self.altura + self.DISTANCIA

    def mover(self):
        self.x -= self.VELOCIDADE

    def desenhar(self, tela):
        tela.blit(self.CANO_TOPO, (self.x, self.pos_cano_cima))
        tela.blit(self.CANO_BASE, (self.x, self.pos_cano_baixo))

    def colidir(self, passaro):
        passaro_mask = passaro.get_mask()
        topo_mask = pygame.mask.from_surface(self.CANO_TOPO)
        base_mask = pygame.mask.from_surface(self.CANO_BASE)
        

        distancia_topo = (self.x - passaro.x, self.pos_cano_cima - round(passaro.y))
        distancia_base = (self.x - passaro.x, self.pos_cano_baixo - round(passaro.y))
        

        topo_ponto = passaro_mask.overlap(topo_mask, distancia_topo)
        base_ponto = passaro_mask.overlap(base_mask, distancia_base)


        if base_ponto or topo_ponto: #se ele colidir
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
        self.x2 = self.LARGURA #seria self.x1 +self.largura, mas x1 = 0

    def mover(self):
        self.x1 -= self.VELOCIDADE
        self.x2 -= self.VELOCIDADE

        if self.x1 + self.LARGURA < 0: #se o chão saiu da tela, adiciono de novo
            self.x1 = self.x2 + self.LARGURA
        if self.x2 + self.LARGURA < 0:
            self.x2 = self.x1 + self.LARGURA

    def desenhar(self, tela):
        tela.blit(self.IMAGEM, (self.x1, self.y))
        tela.blit(self.IMAGEM, (self.x2, self.y))
 


########################criando o jogo#####################
def desenhar_tela(tela, passaros, canos, chao, pontos):
    tela.blit(IMAGEM_FUNDO, (0, 0))
    for passaro in passaros:
        passaro.desenhar(tela)
    for cano in canos:
        cano.desenhar(tela)

    texto = FONTE_PONTOS.render(f"Pontuação: {pontos}", 1, (0, 0, 0))
    tela.blit(texto, (LARGURA - 10 - texto.get_width(), 10))
    chao.desenhar(tela)
    pygame.display.update()

def exibir_game_over(tela):
    texto_game_over = FONTE_PONTOS.render(f"GAME OVER", 40, (0, 0, 0))
    texto_reiniciar = pygame.font.SysFont('comicsansms', 20).render(f"Pressione a tecla R para reiniciar", 1, (0, 0, 0))
    tela.blit(texto_game_over, ((LARGURA - texto_game_over.get_width()) // 2, (ALTURA - texto_game_over.get_height()) // 2))
    tela.blit(texto_reiniciar, ((LARGURA - texto_reiniciar.get_width()) // 2, (ALTURA - texto_reiniciar.get_height()) // 2 + 50 ))


    


def main():
    iniciado = False
    passaros = [Passaro(230, 350)] #quando crio o passaro aqui, tenho que passar a pos. x e y
    chao = Chao(730)
    canos = [Cano(700)]
    tela = pygame.display.set_mode((LARGURA, ALTURA))
    pontos = 0
    relogio = pygame.time.Clock() 
    rodando = True
    game_over = False

    def reiniciar_jogo():
        nonlocal pontos, game_over, canos, chao, passaros, rodando
        pontos = 0
        game_over = False
        canos = [Cano(700)]
        chao = Chao(730)
        passaros = [Passaro(230, 350)]
        rodando = True

    while rodando:
        relogio.tick(30)

        ### interação com o usuário
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
                pygame.quit()
                quit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_SPACE:
                    for passaro in passaros:
                        passaro.pular()

                if evento.key == pygame.K_r and game_over:
                    reiniciar_jogo()

                if evento.key == pygame.K_RETURN: #tecla enter
                    if not iniciado:
                        iniciado = True
                        reiniciar_jogo()
                        
        if not iniciado:  # Verifica se o jogo não foi iniciado
            tela.blit(IMAGEM_INICIO, (0, 0))
            texto_iniciar = pygame.font.SysFont('comicsansms', 30).render("Pressione 'enter' para iniciar ^-^", 1, (0, 0, 0))
            tela.blit(texto_iniciar, ((LARGURA - texto_iniciar.get_width()) // 2, (ALTURA - texto_iniciar.get_height()) // 2))
            pygame.display.update()
            continue


        ##mover as coisas do jogo
        for passaro in passaros:
            passaro.mover()
        chao.mover()
        adicionar_cano = False
        remover_canos = []
        for cano in canos:
            for i, passaro in enumerate(passaros):
                if cano.colidir(passaro):
                    passaros.pop(i)
                    game_over = True
                    break
            cano.mover()
            if not cano.passou and passaro.x > cano.x:
                cano.passou = True
                adicionar_cano = True
            
            if cano.x + cano.CANO_TOPO.get_width() < 0:
                remover_canos.append(cano)

        for i, passaro in enumerate(passaros):
            if (passaro.y + passaro.imagem.get_height()) > chao.y or passaro.y < 0: #verificar se a posição do passaro está abaixo do chão (chao.y) ou acima do topo da tela (0)
                passaros.pop(i)
                game_over = True        



        if adicionar_cano:
            pontos += 1
            canos.append(Cano(600))
        
        for cano in remover_canos:
            canos.remove(cano)
        if game_over:
            exibir_game_over(tela)
            pygame.display.update( )
            continue


        desenhar_tela(tela, passaros, canos, chao, pontos)

    

main()

