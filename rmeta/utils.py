__author__ = "Alan Viars"
from decimal import Decimal
from django.conf import settings



TRUE_LIST = [1, "1", "true", "True", "TRUE", "YES", "Yes", "yes", True]
FALSE_LIST = [0, "0", "False", "FALSE", "false", "NO", "No", "no", False]


def bool_env(env_val):
    """ check for boolean values """

    if env_val:
        if env_val in TRUE_LIST:
            return True
        if env_val in FALSE_LIST:
            return False
        return env_val
    else:
        if env_val in FALSE_LIST:
            return False
        return


def int_env(env_val):
    """ convert to integer from String """

    return int(Decimal(float(env_val)))


def IsAppInstalled(target_app=None):
    """ Is an app in INSTALLED_APPS """

    if target_app:
        if target_app in settings.INSTALLED_APPS:
            return True
    # Return False if target_app is not defined
    # or target_app is not found in INSTALLED_APPS
    return False