#!/usr/bin/env python3

import hashlib
import hmac
import os
import requests


def get_env_var(name):
    try:
        return os.environ[name]
    except KeyError:
        raise KeyError(f"{name} is missing from the environment") from None


def main():
    key_filename = os.environ.get('DOWNLOADS_CREATE_KEY',
                                  '/etc/dolphin-keys/downloads-create')
    callback_url = os.environ.get('CALLBACK_URL',
                                  'https://dolphin-emu.org/download/new/')

    branch = get_env_var('BRANCH')
    shortrev = get_env_var('SHORTREV')
    hash = get_env_var('HASH')
    author = get_env_var('AUTHOR')
    description = get_env_var('DESCRIPTION')
    target_system = get_env_var('TARGET_SYSTEM')
    build_url = get_env_var('BUILD_URL')
    user_os_matcher = get_env_var('USER_OS_MATCHER')

    with open(key_filename, 'rb') as f:
        key = f.read().strip()

    parts = [branch, shortrev, hash, author, description, target_system,
             build_url, user_os_matcher]

    msg = "|".join([str(len(part)) for part in parts] + parts)
    hm = hmac.new(key, msg.encode("utf-8"), hashlib.sha1)

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

    r = requests.post(callback_url, data=post_data)
    r.raise_for_status()
    print(r.text)


if __name__ == '__main__':
    main()
