from typing import List
from flask import abort
from flask_login import current_user

def permission_required(permissions: List):
    has_permission = False
    for permission in permissions:
        if permission in current_user.account_type:
            has_permission = True
    if not has_permission:
        abort(403)
