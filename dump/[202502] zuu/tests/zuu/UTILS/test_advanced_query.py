import pytest
from zuu.UTILS.advanced_query import AdvancedQuery, AQCtx

@pytest.fixture
def setup_query():
    query = AdvancedQuery()
    
    @query.matcher()
    def match_a(string : str):
        return string.startswith("dir(") and string.endswith(")")
        
    @match_a.handler()
    def handle_a(ctx : AQCtx, cache : dict, **kwargs):
        result = cache[ctx.result[4:-1]]
        ctx.result = result

    @query.matcher(any=False)
    def match_b(string : str):
        return string.startswith("file(") and string.endswith(")")
    
    @match_b.handler()
    def handle_b(ctx : AQCtx, cache : dict, **kwargs):
        result = cache[ctx.result[5:-1]]
        ctx.result = result

    @query.matcher(any=False)
    def match_c(string : str):
        return string.startswith("func(") and string.endswith(")")
    
    @match_c.handler()
    def handle_c(ctx : AQCtx, cache : dict, **kwargs):
        result = cache[ctx.result[5:-1]]
        ctx.result = result

    return query

def test_match_a(setup_query : AdvancedQuery):
    query = setup_query
    cache = {'test_dir': 'directory_result'}
    ctx = AQCtx()
    
    query.handle(ctx,'dir(test_dir)', cache=cache)
    assert ctx.result == 'directory_result'

def test_match_b(setup_query : AdvancedQuery):
    query = setup_query
    cache = {'test_file': 'file_result'}
    ctx = AQCtx()
    
    query.handle(ctx,'file(test_file)', cache=cache)
    assert ctx.result == 'file_result'

def test_match_c(setup_query : AdvancedQuery):
    query = setup_query
    cache = {'test_func': 'function_result'}
    ctx = AQCtx()
    
    query.handle(ctx,'func(test_func)', cache=cache)
    assert ctx.result == 'function_result'




        