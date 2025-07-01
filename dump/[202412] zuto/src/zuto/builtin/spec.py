import logging
import typing

from pydantic import Field
from zuto.core.part import ZutoPart
from zuto.utils.flow import run_oneliner

class PostSpec(ZutoPart):
    error : typing.Optional[str] = None
    success : typing.Optional[str] = None
    fail : typing.Optional[str] = None
    __block_auto__ = True

    def _on_execute(self, ctx, blocking: int = -1):
        err = "ERROR" in ctx.flags.current
        if err and self.error:
            run_oneliner(ctx, self.error) 
                    
        if "FAIL" in ctx.flags.current and self.fail:
            run_oneliner(ctx, self.fail) 
                    
        if not err and self.success:
            run_oneliner(ctx, self.success)

        ret = 1
        if any(flag in ctx.flags.current for flag in ["SKIP", "EXIT", "GOTO"]):
            ret = 0
            
        return ret

class JobSpec(ZutoPart):
    pre : typing.Optional[str] = None
    post : typing.Optional[typing.Union[PostSpec, str]] = None
    cond : typing.Optional[str] = None
    flags : typing.Optional[typing.List[str]] = Field(default_factory=list)
    steps : typing.List[dict] = Field(default_factory=list)

    def _on_execute(self, ctx, blocking: int = -1):
        if self.cond and not ctx.eval(self.cond):
            logging.info(f"Skipping job {ctx.current_job.name} because cond is not met")
            return

        if self.pre:
            run_oneliner(ctx, self.pre)

        ctx.meta.push(success=True)
        for step in self.steps:
            try:
                ctx._invoke(step)
            except Exception as e:
                ctx.flags.set("ERROR")
                logging.error(f"Error in job {ctx.current_job}: {e}")
                if not self.post or (isinstance(self.post, PostSpec) and not self.post.error):
                    ctx.meta.push(success=False)
                    raise e
            finally:
                ctx._reconcile_flags()
                if not self._execute_child("post", ctx):
                    ctx.meta.push(success=False)
                    break
                
                