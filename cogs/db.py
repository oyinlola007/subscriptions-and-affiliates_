import sqlite3
from datetime import datetime

import cogs.config as config

conn = sqlite3.connect(config.DATABASE_NAME)

def initializeDB():
    try:
        conn.execute('''CREATE TABLE AFFILIATE
                 (DISCORD_ID TEXT PRIMARY KEY NOT NULL,
                 AFFILIATE_LINK TEXT,
                 BTC_WALLET TEXT,
                 DATE_JOINED TEXT,
                 TOTAL_INVITED TEXT,
                 TOTAL_PAID TEXT,
                 INVITED_LEVEL TEXT,
                 PAID_LEVEL TEXT);''')
    except:
        pass

    try:
        conn.execute('''CREATE TABLE INVITES
                 (INVITEE TEXT PRIMARY KEY NOT NULL,
                 INVITER TEXT,
                 SUB_STATUS TEXT,
                 TIME_STAMP TEXT);''')
    except:
        pass

    try:
        conn.execute('''CREATE TABLE ACTIVE_MEMBERS
                 (DISCORD_ID TEXT PRIMARY KEY NOT NULL,
                 EXPIRY_DATE TEXT,
                 SUB_TYPE TEXT,
                 NOTIFY TEXT);''')
    except:
        pass

    try:
        conn.execute('''CREATE TABLE PENDING_TRANSACTIONS
                 (TRANSACTION_ID TEXT PRIMARY KEY NOT NULL,
                 DISCORD_ID TEXT,
                 AMOUNT_BTC TEXT,
                 AMOUNT_USD TEXT,
                 TIME_STAMP TEXT,
                 EMAIL TEXT);''')
    except:
        pass

    try:
        conn.execute('''CREATE TABLE SUCCESSFUL_TRANSACTIONS
                 (TRANSACTION_ID TEXT PRIMARY KEY NOT NULL,
                 DISCORD_ID TEXT,
                 AMOUNT_BTC TEXT,
                 AMOUNT_USD TEXT,
                 STATUS TEXT,
                 EMAIL TEXT,
                 TIME_STAMP TEXT);''')
    except:
        pass

    try:
        conn.execute('''CREATE TABLE FAILED_TRANSACTIONS
                 (TRANSACTION_ID TEXT PRIMARY KEY NOT NULL,
                 DISCORD_ID TEXT,
                 AMOUNT_BTC TEXT,
                 AMOUNT_USD TEXT,
                 STATUS TEXT,
                 EMAIL TEXT,
                 TIME_STAMP TEXT);''')
    except:
        pass


    try:
        conn.execute('''CREATE TABLE AFFILIATE_TO_PAY
                 (TIME_STAMP TEXT,
                 DISCORD_ID TEXT,
                 AMOUNT_BTC TEXT,
                 INVITEE_ID TEXT);''')
    except:
        pass


    try:
        conn.execute('''CREATE TABLE AFFILIATE_PAID
                 (TIME_STAMP TEXT,
                 DISCORD_ID TEXT,
                 AMOUNT_BTC TEXT,
                 INVITEE_ID TEXT);''')
    except:
        pass


    try:
        conn.execute('''CREATE TABLE MESSAGE_TRACKER
                 (DISCORD_ID TEXT PRIMARY KEY NOT NULL,
                 STATUS TEXT,
                 PACKAGE TEXT);''')
    except:
        pass

    try:
        conn.execute('''CREATE TABLE SUPER_AFFILIATES
                 (DISCORD_ID TEXT PRIMARY KEY NOT NULL);''')
    except:
        pass

    try:
        conn.execute('''CREATE TABLE USER_DETAILS
                 (DISCORD_ID TEXT PRIMARY KEY NOT NULL,
                 USERNAME TEXT,
                 AVATAR_URL TEXT);''')
    except:
        pass

    conn.commit()


def find_super(invitee):
    super_affiliates = []
    data = conn.execute(f"SELECT DISCORD_ID from SUPER_AFFILIATES")
    for row in data:
        super_affiliates.append(row[0])
    try:
        inviter = conn.execute(f"SELECT INVITER from INVITES where INVITEE='{invitee}'").fetchone()[0]
    except:
        return "1"
    if int(inviter) in super_affiliates:
        return inviter
    else:
        return find_super(inviter)

def find_downstream(invitee):
    super_affiliates = []
    data = conn.execute(f"SELECT DISCORD_ID from SUPER_AFFILIATES")
    for row in data:
        super_affiliates.append(row[0])

    try:
        inviter = conn.execute(f"SELECT INVITER from INVITES where INVITEE='{invitee}'").fetchone()[0]
    except:
        return "1"

    if int(inviter) not in super_affiliates:
        return inviter
    else:
        return "1"


def insert_invites(code, discord_id):
    inviter_id = conn.execute(f"SELECT DISCORD_ID from AFFILIATE where AFFILIATE_LINK='https://discord.gg/{code}'").fetchone()[0]

    time_stamp = datetime.now().strftime(config.DATE_FORMAT)
    sqlite_insert_with_param = """INSERT INTO 'INVITES'
    ('INVITEE', 'INVITER', 'SUB_STATUS', 'TIME_STAMP')
    VALUES (?, ?, ?, ?);"""
    data_tuple = (discord_id, inviter_id, "0", time_stamp)
    conn.execute(sqlite_insert_with_param, data_tuple)
    conn.commit()

def insert_message_tracker(discord_id, status, package):
    sqlite_insert_with_param = """INSERT OR REPLACE INTO 'MESSAGE_TRACKER'
    ('DISCORD_ID', 'STATUS', 'PACKAGE')
    VALUES (?, ?, ?);"""
    data_tuple = (discord_id, status, package)
    conn.execute(sqlite_insert_with_param, data_tuple)
    conn.commit()

def insert_aff_paid(time_stamp, discord_id, amount_btc, invitee_id):
    sqlite_insert_with_param = """INSERT INTO 'AFFILIATE_PAID'
    ('TIME_STAMP', 'DISCORD_ID', 'AMOUNT_BTC', 'INVITEE_ID')
    VALUES (?, ?, ?, ?);"""
    data_tuple = (time_stamp, discord_id, amount_btc, invitee_id)
    conn.execute(sqlite_insert_with_param, data_tuple)
    conn.commit()

def insert_pending_transactions(transaction_id, discord_id, amount_btc, amount_usd, time_stamp, email):
    sqlite_insert_with_param = """INSERT INTO 'PENDING_TRANSACTIONS'
    ('TRANSACTION_ID', 'DISCORD_ID', 'AMOUNT_BTC', 'AMOUNT_USD', 'TIME_STAMP', 'EMAIL')
    VALUES (?, ?, ?, ?, ?, ?);"""
    data_tuple = (transaction_id, discord_id, amount_btc, amount_usd, time_stamp, email)
    conn.execute(sqlite_insert_with_param, data_tuple)
    conn.commit()

def insert_into_affiliate(discord_id, link, wallet, time_stamp):
    sqlite_insert_with_param = """INSERT INTO 'AFFILIATE'
    ('DISCORD_ID', 'AFFILIATE_LINK', 'BTC_WALLET', 'DATE_JOINED')
    VALUES (?, ?, ?, ?);"""
    data_tuple = (discord_id, link, wallet, time_stamp)
    conn.execute(sqlite_insert_with_param, data_tuple)
    conn.commit()

def insert_failed_transaction(txn_id, discord_id, amount_btc, fee_usd, status_text, email, time_stamp):
    sqlite_insert_with_param = """INSERT INTO 'FAILED_TRANSACTIONS'
    ('TRANSACTION_ID', 'DISCORD_ID', 'AMOUNT_BTC', 'AMOUNT_USD', 'STATUS', 'EMAIL', 'TIME_STAMP')
    VALUES (?, ?, ?, ?, ?, ?, ?);"""
    data_tuple = (txn_id, discord_id, amount_btc, fee_usd, status_text, email, time_stamp)
    conn.execute(sqlite_insert_with_param, data_tuple)
    conn.commit()

def insert_successful_transaction(txn_id, discord_id, amount_btc, fee_usd, status_text, email, time_stamp):
    sqlite_insert_with_param = """INSERT INTO 'SUCCESSFUL_TRANSACTIONS'
    ('TRANSACTION_ID', 'DISCORD_ID', 'AMOUNT_BTC', 'AMOUNT_USD', 'STATUS', 'EMAIL', 'TIME_STAMP')
    VALUES (?, ?, ?, ?, ?, ?, ?);"""
    data_tuple = (txn_id, discord_id, amount_btc, fee_usd, status_text, email, time_stamp)
    conn.execute(sqlite_insert_with_param, data_tuple)
    conn.commit()

def insert_active_member(discord_id, exp, fee_usd, status):
    sqlite_insert_with_param = """INSERT OR REPLACE INTO 'ACTIVE_MEMBERS'
    ('DISCORD_ID', 'EXPIRY_DATE', 'SUB_TYPE', 'NOTIFY')
    VALUES (?, ?, ?, ?);"""
    data_tuple = (discord_id, exp, fee_usd, status)
    conn.execute(sqlite_insert_with_param, data_tuple)
    conn.commit()

def insert_affiliate_to_pay(time_stamp, discord_id, amount, invitee_id):
    sqlite_insert_with_param = """INSERT INTO 'AFFILIATE_TO_PAY'
    ('TIME_STAMP', 'DISCORD_ID', 'AMOUNT_BTC', 'INVITEE_ID')
    VALUES (?, ?, ?, ?);"""
    data_tuple = (time_stamp, discord_id, amount, invitee_id)
    conn.execute(sqlite_insert_with_param, data_tuple)
    conn.commit()

def insert_user_details(discord_id, username, avatar_url):
    sqlite_insert_with_param = """INSERT OR REPLACE INTO 'USER_DETAILS'
    ('DISCORD_ID', 'USERNAME', 'AVATAR_URL')
    VALUES (?, ?, ?);"""
    data_tuple = (discord_id, username, avatar_url)
    conn.execute(sqlite_insert_with_param, data_tuple)
    conn.commit()

def get_affiliate(discord_id):
    return conn.execute(f"SELECT * from AFFILIATE where DISCORD_ID='{discord_id}'").fetchone()[0]

def get_all_affiliate():
    return conn.execute(f"SELECT * from AFFILIATE")

def get_all_anual_subs():
    return conn.execute(f"SELECT * from ACTIVE_MEMBERS WHERE SUB_TYPE = '1600'")

def get_all_pending_transactions():
    return conn.execute(f"SELECT * from PENDING_TRANSACTIONS")

def get_total_paid(discord_id):
    return conn.execute(f"SELECT SUM(CAST(AMOUNT_BTC AS FLOAT)) from AFFILIATE_PAID where DISCORD_ID='{discord_id}'").fetchone()[0]

def to_pay_user(discord_id):
    return conn.execute(f"SELECT SUM(CAST(AMOUNT_BTC AS FLOAT)) from AFFILIATE_TO_PAY where DISCORD_ID='{discord_id}'").fetchone()[0]

def get_total_paid_invites(discord_id):
    return conn.execute(f"SELECT COUNT(INVITEE) from INVITES where SUB_STATUS != '0' AND INVITER = '{discord_id}'").fetchone()[0]

def get_total_invites(discord_id):
    return conn.execute(f"SELECT COUNT(INVITEE) from INVITES where INVITER = '{discord_id}'").fetchone()[0]

def get_aff_to_pay():
    return conn.execute(f"SELECT * from AFFILIATE_TO_PAY")

def get_all_active_members():
    return conn.execute(f"SELECT * from ACTIVE_MEMBERS")

def get_active_member(discord_id):
    return conn.execute(f"SELECT * from ACTIVE_MEMBERS where DISCORD_ID='{discord_id}'")

def get_inviter(invitee):
    return conn.execute(f"SELECT INVITER from INVITES where INVITEE = '{invitee}'").fetchone()[0]

def get_sub_status(discord_id):
    return conn.execute(f"SELECT SUB_STATUS from INVITES where INVITEE = '{discord_id}'").fetchone()[0]

def count_aff_to_pay():
    return conn.execute(f"SELECT COUNT(TIME_STAMP) from AFFILIATE_TO_PAY").fetchone()[0]

def get_wallet(discord_id):
    return conn.execute(f"SELECT BTC_WALLET from AFFILIATE where DISCORD_ID='{discord_id}'").fetchone()[0]

def get_email_from_successful_txn(discord_id):
    return conn.execute(f"SELECT EMAIL from SUCCESSFUL_TRANSACTIONS where DISCORD_ID='{discord_id}'").fetchone()[0]

def delete_aff_to_pay(time_stamp):
    conn.execute(f"DELETE from AFFILIATE_TO_PAY where TIME_STAMP='{time_stamp}'")
    conn.commit()

def get_message_tracker(discord_id):
    return conn.execute(f"SELECT STATUS from MESSAGE_TRACKER where DISCORD_ID='{discord_id}'").fetchone()[0]

def get_message_tracker_package(discord_id):
    return conn.execute(f"SELECT PACKAGE from MESSAGE_TRACKER where DISCORD_ID='{discord_id}'").fetchone()[0]

def get_expiry_date(discord_id):
    return conn.execute(f"SELECT EXPIRY_DATE from ACTIVE_MEMBERS where DISCORD_ID='{discord_id}'").fetchone()[0]

def delete_message_tracker(discord_id):
    conn.execute(f"DELETE from MESSAGE_TRACKER where DISCORD_ID='{discord_id}'")
    conn.commit()

def delete_from_pending_transaction(txn_id):
    conn.execute(f"DELETE from PENDING_TRANSACTIONS where TRANSACTION_ID='{txn_id}'")
    conn.commit()

def delete_active_members(discord_id):
    conn.execute(f"DELETE from ACTIVE_MEMBERS where DISCORD_ID='{discord_id}'")
    conn.commit()

def update_wallet(address, discord_id):
    conn.execute(f"UPDATE AFFILIATE set BTC_WALLET = '{address}' where DISCORD_ID = '{discord_id}'")
    conn.commit()

def update_message_tracker(discord_id, status, package):
    conn.execute(f"UPDATE MESSAGE_TRACKER set STATUS = '{status}', PACKAGE = '{package}' where DISCORD_ID = '{discord_id}'")
    conn.commit()

def update_notify_in_active_members(notify, discord_id):
    conn.execute(f"UPDATE ACTIVE_MEMBERS set NOTIFY = '{notify}' where DISCORD_ID = '{discord_id}'")
    conn.commit()

def update_affiliate_invited_level(discord_id, level):
    conn.execute(f"UPDATE AFFILIATE set INVITED_LEVEL = '{level}' where DISCORD_ID = '{discord_id}'")
    conn.commit()

def update_affiliate_paid_level(discord_id, level):
    conn.execute(f"UPDATE AFFILIATE set PAID_LEVEL = '{level}' where DISCORD_ID = '{discord_id}'")
    conn.commit()

def update_affiliate_total_paid(discord_id, total_paid_invites):
    conn.execute(f"UPDATE AFFILIATE set TOTAL_PAID = '{str(total_paid_invites)}' where DISCORD_ID = '{discord_id}'")
    conn.commit()

def update_affiliate_total_pinvitee(discord_id, overall_invites):
    conn.execute(f"UPDATE AFFILIATE set TOTAL_INVITED = '{str(overall_invites)}' where DISCORD_ID = '{discord_id}'")
    conn.commit()

def update_sub_status(discord_id, sub_status):
    conn.execute(f"UPDATE INVITES set SUB_STATUS = '{sub_status}' where INVITEE = '{discord_id}'")
    conn.commit()

def get_email_from_successful_txn(discord_id):
    return conn.execute(f"SELECT EMAIL from SUCCESSFUL_TRANSACTIONS where DISCORD_ID='{discord_id}'").fetchone()[0]