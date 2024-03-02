import pygame
from pygame import mixer
import pickle
from os import path

pygame.mixer.pre_init(44100, -16, 2, 512)
mixer.init()
pygame.init()
clock = pygame.time.Clock()
fps = 60
screen_width = 1000
screen_height = 1000

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Yerbolat')
font = pygame.font.Font('font/minecraft.ttf', 70)
font_score = pygame.font.Font('font/minecraft.ttf', 30)

# razmer objecta
tile_size = 50
game_over = 0
main_menu = True
level = 0
max_levels = 7
score = 0
aq = (255, 255, 255)
red = (255, 0, 0)
bg_img = pygame.image.load('img/sky.png')
restart_img = pygame.image.load('img/restart_btn.png')
start_img = pygame.image.load('img/start_btn.png')
exit_img = pygame.image.load('img/exit_btn.png')

# звуки
# бэкграунд
pygame.mixer.music.load('img/C418_-_Minecraft_-_Main_Theme_65703958.mp3')
pygame.mixer.music.play(-1, 0.0, 5000)
# когда подобрал алмаз
coin_fx = pygame.mixer.Sound('img/inecraft_levelu.mp3')
coin_fx.set_volume(0.5)  # громкость
game_over_fx = pygame.mixer.Sound('img/minecraft_hurt_alpha_2009.mp3')
game_over_fx.set_volume(0.5)  # громкость


# функция для шрифта текст шриыт сверху цвет координаты
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


# сброс уровня
def reset_level(level):
    global world_data
    player.reset(100, screen_height - 130)  # сброс позиции игрока
    blob_group.empty()
    platform_group.empty()
    coin_group.empty()
    lava_group.empty()
    exit_group.empty()
    if path.exists(f'level{level}_data'):
        pickle_in = open(f'level{level}_data', 'rb')
        world_data = pickle.load(pickle_in)
    world = World(world_data)
    # создать алмаз для счетчика
    score_coin = Coin(tile_size // 2, tile_size // 2)
    coin_group.add(score_coin)
    return world


# кнопки
class Button:
    def __init__(self, x, y, image):
        self.image = image  # картина
        self.rect = self.image.get_rect()  # границы кнопки х у
        self.rect.x = x
        self.rect.y = y
        self.clicked = False  # не нажата

    def draw(self):
        action = False

        # поз мышки
        pos = pygame.mouse.get_pos()

        # проверять нажатие мышки
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                action = True
                self.clicked = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        # рисовать на экоан
        screen.blit(self.image, self.rect)

        return action


# создание персонажа
class Player():
    def __init__(self, x, y):  # инициализирует игрока значениями x y
        self.reset(x, y)  # рестартает

    def update(self, game_over):
        dx = 0
        dy = 0
        walk_cooldown = 5
        col_thresh = 20

        if game_over == 0:
            # дывыйженияго движения
            key = pygame.key.get_pressed()
            if key[pygame.K_SPACE] and self.jumped == False and self.in_air == False:
                self.vel_y = -16
                self.jumped = True
            if key[pygame.K_SPACE] == False:
                self.jumped = False
            if key[pygame.K_LEFT]:
                dx -= 5
                self.counter += 1
                self.direction = -1
            if key[pygame.K_RIGHT]:
                dx += 5
                self.counter += 1
                self.direction = 1
            if key[pygame.K_LEFT] == False and key[pygame.K_RIGHT] == False:
                self.counter = 0
                self.index = 0
                if self.direction == 1:
                    self.image = self.images_right[self.index]
                if self.direction == -1:
                    self.image = self.images_left[self.index]

            # анимация движения
            if self.counter > walk_cooldown:
                self.counter = 0
                self.index += 1  # если условие орныдалса то анимация +1 кадр
                if self.index >= len(self.images_right):  # цикличная анимацияга керек
                    self.index = 0
                if self.direction == 1:  # направление движения
                    self.image = self.images_right[self.index]
                if self.direction == -1:
                    self.image = self.images_left[self.index]

            # гравитация
            self.vel_y += 1
            if self.vel_y > 10:  # если больше этого то опускает
                self.vel_y = 10
            dy += self.vel_y

            # проверка нато задел ли или нет
            self.in_air = True
            for tile in world.tile_list:
                # по х осе
                if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0
                # по у осе
                if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    # проверка на прыжок
                    if self.vel_y < 0:
                        dy = tile[1].bottom - self.rect.top
                        self.vel_y = 0
                    # проерка на падение над землей
                    elif self.vel_y >= 0:
                        dy = tile[1].top - self.rect.bottom
                        self.vel_y = 0
                        self.in_air = False

            # проверка на столкновение с слаймом
            if pygame.sprite.spritecollide(self, blob_group, False):
                game_over = -1
                game_over_fx.play()

            # проверка на столкновение с лавой
            if pygame.sprite.spritecollide(self, lava_group, False):
                game_over = -1
                game_over_fx.play()

            # проверка на столкновение с дверью те выходом
            if pygame.sprite.spritecollide(self, exit_group, False):
                game_over = 1

            # движущиеся платформы
            for platform in platform_group:
                # cпо хollision in the x direction
                if platform.rect.colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0
                # по у
                if platform.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    # над/на плат
                    if abs((self.rect.top + dy) - platform.rect.bottom) < col_thresh:
                        self.vel_y = 0
                        dy = platform.rect.bottom - self.rect.top
                    # под плат
                    elif abs((self.rect.bottom + dy) - platform.rect.top) < col_thresh:
                        self.rect.bottom = platform.rect.top - 1
                        self.in_air = False
                        dy = 0
                    # двигатся на платформе
                    if platform.move_x != 0:
                        self.rect.x += platform.move_direction

            # обновление координат игрока
            self.rect.x += dx
            self.rect.y += dy

        # проигрыш
        elif game_over == -1:
            self.image = self.dead_image
            draw_text('You Died!', font, red, (screen_width // 2) - 200, screen_height // 2)
            if self.rect.y > 200:
                self.rect.y -= 5

        # вывести игрока на экран
        screen.blit(self.image, self.rect)

        return game_over

    # функция для ресета
    def reset(self, x, y):
        # направление игрока
        self.images_right = []
        self.images_left = []
        # устанавливет ака сбрасывает значения
        self.index = 0
        self.counter = 0
        # цикл ддля загрузки персонажа,направо налево
        for num in range(1, 5):
            img_right = pygame.image.load(f'img/guy{num}.png')
            img_right = pygame.transform.scale(img_right, (40, 80))
            img_left = pygame.transform.flip(img_right, True, False)
            self.images_right.append(img_right)
            self.images_left.append(img_left)
        # эффект при смерти
        self.dead_image = pygame.image.load('img/ghost.png')
        # устанавливается в первое изображение в списке
        self.image = self.images_right[self.index]
        self.rect = self.image.get_rect()
        # позиции ресета
        self.rect.x = x
        self.rect.y = y
        # размера изображения
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        # вертикальная скорость
        self.vel_y = 0
        # не прыгал
        self.jumped = False
        # по х не двигался
        self.direction = 0
        # персонаж сейчас в воздхухе
        self.in_air = True


# создание мира каждый тайл это разный обьект в игре
class World():
    def __init__(self, data):
        self.tile_list = []
        dirt_img = pygame.image.load('img/dirt.png')
        grass_img = pygame.image.load('img/grass.png')
        row_count = 0
        for row in data:
            col_count = 0
            for tile in row:
                if tile == 1:
                    img = pygame.transform.scale(dirt_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 2:
                    img = pygame.transform.scale(grass_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 3:
                    blob = Enemy(col_count * tile_size, row_count * tile_size + 15)
                    blob_group.add(blob)
                if tile == 4:
                    platform = Platform(col_count * tile_size, row_count * tile_size, 1, 0)
                    platform_group.add(platform)
                if tile == 5:
                    platform = Platform(col_count * tile_size, row_count * tile_size, 0, 1)
                    platform_group.add(platform)
                if tile == 6:
                    lava = Lava(col_count * tile_size, row_count * tile_size + (tile_size // 2))
                    lava_group.add(lava)
                if tile == 7:
                    coin = Coin(col_count * tile_size + (tile_size // 2), row_count * tile_size + (tile_size // 2))
                    coin_group.add(coin)
                if tile == 8:
                    exit = Exit(col_count * tile_size, row_count * tile_size - (tile_size // 2))
                    exit_group.add(exit)
                col_count += 1
            row_count += 1

    def draw(self):
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])


# cлайм
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('img/blob.png')
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_direction = 1
        self.move_counter = 0

    # движение слайма
    def update(self):
        self.rect.x += self.move_direction
        self.move_counter += 1
        if abs(self.move_counter) > 50:
            self.move_direction *= -1
            self.move_counter *= -1


# платформы с ютуба
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, move_x, move_y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('img/platform.png')
        self.image = pygame.transform.scale(img, (tile_size, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_counter = 0
        self.move_direction = 1
        self.move_x = move_x
        self.move_y = move_y

    def update(self):
        self.rect.x += self.move_direction * self.move_x
        self.rect.y += self.move_direction * self.move_y
        self.move_counter += 1
        if abs(self.move_counter) > 50:
            self.move_direction *= -1
            self.move_counter *= -1


# лава
class Lava(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('img/lava.png')
        self.image = pygame.transform.scale(img, (tile_size, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


# алмазы
class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('img/coin.png')
        # размеры
        self.image = pygame.transform.scale(img, (tile_size // 2, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)


# дверь
class Exit(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('img/exit.png')
        self.image = pygame.transform.scale(img, (tile_size, int(tile_size * 1.5)))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


# сам игрок и его размеры
player = Player(100, screen_height - 130)
# группы чтобы в экране они появлялись
blob_group = pygame.sprite.Group()
platform_group = pygame.sprite.Group()
lava_group = pygame.sprite.Group()
coin_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()

# счетчик алмаза
score_coin = Coin(tile_size // 2, tile_size // 2)
coin_group.add(score_coin)

# левела и прохож через лвла
if path.exists(f'level{level}_data'):
    pickle_in = open(f'level{level}_data', 'rb')
    world_data = pickle.load(pickle_in)
world = World(world_data)

# кнопка чтарта рестарта и выхода
restart_button = Button(screen_width // 2 - 175, screen_height // 2 + 100, restart_img)
start_button = Button(screen_width // 2 - 350, screen_height // 2, start_img)
exit_button = Button(screen_width // 2 + 150, screen_height // 2, exit_img)

run = True
while run:
    clock.tick(fps)
    screen.blit(bg_img, (0, 0))
    if main_menu == True:
        if exit_button.draw():
            run = False
        if start_button.draw():
            main_menu = False
    else:
        world.draw()
        if game_over == 0:
            blob_group.update()  # обновление счетчика
            platform_group.update()

            # подобрал ли алмаз
            if pygame.sprite.spritecollide(player, coin_group, True):
                score += 1
                coin_fx.play()
            draw_text('X ' + str(score), font_score, aq, tile_size - 10, 10)
        # те самые группы чтобы были на экране
        blob_group.draw(screen)
        platform_group.draw(screen)
        lava_group.draw(screen)
        coin_group.draw(screen)
        exit_group.draw(screen)

        game_over = player.update(game_over)

        # умер
        if game_over == -1:
            if restart_button.draw():
                world_data = []
                world = reset_level(level)
                game_over = 0
                score = 0

        # прошел
        if game_over == 1:
            # сброс уровня и на некст лвл
            level += 1
            if level <= max_levels:
                # ресет
                world_data = []
                world = reset_level(level)
                game_over = 0
                # прошел игру
            else:
                draw_text('YOU WIN!', font, red, (screen_width // 2) - 140, screen_height // 2)
                if restart_button.draw():
                    level = 1
                    # ресет
                    world_data = []
                    world = reset_level(level)
                    game_over = 0
                    score = 0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()


pygame.quit()


#yhx yt ch:buzz