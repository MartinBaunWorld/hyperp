import os
import inspect
from zipfile import ZipFile
from functools import wraps
from traceback import format_exc
from datetime import datetime
import tempfile
from uuid import uuid4

from bottle import post, request, HTTPResponse, response, hook
from bottle import get as bottleget

from .utils import to_int, dumps, is_ip4, rmdir, mkdir
from .docs import DOCS
from enum import Enum

# TODO: rpc msg on errors


class InvalidForm(Exception):
    def __init__(self, param, msg):
        self.param = param 
        self.msg = msg 


def get_or_404(query):
    from peewee import DoesNotExist
    try:
        return query.get()
    except DoesNotExist as e:
        e_msg = e.__class__.__name__
        model_name = e_msg.split("DoesNotExist")[0] if len(e_msg.split("DoesNotExist")) > 0 else ""

        raise HTTPResponse(
            status=404,
            headers={"Content-Type": "application/json"},
            body=dumps(dict(msg=f"{model_name} Not Exist")),
        )


def _get_sig(func):

    signature = inspect.signature(func)
    params = []
    paramsDict = {}

    def get_type(p):
        if isinstance(p.annotation, type) and issubclass(p.annotation, Enum):
            return "enum"

        if p.annotation != p.empty:
            return p.annotation.__name__

        return "Unknown"

    def get_enums(p):
        if isinstance(p.annotation, type) and issubclass(p.annotation, Enum):
            return [item.value for item in p.annotation]
        
        return []

    # paramDict is exactly like params but just an dict instead of list
    # this is so validate can access it faster
    for name, p in signature.parameters.items():

        param = {
            "name": name,
            "docs": str(inspect.getdoc(func) if inspect.getdoc(func) else ""),
            "typeClass": p.annotation if p.annotation != inspect.Parameter.empty else "Any",
            "type": get_type(p),
            "enums": get_enums(p),
            "required": p.default == p.empty,
            "default": p.default if p.default != inspect.Parameter.empty else "N/A",
            "has_default": True if p.default != inspect.Parameter.empty else False,
        }
        params.append(param)
        paramsDict[param['name']] = param

    result = {
        "name": func.__name__,
        "params": params, 
        "paramsDict": paramsDict,
        "method": "post", 
        "func": func,
    }

    return result


def validate_and_call(func, sig, args):
    params = sig["paramsDict"]

    def get_enum_value(expected_type, name, value):
        # Check if the value matches any of the Enum members' values
        # Also checks for optimistcally converted ints
        int_value = to_int(value, None)

        for possible in expected_type:
            if value == possible.value:
                return value
            if int_value == possible.value:
                return int_value

        raise InvalidForm(name, f'Expected one of {[item.value for item in expected_type]}')

    for arg_name, arg_value in args.items():
        if arg_name not in params:
            # TODO log this error
            print(f'Unexpected argument {arg_name}={arg_value}')
            continue
        
        expected_type = params[arg_name]["typeClass"]
        
        if isinstance(expected_type, type) and issubclass(expected_type, Enum):
            args[arg_name] = get_enum_value(expected_type, arg_name, arg_value)
        elif expected_type != "Any" and not isinstance(arg_value, expected_type):
            raise InvalidForm(arg_name, f'Expected {expected_type.__name__} type')
    
    kwargs = {arg_name: args[arg_name] for arg_name in params if arg_name in args}

    # Check that all of them are there
    for param, param_details in params.items():
        if param not in args and param_details['required']:
            raise InvalidForm(param, 'Missing expected parameter')

    return func(**kwargs)


_apis = []


def _get_request_data():
    """
    Get request data depends on content type
    """
    content_type = request.get_header("Content-Type", "")
    # TODO: Should we accept also query parameters?
    try:
        if "application/json" in content_type:
            return request.json
        elif "multipart/form-data" in content_type:
            return request.forms
        else:
            return {}
    except:
        return {}


def get(path, checker=None):
    def decorator(func):
     
        @wraps(func)
        @bottleget(path)
        def wrapper(*args, **kwargs):
            checked = checker() if checker else ''
            if checked:
                response.status = 401
                return checked

            return func(*args, **kwargs)
        
        return wrapper
    return decorator


def rpc(path, checker=None):
    def decorator(func):
        sig = _get_sig(func)
        sig['path'] = path
        _apis.append(sig)

        @wraps(func)
        @post(path)
        def wrapper(*args, **kwargs):
            req_data = _get_request_data()        
            checked = checker() if checker else ''
            if checked:
                response.status = 401
                response.content_type = "application/json"

                return dict(msg=checked)
            try:
                response.status = 200
                response.content_type = "application/json"
                return validate_and_call(func, sig, req_data)
            except InvalidForm as e:
                response.status = 400
                response.content_type = "application/json"
                return {"msg": "Invalid Form", "param": e.param, "msg": e.msg}
            return dumps(res)

        return wrapper

    return decorator


def install_docs(app, path, base):
    # It is important that this is at init else it wont work

    apis = []

    # We do this because we need the base url
    # and we need to remove non-seriazable things
    # like func and parameter classes
    # It is slow, but only done everytime we render docs
    # so it's okay
    for api in _apis:
        params = []

        for p in api['params']:
            params.append(dict(
                name=p['name'],
                type=p['type'],
                enums=p['enums'],
                required=p['required'],
                default=p['default'],
                has_default=p['has_default'],
            ))

        apis.append(dict(
            name=api['name'],
            url=f"{base}{api['path']}",
            method=api['method'],
            docs=p['docs'],
            params=params,
        )) 

    @app.get(path)
    def mydocs_view():
        return DOCS.replace("APIS", dumps(apis)).replace("BASE", base)


def get_token():
    if "Authorization" in request.headers:
        return (
            request.
            headers["Authorization"].
            replace('bearer', '').
            replace('Bearer', '').
            replace('BEARER', '').
            strip()
        )
    elif 'token' in request.cookies:
        return request.cookies['token']
    elif "multipart/form-data" in str(request.content_type):
        return request.forms.get("authorization")

    return None


def install_deploy(path, output, key="", on_invalid_key=None, post_fun=None, merge=False):
    @post(path)
    def deployer():
        if key and request.headers.get("Authorization", "") != f"apitoken {key}":
            if on_invalid_key and callable(on_invalid_key):
                on_invalid_key()
            return "no access"

        with tempfile.TemporaryDirectory() as tmp_dir:
            zip_path = os.path.join(tmp_dir, f'deployer-{uuid4()}.zip')
            request.files.get("file").save(zip_path, overwrite=True)

            with ZipFile(zip_path, "r") as fh:
                if not merge:
                    rmdir(output)

                mkdir(output)
                fh.extractall(output)

            if post_fun and callable(post_fun):
                post_fun()

            request.body.close()
            # TODO remove file after deploy

        return "ok"


def install_cors(app, hosts):
    @app.route("/<:re:.*>", method="OPTIONS")
    def enable_cors_generic_route():
        """
        This route takes priority over all others. So any request with an OPTIONS
        """
        add_cors_headers()

    @app.hook("after_request")
    def enable_cors_after_request_hook():
        add_cors_headers()

    def add_cors_headers():
        cors_ok = request.headers["Host"] in hosts

        if cors_ok:
            response.headers["Access-Control-Allow-Origin"] = '*'
            response.headers[
                "Access-Control-Allow-Headers"
            ] = "Content-Type, Content-Length, Accept-Encoding, X-CSRF-Token, Authorization, accept, origin, Cache-Control, X-Requested-With, sentry-trace"
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers[
                "Access-Control-Allow-Methods"
            ] = "POST, HEAD,PATCH , OPTIONS, GET, PUT"


def _formatted_headers() -> str:
    """
    This function returns string of request headers
    that don't contain forbidden names.
    """
    forbidden_names = ("key", "auth", "secret", "cookie", "session")
    headers = "\n".join(
        [
            f"{key}: {value}"
            for key, value in request.headers.items()
            if key.lower() not in forbidden_names
        ]
    )

    if request.headers:
        return headers

    return ""


def get_ip():
    for header in ["X-Real-IP", "X-Forwarded-For", "X-Forwarded-Host"]:
        if header in request.headers:
            ip = request.headers[header]

            if ',' in ip:
                ip = ip.split(',')[0]

            if not is_ip4(ip):
                continue

            return ip

    return "127.0.0.1"


class ErrorHandler:
    def __init__(self, on_error):
        self._on_error = on_error

    def _format(self):
        msg = ""
        try:
            msg += f"{request.path} [{request.method}] {get_ip()}\n\n"
            msg += _formatted_headers()
        except: # noqa
            msg += (
                f"Failed to generate error message\n{format_exc()}\n\n"
                f"for the error:"
            )

        return msg

    def __call__(self, callback):
        def wrapper(*args, **kwargs):
            try:
                return callback(*args, **kwargs)
            except HTTPResponse as e:
                response.status = getattr(e, "status", None)
                response.headers.update(getattr(e, "headers", {}))
                return getattr(e, "body", {"msg": "Something went wrong"})
            except:  # noqa
                msg = f"{self._format()}\n\n{format_exc()}"
                self._on_error(msg)
                print(msg)
                return {"msg": "Internal Error"}

        return wrapper


def install_peewee(db):
    @hook("before_request")
    def _db_connect():
        db.connect(reuse_if_open=True)

    @hook("after_request")
    def _db_close():
        if not db.is_closed():
            db.close()


def cache(hours=None, days=None):
    if hours is None and days is None:
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate'
        return

    time = 0
    if hours:
        time += hours * 60 * 60

    if days:
        time += days * 60 * 60 * 24

    response.set_header('Cache-Control', f'public, max-age={time}')
