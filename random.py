import secrets

#随机生成18位数
def generate_number(length: int) -> str:
    return ''.join(secrets.choice('0123456789') for _ in range(length))
