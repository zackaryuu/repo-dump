class ActionPair:
    """
    an abstract class with a generic call method

    """

    def __call__(self, *args, **kwargs):
        pass

class PreProcessPair(ActionPair):
    """
    a class to represent a pre-process action pair
    """
    pass

class PostProcessPair(ActionPair):
    """
    a class to represent a post-process action pair
    """

    def __init__(self, name : str, *args, rename_to : str =None) -> None:
        self.name = name
        self.args = args
        self.rename_to = rename_to

class ResParsePair(PostProcessPair):
    """
    defines a variable to be parsed from the response
    """

    def __call__(self, data : dict, target : dict):
        if self.name not in data:
            return None

        val = data.get(self.name)
       
        for arg in self.args:
            if callable(arg):
                val = arg(val)

        name = self.rename_to if self.rename_to is not None else self.name
        target[name] = val
    

