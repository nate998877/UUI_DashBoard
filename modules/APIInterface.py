class APIInterface:
  def __init__(self, *args):
    self.api_base = args[0]
    self.api_key = args[1]
    self.user_id = args[2]