from lib.api import OSNAP

class OSnapApp:
    def __init__(self): 
      ## iterate over all the methods of the API class
      self.handler_registry = OSNAP.handler_registry
      self.check_api()

    def check_api(self):
      handler_types = set([ handler_type for ( handler_type, handler ) in self.handler_registry ])
      required_handler_types = set(["agents", "tools", "run"])
      missing_handler_types = required_handler_types - handler_types
      if len(missing_handler_types): 
        raise "Missing required handlers: " + str(missing_handler_types)    


# Usage Example 

# @OSNAP.agents()
# def my_apps_agent_handler():
#  return my_apps_agent_registry.get_agents(request)
# 
# myapp = OSnapApp()