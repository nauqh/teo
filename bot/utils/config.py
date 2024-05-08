import tomllib


def load_config() -> dict:
    with open("config.toml", "rb") as f:
        return tomllib.load(f)


settings = load_config()
