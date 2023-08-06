'''
Jogo Flappy Bird em Python
Utilizando a biblioteca: PyGame

Criado por: Carlos Alberto Morais Moura Filho
Versão: 1.0
Atualizado em: 11/06/2021
'''
# pylint: disable=no-member
# pylint: disable=too-many-locals
# pylint: disable=too-many-branches
# pylint: disable=too-many-statements
# pylint: disable=c-extension-no-member
# pylint: disable=no-name-in-module

# Bibliotecas
from os import path, environ, getcwd, chdir
from random import randint, choice
from sys import platform as plat, exit as ext, path as syspath
import pickle
import pygame, sys
from pygame.constants import QUIT, KEYDOWN, K_ESCAPE, K_SPACE
# Constantes
BASE_DIR = path.dirname(__file__)    # Diretorio do jogo
SOUNDS_PATH = path.normpath(path.join(BASE_DIR, 'res/sounds'))
ICON_PATH = path.normpath(path.join(BASE_DIR, 'res/assets/icons'))
BIRDS_PATH = path.normpath(path.join(BASE_DIR, 'res/assets/birds'))
PIPES_PATH = path.normpath(path.join(BASE_DIR, 'res/assets/pipes'))
SCENERY_PATH = path.normpath(path.join(BASE_DIR, 'res/assets/sceneries'))
NUMS_PATH = path.normpath(path.join(BASE_DIR, 'res/assets/numbers'))
MSGS_PATH = path.normpath(path.join(BASE_DIR, 'res/assets//messages'))
SCREEN_WIDTH = 400                   # Comprimento da tela
SCREEN_HEIGHT = 800                  # Altura da tela
RED = (255, 0, 0)                    # Cor vermelha, para a linha de pontuação
GRAVITY = 1                          # Gravidade
GAME_SPEED = SPEED = 10              # Velocidades
FPS = 30                             # Frames por segundo
GROUND_WIDTH = SCREEN_WIDTH * 2      # Comprimento do chão
GROUND_HEIGHT = 100                  # Altura do chão
PIPE_WIDTH = 80                      # Comprimento do cano
PIPE_HEIGHT = 500                    # Altura do cano
PIPE_GAP = 200                       # Espaço entre os canos
DIE = 0                              # Identificação para o som de morte
HIT = 1                              # Identificação para o som de colisão
POINT = 2                            # Identificação para o som de pontuação
SWOOSH = 3                           # Identificação para o som da corrente de ar
WING = 4                             # Identificação para o som de voo
# Comandos para o PyInstaller
dirpath = getcwd()
syspath.append(dirpath)
if getattr(sys, "frozen", False):
    chdir(sys._MEIPASS)

class Bird(pygame.sprite.Sprite):
    '''Classe que representa o pássaro'''
    def __init__(self, color):
        pygame.sprite.Sprite.__init__(self)
        self.images = (
            pygame.image.load(
                f'{BIRDS_PATH}/{color}/upflap.png'
            ).convert_alpha(),
            pygame.image.load(
                f'{BIRDS_PATH}/{color}/midflap.png'
            ).convert_alpha(),
            pygame.image.load(
                f'{BIRDS_PATH}/{color}/downflap.png'
            ).convert_alpha()
        )
        self.speed = SPEED
        self.current_image = 0
        self.image = self.images[self.current_image]
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect[0] = (SCREEN_WIDTH / 2) - (self.image.get_width() / 2)
        self.rect[1] = SCREEN_HEIGHT / 2

    def update(self):
        '''Função que representa como o pássaro se comporta em cada interação no jogo'''
        self.speed += GRAVITY
        self.current_image = (self.current_image + 1) % 3
        self.image = pygame.transform.rotozoom(self.images[self.current_image], self.speed * -3, 1)
        self.rect[1] += self.speed

    def bump(self):
        '''Função que representa a ação de voar do pássaro'''
        self.speed = -SPEED

    def get_width(self):
        '''Função que retorna o comprimento do pássaro'''
        return self.image.get_size()[0]

    def get_height(self):
        '''Função que retorna a altura do pássaro'''
        return self.image.get_size()[1]

class Pipe(pygame.sprite.Sprite):
    '''Classe que representa os canos'''
    def __init__(self, color, inverted, pos_x, size_y):
        pygame.sprite.Sprite.__init__(self)
        self.images = (
            pygame.image.load(f'{PIPES_PATH}/{color}.png').convert_alpha(),
            pygame.image.load(f'{PIPES_PATH}/{color}.png').convert_alpha()
        )
        self.current_image = 0
        self.image = self.images[self.current_image]
        self.image = pygame.transform.scale(self.image, (PIPE_WIDTH,PIPE_HEIGHT))
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect[0] = pos_x
        if inverted:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect[1] = -(self.rect[3] - size_y + GROUND_HEIGHT)
        else:
            self.rect[1] = SCREEN_HEIGHT - size_y - GROUND_HEIGHT

    def update(self):
        '''Função que representa como os canos se comportam em cada interação no jogo'''
        self.rect[0] -= GAME_SPEED

    def get_width(self):
        '''Função que retorna o comprimento do cano'''
        return self.image.get_size()[0]

    def get_height(self):
        '''Função que retorna a altura do cano'''
        return self.image.get_size()[1]

class Ground(pygame.sprite.Sprite):
    '''Classe que representa o chão'''
    def __init__(self, pos_x):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(
            f'{SCENERY_PATH}/ground.png'
        ).convert_alpha()
        self.image = pygame.transform.scale(self.image, (GROUND_WIDTH, GROUND_HEIGHT))
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect[0] = pos_x
        self.rect[1] = SCREEN_HEIGHT - GROUND_HEIGHT

    def update(self):
        '''Função que representa o comportamento do chão em cada interação no jogo'''
        self.rect[0] -= GAME_SPEED

    def get_width(self):
        '''Função que retorna o comprimento do chão'''
        return self.image.get_size()[0]

    def get_height(self):
        '''Função que retorna a altura do chão'''
        return self.image.get_size()[1]

def is_off_screen(sprite):
    '''Função que testa se o objeto ainda está na tela'''
    return sprite.rect[0] < -(sprite.rect[2])

def has_scored(sprite, pos_x):
    '''Função que testa se o cano passou do pássaro'''
    return sprite.rect[0] == pos_x

def get_random_pipes(pos_x):
    '''Função que gera os canos aleatórios do jogo'''
    colors = ['green', 'red']
    color = choice(colors)
    size = randint(GROUND_HEIGHT, PIPE_HEIGHT)
    pipe = Pipe(color, False, pos_x, size)
    pipe_inverted = Pipe(color, True, pos_x, SCREEN_HEIGHT - size - PIPE_GAP)
    return (pipe, pipe_inverted)

def create_file():
    '''Função que cria o arquivo de dados'''
    open(f'{BASE_DIR}/score.dat', 'xb+')

def manipulate_file():
    '''Função que manipula um arquivo de dados'''
    return open(f'{BASE_DIR}/score.dat', 'rb+')

def set_high_score(file, value):
    '''Função que grava em um arquivo a pontuação máxima do jogo'''
    pickle.dump(value, file)

def get_high_score(file):
    '''Função que lê de um arquivo a pontuação máxima salva do jogo'''
    return int(pickle.load(file))

def draw_score(sface, value, align, position):
    '''Função que desenha e exibe a pontuação na tela'''
    # Criação dos números gráficos da pontuação do jogo
    numbers = (
        pygame.image.load(f'{NUMS_PATH}/0.png').convert_alpha(),
        pygame.image.load(f'{NUMS_PATH}/1.png').convert_alpha(),
        pygame.image.load(f'{NUMS_PATH}/2.png').convert_alpha(),
        pygame.image.load(f'{NUMS_PATH}/3.png').convert_alpha(),
        pygame.image.load(f'{NUMS_PATH}/4.png').convert_alpha(),
        pygame.image.load(f'{NUMS_PATH}/5.png').convert_alpha(),
        pygame.image.load(f'{NUMS_PATH}/6.png').convert_alpha(),
        pygame.image.load(f'{NUMS_PATH}/7.png').convert_alpha(),
        pygame.image.load(f'{NUMS_PATH}/8.png').convert_alpha(),
        pygame.image.load(f'{NUMS_PATH}/9.png').convert_alpha()
    )
    score_img_width = 0
    # Cria uma lista com os números da pontuação
    score = list(value)
    score_img = []
    # Converte a lista com os números da pontuação para uma lista com a representação gráfica
    for num in enumerate(score):
        score_img.append(numbers[int(num[1])])
        score_img_width += numbers[int(num[1])].get_width()
    # Cálculo das posições do primeiro digito da pontuação
    # Define a posição do X
    if align == 'center':
        score_img_pos_x = SCREEN_WIDTH / 2 - score_img_width / 2
    elif align == 'left':
        score_img_pos_x = 10
    elif align == 'right':
        score_img_pos_x = SCREEN_WIDTH - 10 - score_img_width
    else:
        score_img_pos_x = SCREEN_WIDTH + 10
    # Define a posição do Y
    if position == 'top':
        score_img_pos_y = 10
    elif position == 'bottom':
        score_img_pos_y = SCREEN_HEIGHT - 10 - numbers[0].get_height()
    else:
        score_img_pos_y = SCREEN_HEIGHT + 10
    # Desenha a pontuação na tela
    for img in enumerate(score_img):
        sface.blit(img[1], (score_img_pos_x, score_img_pos_y))
        score_img_pos_x += img[1].get_width()    # Posição X para desenhar o próximo digito

def close_game():
    '''Função que encerra todas as bibliotecas e fecha o jogo'''
    pygame.display.quit()
    pygame.mixer.quit()
    pygame.quit()
    ext()

def main():
    '''Função principal que trata de toda a execução do jogo'''
    # Centraliza a janela do jogo no monitor
    environ['SDL_VIDEO_CENTERED'] = '1'
    pygame.init()
    pygame.mixer.pre_init(frequency = 44100, size = 16, channels = 1, buffer = 512)
    splash = True
    run = False
    # Criação da janela
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    icon = pygame.image.load(f'{ICON_PATH}/icon.png').convert_alpha()
    pygame.display.set_icon(icon)
    pygame.display.set_caption('Flappy Bird v1.0')
    # Contador de pontuação do jogo
    score = 0
    # Carrega a informação da pontuação máxima do jogo
    if path.isfile(f'{BASE_DIR}/score.dat'):
        file = manipulate_file()
        high_score = get_high_score(file)
        file.close()
    else:
        high_score = score
        create_file()
        file = manipulate_file()
        set_high_score(file, str(high_score))
        file.close()
    # Testa o sistema em que o jogo está rodando
    sound_type = 'wav' if 'win' in plat else 'ogg'
    # Carregamento dos sons do jogo
    sounds = (
        pygame.mixer.Sound(f'{SOUNDS_PATH}/{sound_type}/die.{sound_type}'),
        pygame.mixer.Sound(f'{SOUNDS_PATH}/{sound_type}/hit.{sound_type}'),
        pygame.mixer.Sound(f'{SOUNDS_PATH}/{sound_type}/point.{sound_type}'),
        pygame.mixer.Sound(f'{SOUNDS_PATH}/{sound_type}/swoosh.{sound_type}'),
        pygame.mixer.Sound(f'{SOUNDS_PATH}/{sound_type}/wing.{sound_type}')
    )
    # Criação das mensagens do jogo
    messages = (
        pygame.image.load(f'{MSGS_PATH}/start_game.png').convert_alpha(),
        pygame.image.load(f'{MSGS_PATH}/game_over.png').convert_alpha(),
        pygame.image.load(f'{MSGS_PATH}/high_score.png').convert_alpha()
    )
    # Criação da imagem de fundo
    backgrounds = (
        pygame.image.load(f'{SCENERY_PATH}/day.png'),
        pygame.image.load(f'{SCENERY_PATH}/night.png')
    )
    journeys = ('day', 'night')
    journey = choice(journeys)
    background = backgrounds[1] if journey == 'night' else backgrounds[1]
    background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))
    # Criação do pássaro
    bird_group = pygame.sprite.Group()
    bird_colors = ('blue', 'red', 'yellow')
    bird = Bird(choice(bird_colors))
    bird_group.add(bird)
    goal = (((bird.rect[0] - bird.get_width()) // 10) - 1) * 10     # Define a linha de pontuação
    # Criaação do chão
    ground_group = pygame.sprite.Group()
    for i in range(2):
        ground = Ground(GROUND_WIDTH * i)
        ground_group.add(ground)
    # Criação dos canos
    pipe_group = pygame.sprite.Group()
    for i in range(2):
        pipes = get_random_pipes(SCREEN_WIDTH * (i + 2))
        pipe_group.add(pipes[0])
        pipe_group.add(pipes[1])
    # Criação do controle de tempo do jogo
    clock = pygame.time.Clock()
    # Laço da tela de abertura do jogo
    while splash:
        splash = messages[0]
        splash_x = SCREEN_WIDTH / 2 - splash.get_width() / 2
        splash_y = SCREEN_HEIGHT / 2 - splash.get_height() / 2
        screen.blit(background, (0, 0))
        screen.blit(splash, (splash_x, splash_y))
        for event in pygame.event.get():
            if event.type == QUIT:
                close_game()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    close_game()
                if event.key == K_SPACE:
                    splash = False
                    run = True
        if high_score > 0:
            highscore = messages[2]                                       # Imagem de High Score
            highscore_x = SCREEN_WIDTH / 2 - highscore.get_width() / 2    # Pos X
            highscore_y = SCREEN_HEIGHT - highscore.get_height() - 40     # Pos Y
            screen.blit(highscore, (highscore_x, highscore_y))            # Exibe a imagem
            draw_score(screen, str(high_score), 'center', 'bottom')       # Exibe o valor
        pygame.display.update()
    # Laço de execução do jogo
    while run:
        # Controle da velocidade do jogo
        clock.tick(FPS)
        # Controle dos eventos do jogo
        for event in pygame.event.get():
            # Evento que fecha a janela
            if event.type == QUIT:
                close_game()
            # Evento que identifica a tecla pressionada
            if event.type == KEYDOWN:
                # Teste para saber se a tecla é "BARRA DE ESPAÇO"
                if event.key == K_SPACE:
                    bird.bump()
                    pygame.mixer.Sound.play(sounds[WING])
        # Desenho da imagem de fundo do jogo
        screen.blit(background, (0, 0))
        # Tomada de decisão quando o chão estiver fora da tela
        if is_off_screen(ground_group.sprites()[0]):
            ground_group.remove(ground_group.sprites()[0]) # Remove o chão
            new_ground = Ground(GROUND_WIDTH - 10)         # Cria um novo chão, com atraso de 10px
            ground_group.add(new_ground)                   # Adiciona o novo chão
        # Tomada de decisão quando o cano estiver fora da tela
        if is_off_screen(pipe_group.sprites()[0]):
            pipe_group.remove(pipe_group.sprites()[0])     # Remove o cano do chão
            pipe_group.remove(pipe_group.sprites()[0])     # Remove o cano invertido
            pipes = get_random_pipes(SCREEN_WIDTH * 2)     # Cria dois novos canos aleatórios
            pipe_group.add(pipes[0])                       # Adiciona o cano do chão
            pipe_group.add(pipes[1])                       # Adiciona o cano invertido
        # Tomada de decisão quando o cano passar do pássaro
        if has_scored(pipe_group.sprites()[0], goal):
            pygame.mixer.Sound.play(sounds[POINT])         # Tocar som de pontuação
            score += 1                                     # Incrementar a pontuação
        # Atualização dos objetos na tela
        bird_group.update()                                # Atualização do pássaro
        pipe_group.update()                                # Atualização dos canos
        ground_group.update()                              # Atualização do chão
        # Desenha os objetos na tela
        bird_group.draw(screen)                            # Desenha o pássaro
        pipe_group.draw(screen)                            # Desenha os canos
        ground_group.draw(screen)                          # Desenha o chão
#        # Desenha uma linha no local da pontuação, onde o cano passa do pássaro
#        pygame.draw.line(screen, RED, [goal, 0], [goal, SCREEN_HEIGHT], 2)
        draw_score(screen, str(score), 'center', 'top')    # Desenha a pontuação do jogo
        # Atualização da tela
        pygame.display.update()
        # Detecção de colisão e fim do jogo
        if (
            pygame.sprite.groupcollide(
                bird_group,
                ground_group,
                False,
                False,
                pygame.sprite.collide_mask
            ) or                              # O jogo acaba se o pássaro bater no chão ou
            pygame.sprite.groupcollide(
                bird_group,
                pipe_group,
                False,
                False,
                pygame.sprite.collide_mask
            )                                 # se bater nos canos
        ):
            gameover = messages[1]                                     # Imagem de Game Over
            gameover_x = SCREEN_WIDTH / 2 - gameover.get_width() / 2   # Pos X
            gameover_y = SCREEN_HEIGHT / 2 - gameover.get_height() / 2 # Pos Y
            screen.blit(gameover, (gameover_x, gameover_y))            # Exibe a mensagem
            pygame.display.update()                                    # Atualização da tela
            pygame.mixer.Sound.play(sounds[HIT])                       # Tocar som de colisão
            pygame.mixer.Sound.play(sounds[DIE])                       # Tocar som de morte
            if score > high_score:                                     # Grava a pontuação máxima
                file = manipulate_file()
                set_high_score(file, str(score))
                file.close()
            pygame.time.wait(1000)                                     # Aguarda 1seg
            run = False                                                # Saída do laço

try:
    if __name__ == "__main__":
        while True:
            main()
except SyntaxError as syntax_exception:
    print(f'Oops! Ocorreu um erro de sintaxe no código.\n\
        __class__ = {syntax_exception.__class__}\n\
        __doc__ = {syntax_exception.__doc__}\n\
        args = {syntax_exception.args}')
except (ValueError, ZeroDivisionError) as value_exception:
    print(f'Oops! Ocorreu um erro de valores.\n\
        __class__ = {value_exception.__class__}\n\
        __doc__ = {value_exception.__doc__}\n\
        args = {value_exception.args}')
except TypeError as type_exception:
    print(f'Oops! Ocorreu um erro de conversão de tipo de dados.\n\
        __class__ = {type_exception.__class__}\n\
        __doc__ = {type_exception.__doc__}\n\
        args = {type_exception.args}')
except Exception as general_exception:
    print(f'Oops! Ocorreu um erro não identificado.\n\
        __class__ = {general_exception.__class__}\n\
        __doc__ = {general_exception.__doc__}\n\
        args = {general_exception.args}')
finally:
    close_game()
