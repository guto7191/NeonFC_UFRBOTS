from api import Api, Api_recv
import comm
import vision
import match
import argparse
import fields as pitch
from commons.utils import get_config
from pyVSSSReferee.RefereeComm import RefereeComm
from vision.sslvision import assign_empty_values

parser = argparse.ArgumentParser(description='NeonFC')
parser.add_argument('--config_file', default='config_real_life.json')
parser.add_argument('--env', default='real_life')

args = parser.parse_args()

class Game():
    def __init__(self, config_file=None, env='real_life'):
        self.config = get_config(config_file)
        self.match = match.MatchRealLife(self,
            **self.config.get('match') #config.get está mostrando o conteúdo da key nesse caso um dicionário
        )
        self.vision = vision.SSLVision()
        self.comm = comm.RLCommMqttESQ() # Comunicação UFRBOTS
        self.field = pitch.Field(self.match.category)
        self.environment = env

        self.use_api = self.config.get("api")
        self.api_address = self.config.get("network").get("api_address")
        self.api_port = self.config.get("network").get("api_port")
        self.api_recv_port = self.config.get("network").get("api_recv_port")

        self.referee = RefereeComm(config_file)

        self.api = Api(self.api_address, self.api_port)
        self.api_recv = Api_recv(self.match, self.api_address, self.api_recv_port)

        self.use_referee = False
        
        self.start()

    def start(self):
        self.vision.assign_vision(self)
        self.match.start()
        
        self.vision.start()
        self.comm.start()
        #self.mostrar_frame()

        if self.use_api:
            self.api.start()
            self.api_recv.start()
    
    def mostrar_frame(self):
        print(self.field.get_dimensions())

    def update(self):
        frame = assign_empty_values(
            self.vision.frame, 
            field_size=self.field.get_dimensions(),
            team_side=self.match.team_side,
            last_frame=self.vision.last_frame
        )
        #print(frame) # Print dos dados passados! VSS-vision 
        self.print_frame_Ufrbots(frame) # Print dos dados passados! VSS-vision 

        self.vision.last_frame = frame
        
        self.match.update(frame)
        commands = self.match.decide()

        self.print_comm_passados_UFRBots(commands)

        # Tentar entender ISSO!!!!!
        if self.use_api and (self.match.game_status == 'STOP' or self.match.game_status == None):
            commands = [
                {
                    'robot_id': r['robot_id'],
                    'color': r['color'],
                    'wheel_left': 0,
                    'wheel_right': 0
                } for r in commands
            ]

        self.comm.send(commands)

        #self.print_comm_passados_UFRBots(commands)

        if self.use_api:
            self.api.send_data(self.match)

    def print_frame_Ufrbots(self, frame):
        #print(frame)
        for k, v in frame.items():
            print(f"{k}: {v}")
            print("-"*130)
    
    def print_comm_passados_UFRBots(self, commands):
        print("Aqui é teste!!!")
        print(commands)
            
g = Game(config_file=args.config_file, env=args.env)

