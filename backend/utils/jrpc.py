_base_jrpc = {'jsonrpc': '2.0'}


def format_jrpc_response(data = None, error = None, id = None) -> dict:
    result = _base_jrpc.copy()
    if data:
        result['result'] = data
    elif error:
        result['error'] = error
    if id:
        result['id'] = id
    return result


def format_jrpc_request(method = None, params = None, id = None) -> dict:
    result = _base_jrpc.copy()
    if method:
        result['method'] = method
    elif params:
        result['params'] = params
    if id:
        result['id'] = id
    return result
