
import cogs.config as config

WELCOME_MESSAGE = ">>> {} Welcome to FX Social Membership 🤗🤗🤗 \n\nReply with **!subscribe** to subscribe to one of our packages or reply with **!enroll_affiliate** to enroll for affilliate program and start earning real money"

LOGGED_IN = "We have logged in as {}"

BROADCAST_CANCELLED = ">>> Broadcast cancelled"

ENTER_BROADCAST_ROLE = ">>> Enter the role you want to send a boradcast to"

ENTER_BROADCAST_MSG = ">>> Enter the message you want to broadcast to members with role '{}'  \nEnter cancel to stop broadast"

INVALID_ROLE = ">>> The role you entered does not exist, check the spelling and enter again (Note that role is case sensitive) \nEnter cancel to stop broadast"

BORADCAST_BODY = ">>> {} you have a message from Admin \n\n{}"

BROADCAST_SENT = ">>> Broadcast sent"

AFFILIATE_STATS = ">>> {} \nInvite link : {} \nTotal paid invites : {}\nTotal invites : {}\nPending payment (" + config.CURRENCY + ") : {}\nTotal amount earned (" + config.CURRENCY + ") : {}\nDate joined : {}"

AFFILIATE_NOT_ENROLLED = ">>> {} The user with the ID is not enrolled as an affiliate"

AFFILIATE_ALREADY_ENROLLED = ">>> {} You are already enrolled as an affiliate. \n\nType **!affiliate_stats** to see your affiliate details"

ENTER_WALLET = ">>> {} Enter a valid " + config.CURRENCY + " wallet address to receive your referral bonuses. \nEnter **skip** to proceed without adding wallet"

ERROR_OCCURED = ">>> {} Error occurred. Please try again"

NOT_ACTIVE_MEMBER = ">>> User you entered is not an active member"

SUBSCRIPTION_ENDED = ">>> User subscription already ended on {}"

RESYNC_SUCCESS = ">>> Resync successful"

AFFILIATE_NOT_ENROLLED_2 = ">>> {} You are not enrolled as an affiliate, type **!enroll_affiliate** to enroll"

SUB_MSG = ">>> {} Reply with the package you want to subscribe to (e.g. **#1**)\n(**Note that only " + config.CURRENCY + " payment is allowed**) \n\n   #1 - Monthly plan. $165 (1 month) \n   #2 - Quarterly plan. $450 (3 months) \n   #3 - Yearly plan. $1600 (12 months)"

NO_AFF_TO_PAY = ">>> {} There is currently no pending affiliate to be paid"

AFF_PAY_ERROR = ">>> {} Error occurred \nUser : {}\nAmount (" + config.CURRENCY + ") : {}\nMessage : {}"

AFF_PAY_SUCCESS = ">>> {} Affiliate payment successful \nUser : {}\nAmount (BTC) : {}"

AFF_PAY_REC = ">>> {} Affiliate payment received \nAmount (BTC) : {} (Note that transaction fee will be deducted) \nInvitee : {}"

CHECKOUT_MSG = ">>> {} Please proceed to checkout here {}. \n\nYou are to pay a total of **{} " + config.CURRENCY + "** into this wallet **{}** before {}. \n\nYou can check the status of your transaction here {}. \n\nYour subscription will be automatically activated once your transation is confirmed"

SUB_ERROR = ">>> {} Error occurred - {}\nPlease start over by replying with **!subscribe**"

PROCESS_TERMINATED = ">>> {} Process terminated"

WALLET_UPDATED_SUCCESS = ">>> {} Wallet updated successfully"

INVALID_WALLET_ENTERED = ">>> {} The wallet address you entered is invalid. Please enter a valid wallet address or enter **skip**"

AFF_ENROLLED = ">>> {} You are now enrolled as an affiliate, your invite link is {}. \n\nInvite members to our server using your link and you'll earn a commision when they subscribe\n\nType **!affiliate_stats** to see your affiliate details \n\nType **!modify_wallet** to modify your BTC wallet "

INVALID_COMMAND = ">>> {} Invalid command"

ENTER_EMAIL_ADRESS = ">>> {} Reply with your email address \n\n**Please enter a valid email address. This will enable us send you a notice if you underpay or need a refund** "

INVITED_MILESTONE_ADMIN =  "```Heyyy, {} [{}] has reached a new milestone, they have reached {} total invited members```"

INVITED_MILESTONE_USER = "```Heyyy, you have reached a new milestone, you have reached {} total invited members```"

PAID_MILESTONE_ADMIN =  "```Heyyy, {} [{}] has reached a new milestone, they have reached {} total paying members```"

PAID_MILESTONE_USER = "```Heyyy, you have reached a new milestone, you have reached {} total paying members```"

TRANSACTION_FAILED = ">>> {} Transaction with id {} has failed. \n\nReason - {}"

AFFILIATE_PAYMENT_ADDING_ERROR = "```Error while adding affiliate payment \n{}```"

PAYMENT_CONFIRMED = ">>> {} Congratulations, your payment has been confirmed and your subscription has been activated. Your subscription is valid till {} \n\nBrand new? You will receive your login details within 2-5 minutes via email\n\nhttps://www.fx-social.com/"

PENDING_TXN_ERROR = "```Error processing pending transaction \n{}```"

SUB_EXP_NOTICE = "{} Your subscription will expire by {}, reply with **!subscribe** to extend your subscription"

SUB_ENDED = "{} Your subscription subscription has ended. reply with **!subscribe** to extend your subscription"

