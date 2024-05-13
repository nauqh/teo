import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    config_mapping = {
        'dev': {'primary': 'hym', 'secondary': 'monash'},
        'prod': {'primary': 'data', 'secondary': 'fsw'}
    }

    def __init__(self, mode: str):

        primary, secondary = self.config_mapping.get(mode, {}).values()
        self.TOKEN = os.getenv('TOKEN_DEV' if mode == 'dev' else 'TOKEN_PROD')
        self.ADMIN = int(os.getenv('ADMIN'))
        self._load_config(primary)
        self._load_config(secondary)

    def _load_config(self, config_name: str):
        config = globals().get(f"{config_name.capitalize()}Config")
        setattr(self, config_name.upper(), config())


class BaseConfig:
    def __init__(self, prefix):
        self.GUILD = int(os.getenv(f"{prefix}_GUILD"))
        self.FORUM_CHANNEL = int(os.getenv(f"{prefix}_FORUM_CHANNEL"))
        self.EXAM_CHANNEL = int(os.getenv(f"{prefix}_EXAM_CHANNEL"))
        self.STAFF_CHANNEL = int(os.getenv(f"{prefix}_STAFF_CHANNEL"))


class HymConfig(BaseConfig):
    def __init__(self):
        super().__init__('HYM')


class MonashConfig(BaseConfig):
    def __init__(self):
        super().__init__('MONASH')


class DataConfig(BaseConfig):
    def __init__(self):
        super().__init__('DATA')


class FswConfig(BaseConfig):
    def __init__(self):
        super().__init__('FSW')


if __name__ == "__main__":
    cf = Config('dev')
    print(cf.HYM.GUILD)
