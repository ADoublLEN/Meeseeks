from typing import List, Dict, Any


class BaseModel():
    """
    This is a base model class. It should be sub-classed and have at least a generate method.
    Our framework will call the generate method to generate the output.
    """
    def __init__(self, **kwargs):
        pass

    async def generate(self, messages: List[Dict[str, Any]], **kwargs) -> str:
        """
        Generate a response from your specific model. Only need to return the raw completion text.
        :param messages:
        :param args:
        :param kwargs:
        :return:
        """
        raise NotImplementedError

