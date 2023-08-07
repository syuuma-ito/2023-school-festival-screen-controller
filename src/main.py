# インポート
import math
import os
import random
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import pygame
import socketio
from dotenv import load_dotenv
from rich.traceback import install

from enemy import Enemy
from player_pointer import PlayerPointer
from utils import logger
from utils.clipNumber import clipNumber

# ----------------------------------------------------------------
# 初期化
# .envファイルの内容を読み込む
load_dotenv()
# エラー表示をリッチに
install()
# 簡易ロガーを初期化
log = logger.logger()
log.set_level(log.DEBUG)


# ----------------------------------------------------------------
# 定数
SCENE_WIDTH_CM = int(os.environ.get("SCENE_WIDTH_CM"))
SCENE_HEIGHT_CM = int(os.environ.get("SCENE_HEIGHT_CM"))
RANGE_WITH_SCREEN = int(os.environ.get("RANGE_WITH_SCREEN"))
# 画面サイズ
WINDOW_WIDTH = int(os.environ.get("WINDOW_WIDTH"))
WINDOW_HEIGHT = int(os.environ.get("WINDOW_HEIGHT"))

SEVER_URL = os.environ.get("SEVER_URL")
FPS = 60
BACKGROUND_COLOR = (0, 0, 0)

ENV = {
    "SCENE_WIDTH_CM": SCENE_WIDTH_CM,
    "SCENE_HEIGHT_CM": SCENE_HEIGHT_CM,
    "RANGE_WITH_SCREEN": RANGE_WITH_SCREEN,
    "WINDOW_WIDTH": WINDOW_WIDTH,
    "WINDOW_HEIGHT": WINDOW_HEIGHT,
    "SEVER_URL": SEVER_URL,
    "FPS": FPS,
    "BACKGROUND_COLOR": BACKGROUND_COLOR,
}

# ----------------------------------------------------------------
# グローバル変数
Global_X = 0
Global_Y = 0
Global_scene = "game"
# ----------------------------------------------------------------
# メイン


class IoClient:
    def __init__(self):
        self.socket = socketio.Client()

        # イベント登録
        self.socket.on("connect", self.__on_connect)
        self.socket.on("disconnect", self.__on_disconnect)
        self.socket.on("angles", self.__on_angle)

    # イベントハンドラ
    def __on_connect(self):
        log.debug("socket.io sever connect")

    def __on_disconnect(self):
        log.debug("socket.io sever disconnect")

    def __on_angle(self, angle):
        global Global_X, Global_Y
        Global_X, Global_Y = self.__calc_coordinate(angle["x"] - 290, angle["y"])

    def __calc_coordinate(self, theta1, theta2):
        # スマホの角度から座標を計算
        x = (
            (
                (SCENE_WIDTH_CM / 2)
                - (RANGE_WITH_SCREEN * math.tan(math.radians(theta1)))
            )
            / SCENE_WIDTH_CM
        ) * WINDOW_WIDTH
        y = (
            (
                (SCENE_HEIGHT_CM / 2)
                - (RANGE_WITH_SCREEN * math.tan(math.radians(theta2)))
            )
            / SCENE_HEIGHT_CM
        ) * WINDOW_HEIGHT
        x = clipNumber(round(x), -25, WINDOW_WIDTH - 25)
        y = clipNumber(round(y), -25, WINDOW_HEIGHT - 25)
        return x, y

    # メイン
    def connect(self, server_url):
        log.info(f"connect to {server_url}")
        self.socket.connect(server_url)
        log.info("socket.io waiting...")
        self.socket.wait()


def socket_main():
    client = IoClient()
    client.connect(SEVER_URL)


def game_main():
    global Global_X
    global Global_Y

    # ページの設定
    class GamePage:
        def __init__(self):
            pointer_sprite = PlayerPointer((0, 0))
            self.player_pointer = pygame.sprite.GroupSingle(pointer_sprite)

            self.enemies = []
            for _ in range(5):
                enemy_sprite = Enemy(
                    (
                        random.randrange(0, WINDOW_WIDTH),
                        random.randrange(0, WINDOW_HEIGHT),
                    ),
                    ENV,
                )
                self.enemies.append(pygame.sprite.GroupSingle(enemy_sprite))

        def run(self):
            # アップデート
            # 描画
            self.player_pointer.update()
            self.player_pointer.draw(screen)
            for enemy in self.enemies:
                enemy.update()
                enemy.draw(screen)

    class WaitPage:
        def __init__(self):
            pass

        def run(self):
            # アップデート
            # 描画
            pass

    # Pygameの初期化
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("インバーター画面プログラム")
    clock = pygame.time.Clock()

    game_page = GamePage()
    wait_page = WaitPage()

    # メインループ
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        screen.fill(BACKGROUND_COLOR)
        if Global_scene == "wait":
            wait_page.run()
        elif Global_scene == "game":
            game_page.run()

        pygame.display.flip()
        clock.tick(FPS)


def main():
    with ThreadPoolExecutor(max_workers=10) as executor:
        executor.submit(game_main)
        executor.submit(socket_main)


if __name__ == "__main__":
    log.info("[緑]========= START =========[/]")
    game_main()
    main()
