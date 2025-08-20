import logging

class LoggerConfig:
    def __init__(self):
        self.logger = logging.getLogger("avatar_service")
        self.logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
        self.logger.addHandler(handler)

    def get_logger(self):
        return self.logger

avatar_service_logger = LoggerConfig().get_logger()
