from environs import Env

class Config:
    def __init__(self):
        self.env = Env()
        self.env.read_env()

        self.token = self.env.str("TOKEN")
        self.admin_id = self.env.int("ADMIN_ID")

        self.db_user = self.env.str("DB_USER")
        self.db_password = self.env.str("DB_PASSWORD")
        self.db_host = self.env.str("DB_HOST")
        self.db_port = self.env.int("DB_PORT")
        self.db_name = self.env.str("DB_NAME")

config = Config()
