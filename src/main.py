# インポート
import logging
import math
import os
import random
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import obsws_python
import socketio
from dotenv import load_dotenv
from rich.traceback import install
from websocket_server import WebsocketServer

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
# ----------------------------------------------------------------
# グローバル変数
Global_X = 0
Global_Y = 0
websocket = None

USERS = {
    "1P": {
        "isConnect": False,
    },
    "2P": {
        "isConnect": False,
    },
    "3P": {
        "isConnect": False,
    },
}

obs = obsws_python.ReqClient(
    host=os.environ["OBSWS_HOST"],
    port=int(os.environ["OBSWS_PORT"]),
    password=os.environ["OBSWS_PASS"],
    timeout=3,
)

isStart = False

# ----------------------------------------------------------------
# メイン


class WebSocket:
    def __init__(self, host, port):
        self.server = WebsocketServer(host=host, port=port, loglevel=logging.DEBUG)
        self.port = port
        self.host = host
        self.server.set_fn_new_client(self.new_client)
        self.server.set_fn_message_received(self.message_received)
        self.server.set_fn_client_left(self.client_left)

    def new_client(self, client, server):
        log.info(f"connect id: {client['id']}")

    def client_left(self, client, server):
        log.info(f"disconnect id: {client['id']}")

    def message_received(self, client, server, message):
        log.info(f"on_message {message} [id: {client['id']}]")

    def run(self):
        log.debug(f"websocket server start {self.host}:{self.port}")
        self.server.run_forever()

    def emit(self, message):
        self.server.send_message_to_all(message)


class IoClient:
    def __init__(self):
        self.socket = socketio.Client()

        # イベント登録
        self.socket.on("connect", self.__on_connect)
        self.socket.on("disconnect", self.__on_disconnect)
        self.socket.on("angles", self.__on_angle)
        self.socket.on("shoot", self.__on_shoot)

    # イベントハンドラ
    def __on_connect(self):
        log.debug("socket.io sever connect")

    def __on_disconnect(self):
        log.debug("socket.io sever disconnect")

    def __on_angle(self, angle):
        global Global_X, Global_Y
        name = angle["name"]
        Global_X, Global_Y = self.__calc_coordinate(angle["x"] - 290, angle["y"])
        websocket.emit(f"angle,{Global_X},{Global_Y},{name}")

    def __on_shoot(self, shoot):
        print(shoot)
        websocket.emit(f"shoot,{Global_X},{Global_Y}")

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

    def connect(self, server_url):
        log.info(f"connect to {server_url}")
        self.socket.connect(server_url)
        log.info("socket.io waiting...")
        self.socket.wait()


def socket_main():
    client = IoClient()
    client.connect(SEVER_URL)


def websocket_main():
    global websocket
    websocket = WebSocket(host="127.0.0.1", port=13254)
    websocket.run()


def set_scene_item_enabled(scene_name: str, item_name: str, enabled: bool) -> None:
    items = obs.get_scene_item_list(scene_name).scene_items
    for item in items:
        if item["sourceName"] == item_name:
            obs.set_scene_item_enabled(scene_name, item["sceneItemId"], enabled)
            return
    raise ValueError(f"{scene_name}に{item_name}というソースはありません")


def obs_main():
    set_scene_item_enabled("待機", "Pointer_1P", False)
    set_scene_item_enabled("待機", "Pointer_2P", False)
    set_scene_item_enabled("待機", "Pointer_3P", False)
    set_scene_item_enabled("待機", "QRコード", True)
    set_scene_item_enabled("待機", "初期設定", True)
    set_scene_item_enabled("待機", "スタートボタン", True)
    set_scene_item_enabled("待機", "OK", True)

    # 始まるまで待機
    while True:
        if isStart:
            break
        set_scene_item_enabled("待機", "QRコード", True)
        set_scene_item_enabled("待機", "初期設定", True)
        if USERS["1P"]["isConnect"]:
            set_scene_item_enabled("待機", "Pointer_1P", True)
        if USERS["2P"]["isConnect"]:
            set_scene_item_enabled("待機", "Pointer_2P", True)
        if USERS["3P"]["isConnect"]:
            set_scene_item_enabled("待機", "Pointer_3P", True)
        time.sleep(5)
        set_scene_item_enabled("待機", "QRコード", False)
        if USERS["1P"]["isConnect"]:
            set_scene_item_enabled("待機", "Pointer_1P", True)
        if USERS["2P"]["isConnect"]:
            set_scene_item_enabled("待機", "Pointer_2P", True)
        if USERS["3P"]["isConnect"]:
            set_scene_item_enabled("待機", "Pointer_3P", True)
        time.sleep(5)
        set_scene_item_enabled("待機", "初期設定", False)
        if USERS["1P"]["isConnect"]:
            set_scene_item_enabled("待機", "Pointer_1P", True)
        if USERS["2P"]["isConnect"]:
            set_scene_item_enabled("待機", "Pointer_2P", True)
        if USERS["3P"]["isConnect"]:
            set_scene_item_enabled("待機", "Pointer_3P", True)
        time.sleep(5)


def main():
    with ThreadPoolExecutor(max_workers=3) as executor:
        # executor.submit(websocket_main)
        # executor.submit(socket_main)
        executor.submit(obs_main)


if __name__ == "__main__":
    log.info("[緑]========= START =========[/]")
    try:
        main()
    except KeyboardInterrupt:
        log.debug("KeyboardInterrupt")
    finally:
        log.info("=== END ===")
        sys.exit(0)
