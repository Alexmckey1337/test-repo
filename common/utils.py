from typing import Tuple


def encode_month(year: int, month: int) -> int:
    """
    Encode month of year to count of months from start of gregorian calendar

    :param year: year number
    :param month: month number
    :return: encode month
    """
    return year * 12 + month


def decode_month(month: int) -> Tuple[int, int]:
    """
    Decode (count of months from start of gregorian calendar) to tuple of year and month number

    :param month: decode month
    :return: tuple (year, month)
    """
    return (month - 1) // 12, month % 12 or 12