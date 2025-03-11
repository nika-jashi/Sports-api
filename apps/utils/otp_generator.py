import math as m
import random as r


def OTP_generator(password_reset=False) -> str: # noqa
    string = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    OTP: str = ""  # noqa
    var_length = len(string)
    if password_reset:
        for i in range(6):
            OTP += string[m.floor(r.random() * var_length)]
    else:
        for i in range(5):
            OTP += string[m.floor(r.random() * var_length)]
    return OTP