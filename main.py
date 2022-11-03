import asyncio, requests, discord
from datetime import datetime
from cryptoaddress import LitecoinAddress
from dateutil.relativedelta import relativedelta

import cogs.config as config
import cogs.strings as strings
import cogs.db as db
import cogs.utils as utils

db.initializeDB()

intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)

status_ = 0
role_ = ""
interval = 60 * 10

invites = {}


@client.event
async def on_ready():
    print(strings.LOGGED_IN.format(client.user))


@client.event
async def on_member_join(member):
    try:
        await member.send(strings.WELCOME_MESSAGE.format(member.mention))
        await member.send(config.WELCOME_VIDEO)
    except:
        pass

    # Getting the invites before the user joining
    # from our cache for this specific guild

    invites_before_join = invites[member.guild.id]

    # Getting the invites after the user joining
    # so we can compare it with the first one, and
    # see which invite uses number increased

    invites_after_join = await member.guild.invites()

    # Loops for each invite we have for the guild
    # the user joined.

    for invite in invites_before_join:
        # Now, we're using the function we created just
        # before to check which invite count is bigger
        # than it was before the user joined.

        if invite.uses < utils.find_invite_by_code(invites_after_join, invite.code).uses:

            # Now that we found which link was used,
            # we will print a couple things in our console:
            # the name, invite code used the the person
            # who created the invite code, or the inviter.

            try:
                db.insert_invites(invite.code, member.id)
            except:
                pass

            return


@client.event
async def on_message(message):
    global status_
    global role_
    if message.author.id != config.BOT_ID:
        try:
            for guild in client.guilds:
                break

            user = await guild.fetch_member(int(message.author.id))
            discord_id = str(user.id)

            if str(message.channel.type) == 'private' and message.author.id in [config.ADMIN_ID, config.DEV_ID]:
                if status_ != 0 and message.content == "cancel":
                    await message.channel.send(strings.BROADCAST_CANCELLED)
                    status_ = 0

                elif message.content == "!broadcast" and status_ == 0:
                    await message.channel.send(strings.ENTER_BROADCAST_ROLE)
                    status_ = 1

                elif status_ == 1:
                    role_ = message.content
                    if discord.utils.get(guild.roles, name=role_) is not None:
                        await message.channel.send(strings.ENTER_BROADCAST_MSG.format(role_))
                        status_ = 2
                    else:
                        await message.channel.send(strings.INVALID_ROLE)

                elif status_ == 2:
                    status_ = 0
                    for member in guild.members:
                        try:
                            user = await guild.fetch_member(member.id)
                            if discord.utils.get(user.roles, name=role_) is not None:
                                await user.send(strings.BORADCAST_BODY.format(user.mention, message.content))
                        except:
                            pass
                    await message.channel.send(strings.BROADCAST_SENT)

                if message.content.lower().startswith('!affiliate_stats '):
                    try:
                        discord_id = message.content.split()[1]
                        user = await guild.fetch_member(str(discord_id))
                        data = db.get_affiliate(discord_id)
                        total_paid = db.get_total_paid(discord_id)
                        to_pay = db.to_pay_user(discord_id)
                        total_paid_invites = db.get_total_paid_invites(discord_id)
                        overall_invites = db.get_total_invites(discord_id)
                        await message.channel.send(strings.AFFILIATE_STATS.format(user.name, data[1], total_paid_invites, overall_invites, to_pay, total_paid, data[3]))
                    except:
                        await message.channel.send(strings.AFFILIATE_NOT_ENROLLED.format(user.name))

                if message.content.lower().startswith('!resync '):
                    try:
                        discord_id = message.content.split()[1]

                        user = await guild.fetch_member(str(discord_id))
                        email = db.get_email_from_successful_txn(discord_id)

                        data = db.get_active_member(discord_id)
                        for row in data:
                            exp = row[1]
                            sub_date = row[2]

                        expiry_date = datetime.strptime(exp, config.DATE_FORMAT)
                        if expiry_date > datetime.now():
                            if sub_date == "1600":
                                role = discord.utils.get(guild.roles, name=config.ACTIVE_ROLE)
                                await user.add_roles(role)
                                annual_role = discord.utils.get(guild.roles, name=config.ANNUAL_SUB_ROLE)
                                await user.add_roles(annual_role)
                                channel = client.get_channel(config.ANNUAL_SUB)
                                plan = "yearly"
                            else:
                                role = discord.utils.get(guild.roles, name=config.ACTIVE_ROLE)
                                await user.add_roles(role)
                                plan = "monthly"

                            data = {
                                "email": email,
                                "activate": True,
                                "name": user.name,
                                "plan": plan
                                }

                            res = requests.post("https://us-central1-fx-social-license.cloudfunctions.net/purchase", json=data)

                            res = requests.get(f"http://harmonicpattern.com/whitelabel/subscribe?token={config.WHITE_LABEL_PRIVATE_TOKEN}&email={email}&name={user.name}")

                            await message.channel.send(strings.RESYNC_SUCCESS)
                        else:
                            await message.channel.send(strings.SUBSCRIPTION_ENDED.format(exp))

                    except Exception as e:
                        await message.channel.send(f"{strings.NOT_ACTIVE_MEMBER}\n\n{e}")


                if message.content.lower().startswith('!resync_yearly'):
                        data = db.get_all_anual_subs()
                        for row in data:
                            try:
                                discord_id = row[0]
                                user = await guild.fetch_member(int(discord_id))
                                email = db.get_email_from_successful_txn(discord_id)

                                data = {
                                    "email": email,
                                    "activate": True,
                                    "name": user.name,
                                    "plan": "yearly"
                                    }

                                res = requests.post("https://us-central1-fx-social-license.cloudfunctions.net/purchase", json=data)
                                await message.channel.send(strings.RESYNC_SUCCESS + " " + user.name)

                            except Exception as e:
                                await message.channel.send(f"{strings.NOT_ACTIVE_MEMBER}\n\n{e}")

            if str(message.channel.type) == 'private' and message.author.id != config.BOT_ID:
                if discord.utils.get(user.roles, name=config.ADMIN) is not None and message.content == "!export":
                    await message.channel.send(file=discord.File(config.DATABASE_NAME))

                elif message.content.lower() == '!enroll_affiliate':
                    try:
                        db.get_affiliate(discord_id)
                        await message.channel.send(strings.AFFILIATE_ALREADY_ENROLLED.format(user.mention))
                    except:
                        try:
                            db.insert_message_tracker(discord_id, "aff_1", "")

                            await message.channel.send(strings.ENTER_WALLET.format(user.mention))

                        except:
                            await message.channel.send(strings.ERROR_OCCURED.format(user.mention))

                elif message.content.lower() == '!modify_wallet':
                    try:
                        db.get_affiliate(discord_id)
                        db.insert_message_tracker(discord_id, "aff_2", "")
                        await message.channel.send(strings.ENTER_WALLET.format(user.mention))
                    except:
                        await message.channel.send(strings.AFFILIATE_NOT_ENROLLED_2.format(user.mention))

                elif message.content.lower() == '!affiliate_stats':
                    try:
                        data = db.get_affiliate(discord_id)
                        total_paid = db.get_total_paid(discord_id)
                        to_pay = db.to_pay_user(discord_id)
                        total_paid_invites = db.get_total_paid_invites(discord_id)
                        overall_invites = db.get_total_invites(discord_id)
                        await message.channel.send(strings.AFFILIATE_STATS.format(user.mention, data[1], total_paid_invites, overall_invites, to_pay, total_paid, data[3]))
                    except:
                        await message.channel.send(strings.AFFILIATE_NOT_ENROLLED_2.format(user.mention))

                elif message.content.lower() == '!subscribe':
                    try:
                        db.insert_message_tracker(discord_id, "sub_1", "")
                        await message.channel.send(strings.SUB_MSG.format(user.mention))
                    except:
                        await message.channel.send(strings.ERROR_OCCURED.format(user.mention))

                elif str(message.channel.type) == 'private' and message.author.id == config.ADMIN_ID and message.content.lower() == '!pay_affiliates':
                    cursor = db.get_aff_to_pay()
                    await message.channel.send(f">>> {db.count_aff_to_pay()} affiliates to be paid")
                    if db.count_aff_to_pay() == 0:
                        await message.channel.send(strings.NO_AFF_TO_PAY.format(user.mention))
                    for row in cursor:
                        await message.channel.send(f">>> ...")
                        try:

                            time_ = row[0]
                            discord_id = row[1]
                            amount_btc = row[2]
                            invitee_id = row[3]
                            wallet = db.get_wallet(discord_id)
                            payee = await guild.fetch_member(int(discord_id))
                            invitee = await guild.fetch_member(int(invitee_id))
                            time_stamp = datetime.now().strftime(config.DATE_FORMAT)

                            await message.channel.send(f">>> Starting payment process for {payee.name}")

                            data = f"version=1&cmd=create_withdrawal&amount={amount_btc}&currency=" + config.CURRENCY + f"&add_tx_fee=1&auto_confirm=1&address={wallet}&key={config.API_PUBLIC_KEY}&format=json"

                            header = {'Content-Type': 'application/x-www-form-urlencoded',
                                    'HMAC': utils.generate_signature(data)}

                            res = requests.post("https://www.coinpayments.net/api.php", data=data, headers=header)

                            if res.json()["error"] != "ok":
                                await message.channel.send(strings.AFF_PAY_ERROR.format(user.mention, payee.name, amount_btc, res.json()['error']))
                            else:
                                db.delete_aff_to_pay(time_)
                                await message.channel.send(strings.AFF_PAY_SUCCESS.format(user.mention, payee.name, amount_btc))
                                await payee.send(strings.AFF_PAY_REC.format(payee.mention, amount_btc, invitee.name))
                                db.insert_aff_paid(time_stamp, discord_id, amount_btc, invitee_id)
                                
                        except:
                            pass


                else:
                    try:
                        if db.get_message_tracker(discord_id) == 'sub_2':
                            try:
                                package = db.get_message_tracker_package(discord_id)
                                db.delete_message_tracker(discord_id)

                                if package == "#1":
                                    fee_usd = "165"
                                elif package == "#2":
                                    fee_usd = "450"
                                elif package == "#3":
                                    fee_usd = "1600"

                                email = message.content.lower()

                                data = f"version=1&cmd=create_transaction&amount={fee_usd}&currency1=USD&currency2=" + config.CURRENCY + f"&buyer_email={email}&key={config.API_PUBLIC_KEY}&format=json"

                                header = {'Content-Type': 'application/x-www-form-urlencoded',
                                        'HMAC': utils.generate_signature(data)}

                                res = requests.post("https://www.coinpayments.net/api.php", data=data, headers=header)

                                result = res.json()['result']
                                txn_id = result['txn_id']
                                address = result['address']
                                timeout = result['timeout']
                                checkout_url = result['checkout_url']
                                amount = result['amount']
                                status_url = result['status_url']
                                qrcode_url = result['qrcode_url']

                                time_stamp = datetime.now().strftime(config.DATE_FORMAT)

                                db.insert_pending_transactions(txn_id, discord_id, amount, fee_usd, time_stamp, email)

                                await message.channel.send(strings.CHECKOUT_MSG.format(user.mention, checkout_url, amount, address, utils.display_time(timeout), status_url))
                                await message.channel.send(qrcode_url)

                            except Exception as e:
                                await message.channel.send(strings.SUB_ERROR.format(user.mention, e))
                    except:
                        pass

                    try:
                        if db.get_message_tracker(discord_id) == 'aff_2':
                            try:
                                if message.content.lower() == 'skip':
                                    db.delete_message_tracker(discord_id)
                                    await message.channel.send(strings.PROCESS_TERMINATED.format(user.mention))
                                else:
                                    try:
                                        address = message.content
                                        ltc_address = LitecoinAddress(address)
                                        db.update_wallet(address, discord_id)
                                        db.delete_message_tracker(discord_id)
                                        await message.channel.send(strings.WALLET_UPDATED_SUCCESS.format(user.mention))

                                    except:
                                        await message.channel.send(strings.INVALID_WALLET_ENTERED.format(user.mention))
                            except:
                                await message.channel.send(f">>> {user.mention} Error occurred")
                    except:
                        pass

                    try:
                        if db.get_message_tracker(discord_id) == 'aff_1':
                            try:
                                if message.content.lower() == 'skip':
                                    channel = client.get_channel(config.MAIN_CHANNEL)
                                    link = await channel.create_invite(unique = True)
                                    link = link.url
                                    time_stamp = datetime.now().strftime(config.DATE_FORMAT)
                                    db.delete_message_tracker(discord_id)
                                    db.insert_into_affiliate(discord_id, link, "", time_stamp)
                                    await message.channel.send(strings.AFF_ENROLLED.format(user.mention, link))

                                else:
                                    try:
                                        address = message.content
                                        ltc_address = LitecoinAddress(address)

                                        channel = client.get_channel(config.MAIN_CHANNEL)
                                        link = await channel.create_invite(unique = True)
                                        link = link.url
                                        time_stamp = datetime.now().strftime(config.DATE_FORMAT)
                                        db.insert_into_affiliate(discord_id, link, address, time_stamp)
                                        db.delete_message_tracker(discord_id)
                                        await message.channel.send(strings.AFF_ENROLLED.format(user.mention, link))

                                    except:
                                        await message.channel.send(strings.INVALID_WALLET_ENTERED.format(user.mention))
                            except:
                                await message.channel.send(strings.INVALID_COMMAND.format(user.mention))
                    except Exception as e:
                        user = await guild.fetch_member(config.DEV_ID)
                        #await user.send(f"```Error processing message \n{e}```")

                    try:
                        if db.get_message_tracker(discord_id) == 'sub_1' and message.content.lower() in ["#1", "#2", "#3"]:
                            try:
                                choice = message.content
                                db.update_message_tracker(discord_id, "sub_2", choice)

                                await message.channel.send(strings.ENTER_EMAIL_ADRESS.format(user.mention))
                            except:
                                await message.channel.send(strings.INVALID_COMMAND.format(user.mention))

                    except Exception as e:
                        user = await guild.fetch_member(config.DEV_ID)
                        #await user.send(f"```Error processing message \n{e}```")

        except Exception as e:
            user = await guild.fetch_member(config.DEV_ID)
            #await user.send(f"```Error processing message (main) \n{e}```")


async def user_metrics_background_task():
    await client.wait_until_ready()
    while True:
        global interval

        for guild in client.guilds:
            try:
                invites[guild.id] = await guild.invites()
            except:
                pass

        if interval >= 60 * 10:
            interval = 0
            for member in guild.members:
                try:
                    db.insert_user_details(member.id, member.name, str(member.avatar_url))
                except:
                    pass

        data = db.get_all_affiliate()
        for row in data:
            try:
                discord_id = row[0]
                user = await guild.fetch_member(int(discord_id))
                total_paid_invites = db.get_total_paid_invites(discord_id)
                overall_invites = db.get_total_invites(discord_id)
                try:
                    invited_level = int(row[6])
                    paid_level = int(row[7])

                    if overall_invites >= 1000:
                        if invited_level != 1000:
                            level = "1000"
                            admin = await guild.fetch_member(config.ADMIN_ID)
                            await admin.send(strings.INVITED_MILESTONE_ADMIN.format(user.name, user.id, level))
                            await user.send(strings.INVITED_MILESTONE_USER.format(level))
                            dev = await guild.fetch_member(config.DEV_ID)
                            await dev.send(strings.INVITED_MILESTONE_ADMIN.format(user.name, user.id, level))
                            db.update_affiliate_invited_level(discord_id, level)

                    elif overall_invites >= 250:
                        if invited_level != 250:
                            level = "250"
                            admin = await guild.fetch_member(config.ADMIN_ID)
                            await admin.send(strings.INVITED_MILESTONE_ADMIN.format(user.name, user.id, level))
                            await user.send(strings.INVITED_MILESTONE_USER.format(level))
                            dev = await guild.fetch_member(config.DEV_ID)
                            await dev.send(strings.INVITED_MILESTONE_ADMIN.format(user.name, user.id, level))
                            db.update_affiliate_invited_level(discord_id, level)

                    elif overall_invites >= 100:
                        if invited_level != 100:
                            level = "100"
                            admin = await guild.fetch_member(config.ADMIN_ID)
                            await admin.send(strings.INVITED_MILESTONE_ADMIN.format(user.name, user.id, level))
                            await user.send(strings.INVITED_MILESTONE_USER.format(level))
                            dev = await guild.fetch_member(config.DEV_ID)
                            await dev.send(strings.INVITED_MILESTONE_ADMIN.format(user.name, user.id, level))
                            db.update_affiliate_invited_level(discord_id, level)


                    if total_paid_invites >= 1000:
                        if paid_level != 1000:
                            level = "1000"
                            admin = await guild.fetch_member(config.ADMIN_ID)
                            await admin.send(strings.PAID_MILESTONE_ADMIN.format(user.name, user.id, level))
                            await user.send(strings.PAID_MILESTONE_USER.format(level))
                            dev = await guild.fetch_member(config.DEV_ID)
                            await dev.send(strings.PAID_MILESTONE_ADMIN.format(user.name, user.id, level))
                            db.update_affiliate_paid_level(discord_id, level)

                    elif total_paid_invites >= 250:
                        if paid_level != 250:
                            level = "250"
                            admin = await guild.fetch_member(config.ADMIN_ID)
                            await admin.send(strings.PAID_MILESTONE_ADMIN.format(user.name, user.id, level))
                            await user.send(strings.PAID_MILESTONE_USER.format(level))
                            dev = await guild.fetch_member(config.DEV_ID)
                            await dev.send(strings.PAID_MILESTONE_ADMIN.format(user.name, user.id, level))
                            db.update_affiliate_paid_level(discord_id, level)

                    elif total_paid_invites >= 100:
                        if paid_level != 100:
                            level = "100"
                            admin = await guild.fetch_member(config.ADMIN_ID)
                            await admin.send(strings.PAID_MILESTONE_ADMIN.format(user.name, user.id, level))
                            await user.send(strings.PAID_MILESTONE_USER.format(level))
                            dev = await guild.fetch_member(config.DEV_ID)
                            await dev.send(strings.PAID_MILESTONE_ADMIN.format(user.name, user.id, level))
                            db.update_affiliate_paid_level(discord_id, level)
                except:
                    level = "0"
                    db.update_affiliate_invited_level(discord_id, level)
                    db.update_affiliate_paid_level(discord_id, level)

                db.update_affiliate_total_pinvitee(discord_id, overall_invites)
                db.update_affiliate_total_paid(discord_id, total_paid_invites)
            except:
                pass

        data = db.get_all_pending_transactions()

        for row in data:
            try:
                txn_id = row[0]
                discord_id = row[1]
                amount_btc = row[2]
                fee_usd = row[3]
                email = row[5]

                user = await guild.fetch_member(int(discord_id))

                data = f"version=1&cmd=get_tx_info&txid={txn_id}&key={config.API_PUBLIC_KEY}&format=json"

                header = {'Content-Type': 'application/x-www-form-urlencoded',
                        'HMAC': utils.generate_signature(data)}

                res = requests.post("https://www.coinpayments.net/api.php", data=data, headers=header)
                result = res.json()['result']
                status = result['status']
                status_text = result['status_text']

                if status < 0:
                    time_stamp = datetime.now().strftime(config.DATE_FORMAT)
                    db.insert_failed_transaction(txn_id, discord_id, amount_btc, fee_usd, status_text, email, time_stamp)
                    await user.send(strings.TRANSACTION_FAILED.format(user.mention, txn_id, status_text))
                    db.delete_from_pending_transaction(txn_id)

                elif status >= 100:
                    time_stamp = datetime.now().strftime(config.DATE_FORMAT)
                    db.insert_successful_transaction(txn_id, discord_id, amount_btc, fee_usd, status_text, email, time_stamp)

                    if fee_usd == "165":
                        months = 1
                        channel = client.get_channel(config.MONTHLY_SUB_CHANNEL)
                        await channel.send(f"{email}")
                        role = discord.utils.get(guild.roles, name=config.ACTIVE_ROLE)
                        plan = "monthly"
                    elif fee_usd == "450":
                        channel = client.get_channel(config.MONTHLY_SUB_CHANNEL)
                        await channel.send(f"{email} - 3 MONTHS")
                        months = 3
                        role = discord.utils.get(guild.roles, name=config.ACTIVE_ROLE)
                        plan = "monthly"
                    elif fee_usd == "1600":
                        months = 12
                        role = discord.utils.get(guild.roles, name=config.ACTIVE_ROLE)
                        annual_role = discord.utils.get(guild.roles, name=config.ANNUAL_SUB_ROLE)
                        await user.add_roles(annual_role)
                        channel = client.get_channel(config.ANNUAL_SUB)
                        await channel.send(f"{email}")
                        plan = "yearly"

                    await user.add_roles(role)

                    try:
                        expiry = db.get_expiry_date(discord_id)
                        expiry_date = datetime.strptime(expiry, config.DATE_FORMAT)
                        date_after_month = expiry_date + relativedelta(months=months)
                        exp = date_after_month.strftime(config.DATE_FORMAT)
                    except:
                        date_after_month = datetime.today() + relativedelta(months=months)
                        exp = date_after_month.strftime(config.DATE_FORMAT)

                    db.insert_active_member(discord_id, exp, fee_usd, "0")

                    try:
                        status = db.get_sub_status(discord_id)
                        db.update_sub_status(discord_id, int(status) + months)

                        inviter = db.get_inviter(discord_id)
                        super_ = db.find_super(inviter)
                        #gets the inviter of the inviter provided it's not a super affiliate
                        downstream = db.find_downstream(inviter)

                        if super_ != "1":
                            time_stamp = datetime.now().strftime(config.DATE_FORMAT)
                            db.insert_affiliate_to_pay(time_stamp, super_, str(float(amount_btc)*0.2), discord_id)

                        if downstream != "1":
                            time_stamp = datetime.now().strftime(config.DATE_FORMAT)
                            db.insert_affiliate_to_pay(time_stamp, downstream, str(float(amount_btc)*0.05), discord_id)

                        db.insert_affiliate_to_pay(time_stamp, inviter, str(float(amount_btc)*0.45), discord_id)

                    except Exception as e:
                        user_ = await guild.fetch_member(config.DEV_ID)
                        await user_.send(strings.AFFILIATE_PAYMENT_ADDING_ERROR.format(e))

                    await user.send(strings.PAYMENT_CONFIRMED.format(user.mention, exp))
                    #admin_user = await guild.fetch_member(int(admin_id))
                    #await admin_user.send(f">>> {admin_user.mention} {user.name} subscription has been activated, and they have been given the 'member' role")

                    email = db.get_email_from_successful_txn(discord_id)
                    channel = client.get_channel(config.ZAPPIER_SUB)
                    await channel.send(f"{email}")

                    db.delete_from_pending_transaction(txn_id)

                    data = {
                        "email": email,
                        "activate": True,
                        "name": user.name,
                        "plan": plan
                        }

                    res = requests.post("https://us-central1-fx-social-license.cloudfunctions.net/purchase", json=data)

                    res = requests.get(f"http://harmonicpattern.com/whitelabel/subscribe?token={config.WHITE_LABEL_PRIVATE_TOKEN}&email={email}&name={user.name}")

            except Exception as e:
                user = await guild.fetch_member(config.DEV_ID)
                await user.send(strings.PENDING_TXN_ERROR.format(e))


        data = db.get_all_active_members()

        for row in data:
            try:
                discord_id = row[0]
                exp = row[1]
                expiry_date = datetime.strptime(exp, config.DATE_FORMAT)
                try:
                    notify = int(row[3])
                except:
                    notify = 0

                user = await guild.fetch_member(int(discord_id))
                time_left = expiry_date - datetime.now()

                if expiry_date < datetime.now():
                    time_passed = datetime.now() - expiry_date

                    if time_passed.days >= 5:
                        role = discord.utils.get(guild.roles, name=config.ACTIVE_ROLE)
                        await user.remove_roles(role)
                        role = discord.utils.get(guild.roles, name=config.ANNUAL_SUB_ROLE)
                        await user.remove_roles(role)

                        db.delete_active_members(discord_id)

                        await user.send(f">>> {user.mention} You have been disconnected. Reply with **!subscribe** to reactivate your subscription")
                        #admin_user = await guild.fetch_member(int(admin_id))
                        #await admin_user.send(f">>> {user.name} subscription has ended, and their 'member' role has been revoked")

                        email = db.get_email_from_successful_txn(discord_id)

                        channel = client.get_channel(config.ZAPPIER_UNSUB)
                        await channel.send(f"{email}")

                        data = {
                            "email": email,
                            "activate": False
                            }

                        res = requests.post("https://us-central1-fx-social-license.cloudfunctions.net/purchase", json=data)

                        res = requests.get(f"http://harmonicpattern.com/whitelabel/unsubscribe?token={config.WHITE_LABEL_PRIVATE_TOKEN}&email={email}")


                    elif time_passed.days in [1, 2, 3, 4] and time_passed.seconds <= 10:
                        await user.send(strings.SUB_ENDED.format(user.mention))

                elif time_left.days == 5 and notify < 1:
                    await user.send(strings.SUB_EXP_NOTICE.format(user.mention, exp))
                    db.update_notify_in_active_members("1", discord_id)

                elif time_left.days == 3 and notify < 2:
                    await user.send(strings.SUB_EXP_NOTICE.format(user.mention, exp))
                    db.update_notify_in_active_members("2", discord_id)

                elif time_left.days == 1 and notify < 3:
                    await user.send(strings.SUB_EXP_NOTICE.format(user.mention, exp))
                    db.update_notify_in_active_members("3", discord_id)

            except Exception as e:
                pass
                #user = await guild.fetch_member(dev_id)
                #await user.send(f"```{e}```")

        interval += 1
        await asyncio.sleep(1)


client.loop.create_task(user_metrics_background_task())
client.run(config.DISCORD_TOKEN)

