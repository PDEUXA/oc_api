from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_token(plain_token, hashed_token):
    return pwd_context.verify(plain_token, hashed_token)


def get_token_hash(plain_token):
    return pwd_context.hash(plain_token)
