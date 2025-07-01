from datetime import datetime, timezone
from habilBase.exceptions import HabilRateLimitExceeded, HabilRateLimitHalt
from habilBase.request.requester import RequesterResponse
from habilBase.request.case import RequestCase
from pydantic import BaseModel
from habilBase.logger import requestHandlerLogger as logger

class HabilRequestHandler:
    """

    
    """
    def __init__(self) -> None:
        self.allowed_max_requests = 30
        self.chances_left = 30
        self.rate_limit_reset = None
        self.throw_on_rate_limit = True
    
    def _parse_timestr(self, timestr:str):
        """
        convert 'Mon Oct 10 2022 20:29:54 GMT+0000 (Coordinated Universal Time)' to a datetime object 
        """
        # strip bracket
        timestr = timestr.split("GMT")[0]
        timestr = timestr.strip()
        
        datetimeobj = datetime.strptime(timestr, "%a %b %d %Y %H:%M:%S")
        
        # no need to replace tzinfo, would trigger datetime naive vs datetime aware error
        #datetimeobj = datetimeobj.replace(tzinfo=timezone.utc)
        
        
        return datetimeobj
    
    def __call__(self,
        case : RequestCase,
        *args,
        export : BaseModel = None,
        export_from_parsed : bool = False,
        export_from_data : bool =True,
        **kwargs
    ):
        self.chances_left -= 1
        
        if self.isRateLimited:
            raise HabilRateLimitHalt(self.chances_left)

        response : RequesterResponse = case(
            *args,
            export = export,
            export_from_parsed = export_from_parsed,
            export_from_data =export_from_data,
            **kwargs
        )

        res = response.res
        logger.debug(f"Request returned {res.status_code} status code")
        
        self.chances_left = int(res.headers.get("X-RateLimit-Remaining", 29))
        self.allowed_max_requests = int(res.headers.get("X-RateLimit-Limit", 30))
        
        timestr = res.headers.get("X-RateLimit-Reset", None)
        if timestr:
            self.rate_limit_reset = self._parse_timestr(timestr)
        else:
            logger.error("X-RateLimit-Reset header not found")
        
        if self.isRateLimited and self.throw_on_rate_limit:
            raise HabilRateLimitExceeded(self.rate_limit_reset)
        
        return response
        
    @property
    def isRateLimited(self):
        if self.rate_limit_reset is None:
            return False
        
        if self.chances_left <= 1:
            return True
        
        if self.rate_limit_reset < datetime.utcnow():
            return True
        
        return False
    
DEFAULT_HANDLER = HabilRequestHandler()