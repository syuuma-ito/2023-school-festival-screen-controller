import pygame


class PlayerPointer(pygame.sprite.Sprite):
    def __init__(self, position):
        super().__init__()
        # TODO 色を変えられるようにする
        self.image = pygame.transform.scale(
            pygame.image.load("./src/img/pointer/ポインター緑.png").convert_alpha(), (50, 50)
        )
        self.rect = self.image.get_rect(center=position)
        self.speed = 5

    # TODO ここの処理をsocket.ioに置き換える (これは仮)
    def get_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_UP]:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN]:
            self.rect.y += self.speed

    def update(self):
        self.get_input()
