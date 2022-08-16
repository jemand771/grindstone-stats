from flask import abort

import re


def verify_token(token):
    if token is None:
        return abort(401)
    if re.match("^[0-9a-f]{32}$", token):
        return token
    return abort(403)
