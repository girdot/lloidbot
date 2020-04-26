from discord.ext.commands import Bot
from datetime import datetime
import config
import turnipdb

client = Bot(command_prefix = config.BOT_PREFIX)

nm_help = "Returns everyones turnip prices for a given day.  Defaults to current day\nUsage: %snm [date: mm/dd/yy]" % config.BOT_PREFIX
nr_help = "Set your turnip prices based on time of day.  PST timezone only for now\nUsage: %snr <your price> [comment]" % config.BOT_PREFIX
nrd_help = "Set your turnip prices manually\nUsage:%snrd <your price> <date: mm/dd/yy> <am|pm> [comment]" % config.BOT_PREFIX

def smart_price_attributes():
    now = datetime.now()
    today_at_nine_am = now.replace(hour=8, minute=0)
    today_at_noon = now.replace(hour=12, minute=0)
    today_at_ten_pm = now.replace(hour=22, minute=0)

    if now.date().weekday() == 6:
        return True, False, now.date()
    elif (now < today_at_nine_am) or (now > today_at_ten_pm):
        return None, None, None
    elif now < today_at_noon:
        return False, True, now.date()
    else:
        return False, False, now.date()

@client.command(pass_context=True, aliases=['nm'], help=nm_help)
async def nipmarquee( context, arg="penis"):
    session = turnipdb.Session()
    try:
        date = datetime.strptime(arg.split(" ")[0], '%m/%d/%y').date()
    except:
        date = datetime.now().date()
    date_str = date.strftime("%A %m/%d/%y")
    prices = session.query( turnipdb.Price ).filter_by(\
            date = date ).all()
    user_map = {}
    for p in prices:
        if p.user.discord_id not in user_map:
            user_map[p.user.discord_id] = {'comment':"",'price':0,\
                    'am_price':0, 'am_comment':"", "pm_price":0,\
                    'pm_comment':"",\
                    'nick':context.message.guild.get_member(int(p.user.discord_id)).display_name}
        if date.weekday() == 6:
            user_map[p.user.discord_id]['comment'] = p.comment
            user_map[p.user.discord_id]['price'] = p.price
        elif p.is_am_price:
            user_map[p.user.discord_id]['am_comment'] = p.comment
            user_map[p.user.discord_id]['am_price'] = p.price
        else:
            user_map[p.user.discord_id]['pm_comment'] = p.comment
            user_map[p.user.discord_id]['pm_price'] = p.price
    if date.weekday() == 6:
        report = date_str + "\nuser,price,comment\n"
        report += "\n".join(["%s,%s,%s" % (u['nick'],u['price'],u['comment'])\
                for u in user_map.values()])
    else:
        report = date_str + "\nuser,am_price,am_comment,pm_price,pm_comment\n"
        report += "\n".join(["%s,%s,%s,%s,%s" % (u['nick'],u['am_price'],u['am_comment'],\
                u['pm_price'],u['pm_comment']) for u in user_map.values()])
    await context.message.channel.send(report)

@client.command(pass_context=True, aliases=['nrd'], help=nrd_help)
async def nipreportdetailed(context, *, arg):
    # See if they gave a proper int
    try:
        price = arg.split(" ")[0]
        date = datetime.strptime(arg.split(" ")[1], "%m/%d/%y").date()
        int( price )
        is_sell_price = (date.weekday() == 6)
        is_am_price = (arg.split(" ")[2].lower()=="am") 
    except:
        await context.message.channel.send("Invalid command. Check arguments.")
    comment = ' '.join(arg.split(" ")[3:])

    session = turnipdb.Session()
    # Check if the user exists in our table
    user_db = session.query(turnipdb.User).filter_by(\
            discord_id = context.message.author.id).first()
    if not user_db:
        user_db = turnipdb.User( discord_id = context.message.author.id )
        session.add( user_db )
        session.commit()

    # Check if price for this day is already in DB
    price_db = session.query(turnipdb.Price).filter_by(\
            date= date, is_am_price=is_am_price, user_id=user_db.id).first()
    if not price_db:
        price_db = turnipdb.Price( is_sell_price = is_sell_price,
                is_am_price = is_am_price, date = date, price = price,
                comment = comment, user_id = user_db.id )
    else:
        price_db.price = price
        price_db.comment = comment
    session.add( price_db )
    session.commit()
    await context.message.channel.send("Your price has been recorded")

@client.command(pass_context=True, aliases=['nr',], help=nr_help)
async def nipreport(context, *, arg):
    # See if they gave a proper int
    price = arg.split(" ")[0]
    comment = ' '.join(arg.split(" ")[1:])
    try:
        int(price)
    except ValueError:
        await context.message.channel.send('"%s" is not a valid price' % arg)
        return

    session = turnipdb.Session()
    # Check if the user exists in our table
    user_db = session.query(turnipdb.User).filter_by(\
            discord_id = context.message.author.id).first()
    if not user_db:
        user_db = turnipdb.User( discord_id = context.message.author.id )
        session.add( user_db )
        session.commit()

    is_sell_price, is_am_price, date = smart_price_attributes()
    if not date:
        await context.message.channel.send(\
                'Can\'t use smart add, stores are closed')

    # Check if price for this day is already in DB
    price_db = session.query(turnipdb.Price).filter_by(\
            date= date, is_am_price=is_am_price, user_id=user_db.id).first()
    if not price_db:
        price_db = turnipdb.Price( is_sell_price = is_sell_price,
                is_am_price = is_am_price, date = date, price = price,
                comment = comment, user_id = user_db.id )
    else:
        price_db.price = price
        price_db.comment = comment
    session.add( price_db )
    session.commit()
    await context.message.channel.send("Your price has been recorded")

@client.command(pass_context=True)
async def test(context, arg1, arg2):
    await context.message.channel.send('hola %s %s' % (arg1, arg2))

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

if __name__ == "__main__":
    client.run( config.DISCORD_BOT_TOKEN )
