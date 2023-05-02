import os
import toml
from typing import Generator
from copy import deepcopy
from subprocess import Popen, PIPE, STDOUT

UPLOADS_FOLDER = 'uploads'
CONFIG_FOLDER = 'config'
GLOBAL_CONFIG = 'config.cfg'
PART_CONFIGS = [
    "ai.bak.cfg",
    "chat.bak.cfg",
    "other.bak.cfg",
]


def empty_field(value) -> bool:
    return not (value.strip() if isinstance(value, str) else (True if isinstance(value, bool) else value))


def clean_config(data: dict) -> dict:
    for key, value in deepcopy(data).items():
        if isinstance(value, dict):
            data[key] = clean_config(value)
        if isinstance(value, (list, tuple, set)):
            data[key] = [clean_config(element) if isinstance(element, dict) else element for element in value]
        elif empty_field(value):
            del data[key]
    return data


def execute_command(command: str) -> Generator[str, None, None]:
    process = Popen(command, stdout=PIPE, stderr=STDOUT, shell=True, text=True, bufsize=1)
    for line in process.stdout:
        yield line
    process.stdout.close()
    process.wait()


def read_conf(filename: str) -> dict:
    path = os.path.join(CONFIG_FOLDER, filename)
    if os.path.isfile(path):
        with open(path, "r") as fp:
            return toml.load(fp)
    return {}


def save_conf(filename: str, data: dict, override=True) -> str:
    """
    保存配置文件
    :param filename: 配置文件名
    :param data: 内容
    :param override: 是否覆盖全局配置 config.cfg
    :return: 配置文件路径
    """

    path = os.path.join(CONFIG_FOLDER, filename)
    if filename in [*PART_CONFIGS, GLOBAL_CONFIG]:
        with open(path, "w") as fp:
            toml.dump(clean_config(data), fp)
        if override is True:
            save_global_conf()
    return path


def save_global_conf() -> str:
    """拼接文件并写入 config.cfg"""
    return save_conf(
        GLOBAL_CONFIG,
        {k: v for conf in PART_CONFIGS for k, v in read_conf(conf).items()},
        override=False,  # 防止递归
    )


def handle_upload(file) -> None:
    if not os.path.exists(UPLOADS_FOLDER):
        os.makedirs(UPLOADS_FOLDER)
    file.save(os.path.join(UPLOADS_FOLDER, file.filename))
