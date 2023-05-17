handler_registry = set()
class OSNAP:
  """OSNAP API Decorators

  Example usage:
  @OSNAP.agents()
  def my_apps_get_agents(request):
    return my_apps_agent_registry.get_agents(request)
  """
  def agents():
      def decorator(func):
        def wrapper(*args, **kwargs):
          print("Before calling " + func.__name__)
          #
          # OSNAPRequest = *args["request"]
          func(*args, **kwargs)
          print("After calling " + func.__name__)

        handler_registry.add(("agents", wrapper))    
        return wrapper
      return decorator
  
  def run():
      def decorator(func):
        def wrapper(*args, **kwargs):
          print("Before calling " + func.__name__)
          #
          # OSNAPRequest = *args["request"]
          print("REQUEST: ", args.get("request"))
          func(*args, **kwargs)
          print("After calling " + func.__name__)

        handler_registry.add(("run", wrapper))    
        return wrapper
      return decorator


  def tool_invoke():
      def decorator(func):
        def wrapper(*args, **kwargs):
          print("Before calling " + func.__name__)
          #
          # OSNAPRequest = *args["request"]
          func(*args, **kwargs)
          print("After calling " + func.__name__)

        handler_registry.add(("tool_invoke", wrapper))    
        return wrapper
      return decorator

  # # TODO: Add the rest of the required endpoints
