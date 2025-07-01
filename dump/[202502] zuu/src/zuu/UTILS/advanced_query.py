

import typing


class AdvancedQuerySet:
    def __init__(self, query : 'AdvancedQuery', index : int):
        self.__query = query
        self.__index = index
        if self.__index not in self.__queryObjHandlers:
            self.__queryObjHandlers[self.__index] = []
        if self.__index not in self.__queryObjMatchers:
            self.__queryObjMatchers[self.__index] = (None, [])

    @property
    def __handlers(self) -> typing.List[typing.Callable]:
        return self.__query._AdvancedQuery__handlers[self.__index]
    
    @property
    def __matchers(self) -> typing.Tuple[bool, typing.List[typing.Callable]]:
        return self.__query._AdvancedQuery__matchers[self.__index]

    @property
    def __queryObjHandlers(self):
        return self.__query._AdvancedQuery__handlers
    
    @property
    def __queryObjMatchers(self):
        return self.__query._AdvancedQuery__matchers

    def remove(self):
        self.__queryObjHandlers.pop(self.__index)
        self.__queryObjMatchers.pop(self.__index)

    def handler(self):
        def decorator(func : typing.Callable):
            self.__handlers.append(func)
        return decorator

    def matcher(self, any : bool | None = None):
        def decorator(func : typing.Callable):
            
            flag, mlist = self.__queryObjMatchers[self.__index]
            if flag is not None and any is not None and any != flag:
                raise ValueError("Cannot reset matcher flag")
            if any is not None:
                self.__queryObjMatchers[self.__index] = (any, mlist)
            mlist.append(func)
            
        return decorator


class AQCtx:
    def __init__(self):
        self.result = None
        self.matchmap : typing.Dict[int, bool] = None
        self.cache = {}

class AdvancedQuery:
    def __init__(self):
        self.__counter = 0
        self.__handlers : typing.Dict[int, typing.List[typing.Callable]] = {}
        self.__matchers : typing.Dict[int, typing.Tuple[bool, typing.List[typing.Callable]]] = {}


    def __write_func_meta(self, func : typing.Callable):
        if 'ctx' in func.__code__.co_varnames:
            func.__ctx_required__ = True
        else:
            func.__ctx_required__ = False

    def handler(self):
        def decorator(func : typing.Callable):
            obj = AdvancedQuerySet(self, self.__counter)
            self.__write_func_meta(func)
            obj.handler()(func)
            self.__counter += 1
            return obj
        return decorator
    
    def matcher(self, any : bool | None = None):
        def decorator(func : typing.Callable):
            obj = AdvancedQuerySet(self, self.__counter)
            self.__write_func_meta(func)
            obj.matcher(any)(func)
            self.__counter += 1
            return obj
        return decorator
    
    def appendToAllHandler(self):
        def decorator(func : typing.Callable):
            for handler in self.__handlers.values():
                self.__write_func_meta(func)
                handler.append(func)
        return decorator

    def appendToAllMatcher(self):
        def decorator(func : typing.Callable):
            for flag, mlist in self.__matchers.values():
                self.__write_func_meta(func)
                mlist.append(func)
        return decorator

    def match(self, item, ctx : AQCtx):
        functionCache = {}
        ctx.matchmap = {}

        for id, (flag, mlist) in self.__matchers.items():

            allres = []
            isany = (flag is None or flag)

            for func in mlist:
                # resolve function res
                if func in functionCache:
                    res = functionCache[func]
                elif func.__ctx_required__:
                    res = func(ctx, item)
                    functionCache[func] = res
                else:
                    res = func(item)
                    functionCache[func] = res

                if isany and res:
                    # any
                    allres.append(res)
                    break
                else:
                    # all
                    if not res:
                        allres = []
                        break
                
                allres.append(res)

            if not allres:
                ctx.matchmap[id] = False
            elif isany:
                ctx.matchmap[id] = any(allres)
            else:
                ctx.matchmap[id] = all(allres)

        return ctx
    
    def handle(self,  ctx : AQCtx, item, **kwargs):
        if not ctx.matchmap:
            self.match(item, ctx)

        ctx.result = item
        for i, handler in self.__handlers.items():
            if ctx.matchmap[i]:
                for func in handler:
                    res = func(ctx, **kwargs)
                    if res:
                        ctx.result = res

