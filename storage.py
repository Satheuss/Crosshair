import os
import sys
import json
from dataclasses import asdict, fields

from settings import Settings

NOME_ARQUIVO = "config.json"


def _pasta_do_app() -> str:
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def _caminho() -> str:
    return os.path.join(_pasta_do_app(), NOME_ARQUIVO)


def app_path(nome_arquivo: str) -> str:
    return os.path.join(_pasta_do_app(), nome_arquivo)


def load_settings() -> Settings:
    s = Settings()
    try:
        with open(_caminho(), "r", encoding="utf-8") as f:
            dados = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return s

    nomes_validos = {campo.name for campo in fields(Settings)}
    for chave, valor in dados.items():
        if chave in nomes_validos:
            setattr(s, chave, valor)
    return s


def save_settings(s: Settings) -> None:
    try:
        with open(_caminho(), "w", encoding="utf-8") as f:
            json.dump(asdict(s), f, indent=2)
    except OSError:
        pass
