import random

import pygame


class Enemy(pygame.sprite.Sprite):
    def __init__(self, position, ENV):
        super().__init__()
        self.image = pygame.transform.scale(
            pygame.image.load("./src/img/enemy/Enemy1.png").convert_alpha(), (50, 50)
        )
        self.start_position = position

        self.WINDOW_WIDTH = ENV["WINDOW_WIDTH"]
        self.WINDOW_HEIGHT = ENV["WINDOW_HEIGHT"]
        self.rect = self.image.get_rect(center=position)
        self.speed = 3

        self.__random_counter = 0
        self.__random_wait = 20
        self.__counter = 0
        self.x_speed = 1
        self.y_speed = 1

    def appearance(self):
        # 最初の1秒は少しずつ大きくなるように登場
        self.image = pygame.transform.scale(
            pygame.image.load("./src/img/enemy/Enemy1.png").convert_alpha(),
            (self.__counter, self.__counter),
        )
        self.rect = self.image.get_rect(center=self.start_position)

    def move(self):
        self.__random_counter += 1

        # ランダムに方向を変える
        if self.__random_counter > self.__random_wait:
            random_choices = random.sample([1, 1, 0, -1, -1], 2)

            self.x_speed = random_choices[0]
            self.y_speed = random_choices[1]

            self.__random_counter = 0
            self.__random_wait = random.randrange(5, 80)

        # 壁にぶつかったら跳ね返る
        if self.rect.x < 0:
            self.rect.x = 0
            self.x_speed = self.x_speed * -1
        if self.rect.x > self.WINDOW_WIDTH:
            self.rect.x = self.WINDOW_WIDTH
            self.x_speed = self.x_speed * -1
        if self.rect.y < 0:
            self.rect.y = 0
            self.y_speed = self.y_speed * -1
        if self.rect.y > self.WINDOW_HEIGHT:
            self.rect.y = self.WINDOW_HEIGHT
            self.y_speed = self.y_speed * -1

        # 座標を反映
        self.rect.x += self.speed * self.x_speed
        self.rect.y += self.speed * self.y_speed

    def update(self):
        self.__counter += 1
        if self.__counter <= 60:
            self.appearance()
            return
        self.move()
