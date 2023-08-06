import random

import pygame


class Enemy(pygame.sprite.Sprite):
    def __init__(self, position, WINDOW_WIDTH, WINDOW_HEIGHT):
        super().__init__()
        self.image = pygame.transform.scale(
            pygame.image.load("./src/img/enemy/Enemy1.png").convert_alpha(), (50, 50)
        )

        self.WINDOW_WIDTH = WINDOW_WIDTH
        self.WINDOW_HEIGHT = WINDOW_HEIGHT
        self.rect = self.image.get_rect(center=position)
        self.speed = 3

        self.__random_counter = 0
        self.__random_wait = 20
        self.x_speed = 1
        self.y_speed = 1

    def move(self):
        self.__random_counter += 1

        # ランダムに方向を変える
        if self.__random_counter > self.__random_wait:
            self.x_speed = random.choice([1, 0, -1])
            self.y_speed = random.choice([1, 0, -1])

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

        self.rect.x += self.speed * self.x_speed
        self.rect.y += self.speed * self.y_speed

    def update(self):
        self.move()
