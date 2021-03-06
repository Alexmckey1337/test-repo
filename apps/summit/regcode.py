from common.exception import InvalidRegCode

REG_CODE_SALT = '1324'


def encode_reg_code(profile_id: int) -> str:
    code = '{}{}'.format(str(profile_id), REG_CODE_SALT)

    return hex(int(code)).split('x')[-1]


def is_valid_code(code: str) -> bool:
        return code.endswith(REG_CODE_SALT)


def decode_reg_code(code: str) -> int:
    try:
        code = int('0x' + code, 0)
    except ValueError:
        raise InvalidRegCode
    if not is_valid_code(str(code)):
        raise InvalidRegCode
    return int(str(code)[:-4])
