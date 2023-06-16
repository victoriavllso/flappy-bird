import pygame  # criação de jogos
from pathlib import Path  # integrar o código com os arquivos do computador
import random  # geração de numeros aleatórios (por conta dos canos)

# diretorio do arquivo atual + imgs => ../imgs/
caminho_rel = Path(__file__).parent / 'imgs' # caminho relativo a partir do arquivo atual
#########CONSTANTES###########
LARGURA = 500
ALTURA = 750
TITULO_JOGO = 'FLAPPYZINHO' 
DIR_IMAGENS = caminho_rel.resolve()
IMAGEM_INICIO = pygame.transform.scale2x(pygame.image.load(DIR_IMAGENS / 'fundoi.png'))
IMAGEM_CANO = pygame.transform.scale2x(pygame.image.load(DIR_IMAGENS /'cano.png'))
IMAGEM_CHAO = pygame.transform.scale2x(pygame.image.load(DIR_IMAGENS / 'base.png'))
IMAGEM_FUNDO = pygame.transform.scale2x(pygame.image.load(DIR_IMAGENS / 'piramide.jpg'))

pygame.display.set_caption(TITULO_JOGO)
pygame.font.init()
FONTE_PONTOS = pygame.font.SysFont('comicsansms', 50)


class Passaro:
    IMAGENS = [
        pygame.transform.scale2x(pygame.image.load(DIR_IMAGENS / 'bird1.png')),
        pygame.transform.scale2x(pygame.image.load(DIR_IMAGENS / 'bird2.png')),
        pygame.transform.scale2x(pygame.image.load(DIR_IMAGENS / 'bird3.png')),
    ]
     ##### animações das rotações:
    ROTACAO_MAXIMA = 25
    VELOCIDADE_ROTACAO = 20
    TEMPO_ANIMACAO = 5

### atributos do passaro:
    def __init__(self, x, y): #FUNÇÃO QUE CRIA O PASSARO
        self.x = x
        self.y = y #pos vertical dele
        self.angulo = 0
        self.velocidade = -10.5 # velocidade p cima e p baixo (negativo pois, no pygame, a direção para cima é negativo)
        self.altura = self.y
        self.tempo = 0  # para o movimento do passaro ser parabólico (sorvete)
        self.contagem_imagem = 0
        self.imagem = self.IMAGENS[0]
        self.congela = False


    def pular(self):  # o passaro desloca apenas no eixo y
        self.tempo = 0
        self.altura = self.y #só atualizo a altura quando ele pular


    def mover(self):
        ###calculo do deslocamento
        self.tempo += 1
        deslocamento = 1.6 * (self.tempo**2) + self.velocidade * self.tempo

        ### restrição do deslocamento para ele não acelerar infinitamente p baixou ou p cima
        if deslocamento > 16:  # deslocamento máximo será de 16px
            deslocamento = 16
        elif deslocamento < 0:
            deslocamento -= 2

        self.y += deslocamento


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
        elif self.contagem_imagem >= self.TEMPO_ANIMACAO*4 + 1:
            self.imagem = self.IMAGENS[0]
            self.contagem_imagem = 0


        # se o passaro tiver caindo eu não vou bater asa
        if self.angulo <= -80:
            self.imagem = self.IMAGENS[1]
            self.contagem_imagem = self.TEMPO_ANIMACAO*2

        # desenhar a imagem
        imagem_rotacionada = pygame.transform.rotate(self.imagem, self.angulo)
        centro_imagem = self.imagem.get_rect(topleft=(self.x, self.y)).center
        retangulo = imagem_rotacionada.get_rect(center=centro_imagem)
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
        self.CANO_TOPO = pygame.transform.flip(IMAGEM_CANO, False, True)
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

        # analogo a 'return base_ponto or topo_ponto'
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
 

class Jogo:
    def __init__(self):
        self.relogio = pygame.time.Clock() 
        self.tela = pygame.display.set_mode((LARGURA, ALTURA))
    

    def desenhar_tela(self, passaro, canos, chao, pontos):
        self.tela.blit(IMAGEM_FUNDO, (0, 0))
        passaro.desenhar(self.tela)
        for cano in canos:
            cano.desenhar(self.tela)

        texto = FONTE_PONTOS.render(f"Pontuação: {pontos}", 1, (0, 0, 0))
        self.tela.blit(texto, (LARGURA - 10 - texto.get_width(), 10))
        chao.desenhar(self.tela)
        pygame.display.update()


    def exibir_game_over(self):
        texto_game_over = FONTE_PONTOS.render(f"GAME OVER", 40, (0, 0, 0))
        texto_reiniciar = pygame.font.SysFont('comicsansms', 20).render(f"Pressione a tecla R para reiniciar", 1, (0, 0, 0))
        self.tela.blit(texto_game_over, ((LARGURA - texto_game_over.get_width()) // 2, (ALTURA - texto_game_over.get_height()) // 2))
        self.tela.blit(texto_reiniciar, ((LARGURA - texto_reiniciar.get_width()) // 2, (ALTURA - texto_reiniciar.get_height()) // 2 + 50 ))


    def exibir_menu(self):
        self.tela.blit(IMAGEM_INICIO, (0, 0))
        texto_iniciar = pygame.font.SysFont(
            'comicsansms', 
            30,
        ).render("Pressione 'enter' para iniciar ^-^", 1, (0, 0, 0))

        self.tela.blit(
            texto_iniciar, 
            (
                (LARGURA - texto_iniciar.get_width()) // 2, 
                (ALTURA - texto_iniciar.get_height()) // 2
            ),
        )
        pygame.display.update()


    def iniciar(self):

        def reiniciar_dados():
            pontos = 0
            game_over = False
            canos = [Cano(700)]
            chao = Chao(730)
            passaro = Passaro(230, 350)  # quando crio o passaro aqui, tenho que passar a pos. x e y
            rodando = True

            return (pontos, game_over, canos, chao, passaro, rodando)

        iniciado = False
        pontos, game_over, canos, chao, passaro, rodando = reiniciar_dados()
        
        while rodando:
            self.relogio.tick(30)

            ### interação com o usuário
            for evento in pygame.event.get():

                if evento.type == pygame.QUIT:
                    rodando = False
                    pygame.quit()
                    quit()

                if evento.type == pygame.KEYDOWN:

                    if evento.key == pygame.K_SPACE:
                        passaro.pular()

                    if evento.key == pygame.K_r and game_over:
                        pontos, game_over, canos, chao, passaro, rodando = reiniciar_dados()
                        iniciado = True

                    if evento.key == pygame.K_RETURN:
                        if not iniciado:
                            iniciado = True

            if not iniciado:
                self.exibir_menu()
            else:
                if game_over:
                    continue
                 #################fazer evento para o chaoor chao.colidir(passaro)
                
                ##mover as coisas do jogo
                passaro.mover()
                chao.mover()
                
                #if chao.colidir(passaro):
                    #game_over = True
                # break

                adicionar_cano = False
                canos_passados = []
                for cano in canos:

                    if cano.colidir(passaro):
                        game_over = True
                        break

                    cano.mover()

                    if not cano.passou and passaro.x > cano.x:
                        cano.passou = True
                        adicionar_cano = True
                    
                    if cano.x + cano.CANO_TOPO.get_width() < 0:
                        canos_passados.append(cano)

                if (passaro.y + passaro.imagem.get_height()) > chao.y or passaro.y < 0: #verificar se a posição do passaro está abaixo do chão (chao.y) ou acima do topo da tela (0)
                    game_over = True        

                if game_over:
                    self.exibir_game_over()
                    pygame.display.update()
                    pygame.time.delay(500)
                    continue

                if adicionar_cano:
                    pontos += 1
                    canos.append(Cano(600))
                
                for cano in canos_passados:
                    canos.remove(cano)

                self.desenhar_tela(passaro, canos, chao, pontos)


if __name__ == '__main__':
    jogo = Jogo()
    jogo.iniciar()
