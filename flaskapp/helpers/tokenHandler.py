from itsdangerous import URLSafeTimedSerializer

SECURITY_KEY = 'a1fdc94a9381ca2a2326c5c8b1c241e7ddfbd81848c42e984ccad88199e3264e'
SECURITY_PASSWORD_SALT = 'b38bb15d269c20674ef5db9bfc919f8fe91cbc79ca3a2490d7509b5c667897aa'

def generate_confirmation_token(data):
    serializer = URLSafeTimedSerializer(SECURITY_KEY)
    return serializer.dumps(data, SECURITY_PASSWORD_SALT)


def confirm_token(token, expiration=7200):
    serializer = URLSafeTimedSerializer(SECURITY_KEY)
    try:
        data = serializer.loads(
            token,
            salt=SECURITY_PASSWORD_SALT,
            max_age=expiration
        )
    except:
        return None
    return data