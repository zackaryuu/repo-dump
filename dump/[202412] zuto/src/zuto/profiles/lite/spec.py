import logging
import os
import typing

from pydantic import Field
from zuto.builtin.spec import JobSpec, PostSpec
from zuto.core.ctx import ZutoCtx
from zuto.core.part import ZutoPart

class LiteSpec(ZutoPart):
    name : str
    description : typing.Optional[str] = None
    env : typing.Optional[typing.Dict[str, str]] = None
    when : typing.Optional[typing.Union[str, int]] = None
    jobs : typing.Dict[str, JobSpec] = Field(default_factory=dict)
    post : typing.Optional[typing.Union[PostSpec, str]] = None

    def _on_execute(self, ctx: ZutoCtx, blocking: int = -1):
        logging.info(f"Executing {self.name}")
        if self.description:
            logging.info(f"Description:\n{self.description}")
        
        if self.env:
            for k, v in self.env.items():
                os.environ[k] = v

        try:
            for jobname, job in self.jobs.items():
                logging.info(f"Running job {jobname}")
                ctx.meta.rebase()
                ctx.meta.push(jobname)
                job._on_execute(ctx, blocking)
                
        except Exception as e:
            ctx.flags.set("ERROR")
            ctx.meta.push(success=False)
            if not self.post or (isinstance(self.post, PostSpec) and not self.post.error):
                raise e
        finally:
            if self.post:
                self._execute_child("post", ctx)    
    