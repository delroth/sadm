#!/usr/bin/env python3

import hashlib
import hmac
import os
import requests

CALLBACK_URL = 'https://dolphin-emu.org/download/new/'
DOWNLOADS_CREATE_KEY = open('/etc/dolphin-keys/downloads-create').read().strip()


def get_env_var(name):
    try:
        return os.environ[name].decode("utf-8")
    except KeyError:
        raise KeyError(f"{name} is missing from the environment") from None


if __name__ == '__main__':
    branch = get_env_var('BRANCH')
    shortrev = get_env_var('SHORTREV')
    hash = get_env_var('HASH')
    author = get_env_var('AUTHOR')
    description = get_env_var('DESCRIPTION')
    target_system = get_env_var('TARGET_SYSTEM')
    build_url = get_env_var('BUILD_URL')
    user_os_matcher = get_env_var('USER_OS_MATCHER')

    parts = [branch, shortrev, hash, author, description, target_system,
             build_url, user_os_matcher]

    msg = "|".join([str(len(part)) for part in parts] + parts)
    hm = hmac.new(DOWNLOADS_CREATE_KEY, msg.encode("utf-8"), hashlib.sha1)

    post_data = {
        'branch': branch,
        'shortrev': shortrev,
        'hash': hash,
        'author': author,
        'description': description,
        'target_system': target_system,
        'build_url': build_url,
        'user_os_matcher': user_os_matcher,
        'hmac': hm.hexdigest(),
    }

    r = requests.post(CALLBACK_URL, data=post_data)
    r.raise_for_status()
    print(r.text)
