# -*- coding: utf-8 -*-
# @Time    : 17-8-24 下午2:53
# @Author  : Wang Chao


from django.conf import settings


def ldap_connection(username, password):
    conn = ldap.initialize(settings.LDAP_PROVIDER_URL)
    try:
        conn.simple_bind_s('uid={0},{1}'.format(username, settings.LDAP_BASE_DC), password)
        return 1
    except:
        return 0
