import os, secrets, datetime

class Env:
    def __init__(self):
        self.postgresConnectionString = os.environ.get('POSTGRES_CONNECTION_STRING')
        self.webPort = os.environ.get('WEB_PORT')
        self.secret = os.environ.get('SECRET')

        if not self.postgresConnectionString:
            raise ValueError('POSTGRES_CONNECTION_STRING not in env')
    
        try: self.webPort = int(self.webPort)
        except Exception:
            raise ValueError('WEB_PORT not in env as an integer')
    
        if self.webPort < 1 or self.webPort > 65535:
            raise ValueError('WEB_PORT not in range of a valid port')

class Session:
    def __init__(self):
        self.secret = hex(secrets.randbits(200))[2:]
        self.reset_validity()
  
    def reset_validity(self):
        self.validity = datetime.datetime.now() + datetime.timedelta(minutes=30)
    
    def is_valid(self):
        return self.validity > datetime.datetime.now()

class Redirect:
    def __init__(self, id_: int, path: str, type_: str, target: str):
        self.id = id_
        self.path = path
        self.type = type_
        self.target = target
