import sys
import unittest
import logging

from habilBase.logger import logger, requestHandlerLogger

GLOBAL_ENABLER = False

class testcase_template(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        global GLOBAL_ENABLER
        if not GLOBAL_ENABLER:
            logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
            GLOBAL_ENABLER = True
        return super().setUpClass()
    
    def setUp(self):
        pass
    
    def _internal_toggle_logger(self, logger : logging.Logger, on : bool = True, lv : int = logging.DEBUG):
        if not on:
            logger.setLevel(logging.CRITICAL)
            return
        
        logger.setLevel(lv)
    
    def toggle_logger(self, on: bool = True, lv: int = logging.DEBUG):
        return self._internal_toggle_logger(logger, on, lv)
        
    def toggle_requestHandlerLogger(self, on: bool = True, lv: int = logging.DEBUG):
        return self._internal_toggle_logger(requestHandlerLogger, on, lv)
            
        