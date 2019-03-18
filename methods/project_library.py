import ntplib


def get_time_offset():
    c = ntplib.NTPClient()
    response = c.request('au.pool.ntp.org', version=3)
    return response.offset
