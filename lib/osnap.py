import json
import enum
import time
import uuid
import requests
from typing import Callable, Dict, Union, List
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat, PrivateFormat, NoEncryption
import rsa

class OSNAPApp:
    required_handler_types = set([
        "agents", 
        # "tools",
        # "run"
    ])

    def __init__(self, agents: list): 
      ## iterate over all the methods of the API class
      # TODO: Figure out the best time to check the API      
      # self.check_api()

      # each agent registers itself with the app
      for agent in agents:
        print(agent.name, agent.description)
        OSNAPAgent.register(agent)

    def check_api(self):
      handler_types = set([ handler_type for ( handler_type, handler ) in self.handler_registry ])
      missing_handler_types = self.required_handler_types - handler_types
      if len(missing_handler_types): 
        raise Exception("Missing required handlers: " + str(missing_handler_types))


class Scope(enum.Enum):
    PUBLIC = "public"
    PRIVATE = "private"

    
class OSNAPResponse:
    def __init__(self, payload: Dict):
        self.payload = json.dumps(payload)
        self.signature = None

class OSNAPError:
    def __init__(self, message: str):
        self.payload = json.dumps({"error": message})
        self.signature = None

class SignatureUtil:
    @staticmethod
    def generate_key_pair():
        ( public_key, private_key) = rsa.new_keys(512, poolsize=8)
        private_pem = private_key.private_bytes(Encoding.PEM, PrivateFormat.PKCS8, NoEncryption())
        public_pem = private_key.public_key().public_bytes(Encoding.PEM, PublicFormat.SubjectPublicKeyInfo)
        return private_pem, public_pem

    @staticmethod
    def sign_data(private_key_pem, data):
        private_key = serialization.load_pem_private_key(private_key_pem, None)
        signature = private_key.sign(data.encode(), padding.PKCS1v15(), hashes.SHA256())
        return signature

    @staticmethod
    def verify_signature(public_key_pem, data, signature):
        public_key = serialization.load_pem_public_key(public_key_pem)
        try:
            public_key.verify(signature, data.encode(), padding.PKCS1v15(), hashes.SHA256())
            return True
        except Exception as e:
            return False

class OSNAPRequest:
    def __init__(self, caller_agent_id: str, request_type: str, task_name: str = None, priority: int = 0, request_metadata: Dict = None):
        self.caller_agent_id = caller_agent_id
        self.request_type = request_type
        self.task_name = task_name
        self.priority = priority
        self.request_metadata = request_metadata or {}
        self.timestamp = time.time()
        self.payload = json.dumps({
            "caller_agent_id": self.caller_agent_id,
            "request_type": self.request_type,
            "task_name": self.task_name,
            "priority": self.priority,
            "request_metadata": self.request_metadata,
            "timestamp": self.timestamp
        })
        self.signature = None

class OSNAPAgent:
    def __init__(
        self, 
        name: str, 
        description: str, 
        scope: Scope, 
        info_endpoint: str,
        invoke_endpoint: str,
        registry_url: str,
        #registry : Callable,
        add_agent_function: Callable,
        id: str = str(uuid.uuid4()),
        using_rsa: bool = False, 
        tools: List = []
    ):
        self.id = id 
        self.name = name
        self.description = description
        self.scope = scope
        self.info_endpoint = info_endpoint
        self.invoke_endpoint = invoke_endpoint
        self.registry_url = registry_url
        self.add_agent_function = add_agent_function
        #self.register = register
        self.using_rsa = using_rsa
        self.tools = tools or []

        if using_rsa:
            # Generate a key pair
            self.private_key_pem, self.public_key_pem = SignatureUtil.generate_key_pair()

        # Call the register method with required arguments
       # self.register(agent_id=self.id, name=self.name, description=self.description, invoke_endpoint=self.invoke_endpoint, tools=self.tools, scope=self.scope)


    def register(self) -> None:
        data = {
            "agent_id": self.id,
            "name": self.name,
            "description": self.description,
            "scope": self.scope.value,
            "info_endpoint": self.info_endpoint
            #"public_key": self.public_key_pem
        }
        response = requests.post(f"{self.registry_url}/register", json=data)
        if response.status_code == 200:
            self.add_agent_function(self.id,self.name,self.description,self.info_endpoint,self.tools,self.scope.value)
            print("Agent registered successfully.")
        else:
            print("Failed to register agent:", response.text)

    def unregister(self) -> None:
        data = {
            "agent_id": self.id,
        }
        response = requests.post(f"{self.registry_url}/unregister", json=data)
        if response.status_code == 200:
            print("Agent unregistered successfully.")
        else:
            print("Failed to unregister agent:", response.text)

    def update_tools_on_registry(self) -> None:
        data = {
            "agent_id": self.id,
            "tools": self.handlers['get_tools']()
        }
        response = requests.post(f"{self.registry_url}/update_tools", json=data)
        if response.status_code == 200:
            print("Agent tools updated successfully.")
        else:
            print("Failed to update agent tools:", response.text)

    def send_request_to_agent(self, destination_agent: 'OSNAPAgent', request: OSNAPRequest) -> Union[OSNAPResponse, OSNAPError]:
        if self.handlers['request_validation'](request) and \
           SignatureUtil.verify_signature(destination_agent.public_key_p_key_pem, request.payload, request.signature):
            response = destination_agent.process_request(request)
            if self.handlers['response_validation'](response) and \
               SignatureUtil.verify_signature(destination_agent.public_key_pem, response.payload, response.signature):
                return response
            else:
                return OSNAPError("Invalid response signature")
        else:
            return OSNAPError("Invalid request signature")

    def process_request(self, request: OSNAPRequest) -> Union[OSNAPResponse, OSNAPError]:
        if request.request_type == "info":
            handler = self.handlers.get('info')
            if handler:
                return handler(request)
            else:
                return OSNAPError("Info handler not found")
        elif request.request_type == "task":
            handler = self.handlers.get(request.task_name)
            if handler:
                return handler(request)
            else:
                return OSNAPError("Task handler not found")
        else:
            return OSNAPError("Invalid request type")

    def create_osnap_request(self, request_type: str, task_name: str = None, priority: int = 0, request_metadata: Dict = None) -> OSNAPRequest:
        request = OSNAPRequest(caller_agent_id=self.id, request_type=request_type, task_name=task_name, priority=priority, request_metadata=request_metadata)
        signature = SignatureUtil.sign_data(self.private_key_pem, request.payload)
        request.signature = signature
        return request

    def create_osnap_response(self, payload: Dict) -> OSNAPResponse:
        response = OSNAPResponse(payload=payload)
        signature = SignatureUtil.sign_data(self.private_key_pem, response.payload)
        response.signature = signature
        return response

    def create_osnap_error(self, message: str) -> OSNAPError:
        error = OSNAPError(message)
        signature = SignatureUtil.sign_data(self.private_key_pem, error.payload)
        error.signature = signature
        return error

class OSNAPTool:
    def __init__(self, name: str, description: str, tool_id: str, invoke_endpoint: str, invoke_required_params={}, invoke_optional_params: List[str]=[]):
        self.name = name
        self.description = description
        self.tool_id = tool_id
        self.invoke_endpoint = invoke_endpoint
        self.invoke_required_params = invoke_required_params
        self.invoke_optional_params = invoke_optional_params

# Usage Example 

# @OSNAP.agents()
# def my_apps_agent_handler():
#  return my_apps_agent_registry.get_agents(request)
# 
# myapp = OSnapApp()