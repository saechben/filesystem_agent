
import os
from functools import lru_cache
from pathlib import Path

from omegaconf import DictConfig, OmegaConf

CONFIG_PATH = Path(__file__).with_name("config.yml")
API_KEY_ENV_VAR = "LLM_API_KEY"


def _build_config() -> DictConfig:
    cfg = OmegaConf.load(CONFIG_PATH)
    if not isinstance(cfg, DictConfig):
        raise TypeError("config.yml must contain a mapping at the top level")

    api_key = os.getenv(API_KEY_ENV_VAR)
    if api_key:
        env_cfg = OmegaConf.create({"api": {"key": api_key}})
        cfg = OmegaConf.merge(cfg, env_cfg)

    if not isinstance(cfg, DictConfig):
        raise TypeError("merged configuration must remain a mapping")
    return cfg


@lru_cache
def get_config() -> DictConfig:
    return _build_config()


def reload_config() -> DictConfig:
    cfg = _build_config()
    get_config.cache_clear()
    return cfg
