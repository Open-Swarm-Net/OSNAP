handler_registry = set()
class OSNAP:
  """OSNAP API Decorators"""
  def agents():
      def decorator(func):
        def wrapper(*args, **kwargs):
          print("Before calling " + func.__name__)
          func(*args, **kwargs)
          print("After calling " + func.__name__)

        handler_registry.add(("agents", wrapper))    
        return wrapper
      return decorator


  def tools(fn):
      # takes the fn and registers it
      pass

  # # TODO: Add the rest of the required endpoints


# Usage Example 
# @OSNAP.agents()
# def my_apps_get_agents(request):
#   return my_apps_agent_registry.get_agents(request)

