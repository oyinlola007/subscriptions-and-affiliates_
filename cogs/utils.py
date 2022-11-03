import hmac, hashlib

import cogs.config as config

def find_invite_by_code(invite_list, code):
    # Simply looping through each invite in an
    # invite list which we will get using guild.invites()
    for inv in invite_list:
        # Check if the invite code in this element
        # of the list is the one we're looking for
        if inv.code == code:
            # If it is, we return it.
            return inv

def generate_signature(data):
    key = config.API_SECRET # Defined as a simple string.
    key_bytes= bytes(key , 'latin-1') # Commonly 'latin-1' or 'utf-8'
    data_bytes = bytes(data, 'latin-1') # Assumes `data` is also a string.
    return hmac.new(key_bytes, data_bytes , hashlib.sha512).hexdigest()

def display_time(seconds, granularity=4):
    intervals = (
    ('weeks', 604800),  # 60 * 60 * 24 * 7
    ('days', 86400),    # 60 * 60 * 24
    ('hours', 3600),    # 60 * 60
    ('minutes', 60),
    ('seconds', 1),
    )

    result = []

    for name, count in intervals:
        value = seconds // count
        if value:
            seconds -= value * count
            if value == 1:
                name = name.rstrip('s')
            result.append("{} {}".format(value, name))
    return ', '.join(result[:granularity])

