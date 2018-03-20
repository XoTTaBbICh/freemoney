#!/usr/bin/env python
# -*- coding: utf-8 -*-
import telebot
from telebot import types
import messages
import db_api
import time
import functions
import random
import ast
import settings
import flask
import threading
from yandex_money import api


# import logging
# log = logging.getLogger('werkzeug')
# log.setLevel(logging.ERROR)

users_menu = {}
tb = telebot.TeleBot(settings.telegram_token,threaded=True)
bot_info = tb.get_me()
repost_message = None
answ=functions.AnswFunctions(tb=tb,db=db_api)
helpers = functions.helpers()
wallet = api.Wallet(access_token=settings.ya_token)

to_replace = {'%all_users%': lambda: db_api.count.users(),
              '%users_today%': lambda: db_api.count.activity(date=time.strftime("%d/%m/%Y")),
              '%posts_count%': lambda: db_api.count.channels(active=1),
              '%money_for_views%': lambda: list(db_api.sumof.transactions(row='count', type='view_pay'))[0][
                  'sum(count)'],
              '%money_out%': lambda: list(db_api.sumof.transactions(row='count', type='pay_out'))[0]['sum(count)']}

def get_user(id,message):
    for i in range(1,6):
        user = db_api.get.users(user_id=id)
        if len(user) > 0:
            return user[0]

    tb.send_message(chat_id=message.chat.id, text='Чтобы начать - напиши /start')
    return False

def send_message(message,mobj,**kwargs):
    try:
        if 'text' in mobj: text = mobj['text']
        else: text = ' '

        if 'markup' in mobj: markup = answ.gen(mobj['markup'])
        else: return tb.send_message(message.chat.id, text=text,**kwargs)
        if message.from_user.id in settings.admins:
            markup = answ.gen(mobj['markup'])
            try:
                markup.row(types.KeyboardButton('Админка'))
            except:
                pass
        return tb.send_message(message.chat.id, text=text, reply_markup=markup, **kwargs)
    except:
        return


@tb.message_handler(commands=['start', 'help'])
def send_welcome(message):
    send_message(message, messages.start)
    user = db_api.get.users(user_id=message.from_user.id)

    if len(user)>0:
        return






    db_api.insert.users(user_id=message.from_user.id,menu='home',refs='[]',referal=0,balance=0,ref_balance=0,add_info='{}',channels='[]',username=message.from_user.username,chat_id=message.chat.id,ref_pay=0)
    users_menu.update({message.from_user.id: 'home'})
    db_api.insert.activity(trans_id=random.randint(0, 99999), type='new_user',
                                user_id=message.from_user.id, date=time.strftime("%d/%m/%Y"))
    if len(message.text.split(' '))>1 and message.text.split(' ')[1] != str(message.from_user.id):
        helpers.new_referal(db_api,message.from_user.id,message.text.split(' ')[1])

    return


@tb.message_handler(content_types=["text",'channel','forward_from','post','sticker','forward_from_chat','audio','photo','video_note','voice','location','caption','game','sticker','document','venue','video','contact','entities','photo'],func= lambda m: m.forward_from_chat is not None)
def nuks(message):

    if message.forward_from_chat.type=='channel':


        user = get_user(message.from_user.id, message)

        if not user:
            return
        try:
            add_info = ast.literal_eval(db_api.get.users(user_id=message.from_user.id)[0]['add_info'])
        except:
            add_info = {}

        if message.from_user.id not in users_menu:

            menu = user['menu']
        else:
            menu = users_menu[message.from_user.id]
        user = user

        if menu=='advert':
            try:
                channels = db_api.get.channels(channel_name='@' + message.forward_from_chat.username)
            except:

                tb.send_message(message.chat.id,text=messages.for_advert['error_not_admin']['text'],reply_markup=answ.gen_inl(messages.for_advert['error_not_admin']['markup']))
                return
            if len(channels)>0:

                if not channels[0]['active'] and message.from_user.id==channels[0]['user_id']:
                    pass
                else:

                    return send_message(message,messages.for_advert['already_in'])

            add_info.update(
                {'channel_name': '@' + message.forward_from_chat.username, 'channel_id': message.forward_from_chat.id})
            db_api.insert.users(user_id=message.from_user.id, add_info=str(add_info))
            admin = answ.chechk_admin('@'+message.forward_from_chat.username,bot_info.username)
            if admin:
                send_message(message,messages.for_advert['success'])

                db_api.insert.users(user_id=message.from_user.id,menu='advert_enter_cost')
                return
            else:
                tb.send_message(message.chat.id,text=messages.for_advert['error_not_admin']['text'],reply_markup=answ.gen_inl(messages.for_advert['error_not_admin']['markup']))
                return
        else:
            return







@tb.message_handler(content_types=["text",'channel','forward_from','post','sticker','forward_from_chat','audio','photo','video_note','voice','location','caption','document'])
def nuka(message):

    user_id = message.from_user.id
    global repost_message
    text = message.text
    user = get_user(message.from_user.id, message)

    if not user:
        return
    try:
        add_info = ast.literal_eval(db_api.get.users(user_id=message.from_user.id)[0]['add_info'])
    except:
        add_info = {}

    if message.from_user.id not in users_menu:

        menu = user['menu']
    else:
        menu=users_menu[message.from_user.id]


    if text=='⛔️ Отмена':
        db_api.insert.users(user_id=user['user_id'],menu='home')
        users_menu.update({message.from_user.id:'home'})
        send_message(message,messages.decline)
        return
    if text=='Админка':
        if message.from_user.id in settings.admins:
            db_api.insert.users(user_id=message.from_user.id,menu='admin')
            users_menu.update({message.from_user.id:'admin'})
            send_message(message,messages.admin)
            return


    if menu == 'admin':
        if text == 'заявки на вывод':
            tb.send_message(chat_id=message.chat.id, text='Заявки на вывод', reply_markup=answ.inline_requests(page_n=1))
            return

        if text == 'изменить баланс':
            db_api.insert.users(user_id=message.from_user.id, menu='enter_username')
            users_menu.update({message.from_user.id:'enter_username'})
            send_message(message,messages.edit_balance)
            return
        if text == 'пополнить баланс':
            db_api.insert.users(user_id=message.from_user.id, menu='enter_username_pay')
            users_menu.update({message.from_user.id:'enter_username_pay'})
            send_message(message,messages.edit_balance)
            return
        if text == 'сделать рассылку':
            db_api.insert.users(user_id=message.from_user.id, menu='enter_message')
            users_menu.update({message.from_user.id:'enter_message'})
            send_message(message,messages.mailer)
            return
    if menu == 'enter_message':
        repost_message=message
        db_api.insert.users(user_id=user['user_id'], menu='repost_message_success')
        users_menu.update({message.from_user.id: 'repost_message_success'})
        return send_message(message, messages.mailer['confirm'])
    if menu == 'repost_message_success':
        if text == '✅ Подтвердить':
            if repost_message is not None:
                threading.Thread(target=answ.mailer, kwargs={'message': repost_message}).start()
                db_api.insert.users(user_id=message.from_user.id, menu='admin')
                users_menu.update({message.from_user.id: 'admin'})
                return send_message(message, messages.mailer['success'])



                    # Просим стоимость
    if user['menu'] == 'enter_username':
        id = helpers.ifloat(text)
        if id:
            user_to=db_api.get.users(user_id=id)
            if len(user_to)<1:
                return send_message(message,messages.edit_balance['err_user'])
            msf = {}
            msf.update(messages.edit_balance['enter_balance'])
            msf['text'] = msf['text'].replace('%balance%', str(user_to[0]['balance']))

            send_message(message, msf)
            add_info = ast.literal_eval(user['add_info'])
            add_info.update({'user_id': id})
            add_info = str(add_info)
            db_api.insert.users(user_id=user['user_id'], add_info=add_info, menu='enter_balance_id')
            users_menu.update({message.from_user.id: 'enter_balance_id'})
            return
        else:
            if '@' in text:
                text = text.replace('@','')
                user_to = db_api.get.users(username=text)
                if len(user_to) < 1:
                    return send_message(message, messages.edit_balance['err_user'])
                msf = {}
                msf.update(messages.edit_balance['enter_balance'])
                msf['text']=msf['text'].replace('%balance%',str(user_to[0]['balance']))

                send_message(message, msf)
                add_info = ast.literal_eval(user['add_info'])
                add_info.update({'user_id': text})
                add_info = str(add_info)
                db_api.insert.users(user_id=user['user_id'], add_info=add_info, menu='enter_balance_name')
                users_menu.update({message.from_user.id: 'enter_balance_name'})
                return
            else:
                return send_message(message,messages.edit_balance['err_user'])

    if user['menu'] == 'enter_balance_name':
        id = helpers.ifloat(text)
        if id or id == 0.0:

            send_message(message, messages.edit_balance['success'])
            add_info = ast.literal_eval(user['add_info'])
            if isinstance(add_info['user_id'],str):
                user_id=db_api.get.users(username=add_info['user_id'])[0]['user_id']
                db_api.insert.users(user_id=user_id,balance=id)
            else:
                db_api.insert.users(user_id=add_info['user_id'], balance=id)
            db_api.insert.users(user_id=user['user_id'], menu='admin')
            users_menu.update({message.from_user.id: 'admin'})
            return
        else:
            return send_message(message, messages.edit_balance['err_number'])

    if user['menu'] == 'enter_balance_id':
        id = helpers.ifloat(text)
        if id:

            send_message(message, messages.edit_balance['success'])
            add_info = ast.literal_eval(user['add_info'])
            db_api.insert.users(user_id=add_info['user_id'],balance=id)
            db_api.insert.users(user_id=user['user_id'], menu='admin')
            users_menu.update({message.from_user.id: 'admin'})
            return
        else:
            return send_message(message, messages.edit_balance['err_number'])



  ############################

    if user['menu'] == 'enter_username_pay':
        id = helpers.ifloat(text)
        if id:
            user_to=db_api.get.users(user_id=id)
            if len(user_to)<1:
                return send_message(message,messages.pay_balance['err_user'])
            msf = {}
            msf.update(messages.pay_balance['enter_balance'])
            msf['text'] = msf['text'].replace('%balance%', str(user_to[0]['balance']))

            send_message(message, msf)
            add_info = ast.literal_eval(user['add_info'])
            add_info.update({'user_id': id})
            add_info = str(add_info)
            db_api.insert.users(user_id=user['user_id'], add_info=add_info, menu='enter_balance_name_pay')
            users_menu.update({message.from_user.id: 'enter_balance_name_pay'})
            return
        else:
            if '@' in text:
                text = text.replace('@','')
                user_to = db_api.get.users(username=text)
                if len(user_to) < 1:
                    return send_message(message, messages.pay_balance['err_user'])
                msf = {}
                msf.update(messages.pay_balance['enter_balance'])
                msf['text']=msf['text'].replace('%balance%',str(user_to[0]['balance']))

                send_message(message, msf)
                add_info = ast.literal_eval(user['add_info'])
                add_info.update({'user_id': text})
                add_info = str(add_info)
                db_api.insert.users(user_id=user['user_id'], add_info=add_info, menu='enter_balance_name_pay')
                users_menu.update({message.from_user.id: 'enter_balance_name_pay'})
                return
            else:
                return send_message(message,messages.pay_balance['err_user'])

    if user['menu'] == 'enter_balance_name_pay':
        id = helpers.ifloat(text)
        if id or id ==0.0:

            send_message(message, messages.pay_balance['success'])
            add_info = ast.literal_eval(user['add_info'])
            if isinstance(add_info['user_id'],str):
                user_id=db_api.get.users(username=add_info['user_id'])
                answ.balance(type='pay_in', count=id, user=user_id[0])
            else:
                user_id = db_api.get.users(user_id=add_info['user_id'])
                answ.balance(type='pay_in', count=id, user=user_id[0])

            db_api.insert.users(user_id=user['user_id'], menu='admin')
            users_menu.update({message.from_user.id: 'admin'})
            return
        else:
            return send_message(message, messages.pay_balance['err_number'])



    ##################
    ## Добавление поста    ###########################################
    # Просим стоимость
    if user['menu'] == 'advert_enter_cost':
        cost = helpers.ifloat(text)
        if cost:
            if cost<settings.min_post_cost:
                return send_message(message, messages.for_advert['error_low_cost'])
            send_message(message,messages.for_advert['success_count'])
            add_info.update({'cost':cost})

            db_api.insert.users(user_id=user['user_id'],add_info=str(add_info),menu='advert_enter_count')
            users_menu.update({message.from_user.id: 'advert_enter_count'})
            return
        else:
            return send_message(message, messages.channel_enter_cost['error'])

    # Просим кол-во
    if user['menu'] == 'advert_enter_count':
        count = helpers.ifint(text)
        if count:
            if count<1:
                return
            add_info.update({'count': count})
            conf_mes = {}
            conf_mes.update(messages.for_advert['success_apply'])
            conf_mes['text'] =conf_mes['text'].format(count,add_info['cost'],count*add_info['cost'])
            send_message(message, conf_mes)

            db_api.insert.users(user_id=user['user_id'], add_info=str(add_info), menu='advert_confirm_post')
            users_menu.update({message.from_user.id: 'advert_confirm_post'})
            return

        else:
            send_message(message, messages.channel_enter_count['error_int'])
            return

    # Просим подтверждения
    if user['menu'] == 'advert_confirm_post':
        try:
            if text=='✅ Подтвердить':
                answ.post_confirm(user,send_message,message)
                db_api.insert.users(user_id=user['user_id'],menu='home')
                users_menu.update({message.from_user.id: 'home'})
                return
            else:
                return send_message(message, messages.channel_enter_count['error'])
        except:
            return

    ###########################################################################

    # Смотрим посты
    if text == '➕ Горшочек вари':
        t=threading.Thread(target=answ.sub,kwargs={'user':user,'send_message':send_message,'message':message})
        t.start()
        return



 

    if text == '💎 Золотой пиар канала':
        try:
            if 'last_adv' in add_info:
                tb.delete_message(chat_id=message.chat.id,message_id=add_info['last_adv'])
        except:
            pass
        mes_id = send_message(message, messages.for_advert, parse_mode='Markdown')
        users_menu.update({user_id:'advert'})
        add_info.update({'last_adv':mes_id.message_id})
        db_api.insert.users(user_id=user_id,menu='advert',add_info=str(add_info))

        return

    if text == '👥 Рефералы':
        referals = []

        referal = db_api.get.users(user_id=user['referal'])
        refs2nd = 0

        refs = ast.literal_eval(user['refs'])


        if len(refs)>0:
            for fstref in refs:
                try:
                    secref = ast.literal_eval(db_api.get.users(user_id=fstref)[0]['refs'])
                except:
                    secref =[]
                refs2nd = refs2nd + len(secref)
        if len(refs)<1:
            referals='нет'
        else:
            referals=len(refs)
        if refs2nd<1:
            refs2nd='нет'
        else:
            refs2nd=refs2nd

        if len(referal)<1:

            ref_answ={
                'text':'''👤Вас пригласил: пришел сам
👥Ваши рефералы 1го уровня: {}
👥Ваши рефералы 2го уровня: {}
Реферальная ссылка: https://t.me/{}?start={}

💸Доход с рефералов 1 Уровня - 15%
💸Доход с рефералов 2 Уровня - 5%'''.format(referals,refs2nd,bot_info.username,user['user_id']),
                'markup':messages.start['markup']
            }

        else:
            if referal[0]['username'] is not None:
                ref_answ = {
                    'text': '''👤Вас пригласил: [Реферал](tg://user?id={})
👥Ваши рефералы 1го уровня: {}
👥Ваши рефералы 2го уровня: {}
Реферальная ссылка: [https://t.me/{}?start={}](https://t.me/{}?start={})

💸Доход с рефералов 1 Уровня - 15%
💸Доход с рефералов 2 Уровня - 5%'''.format(user['referal'],referals,refs2nd,bot_info.username,user['user_id'],bot_info.username,user['user_id']),
                    'markup': messages.start['markup']
                }
                try:
                    return send_message(message, ref_answ, disable_web_page_preview=True,parse_mode='Markdown')
                except:
                    ref_answ = {
                        'text': '''👤Вас пригласил: {}
👥Ваши рефералы 1го уровня: {}
👥Ваши рефералы 2го уровня: {}
Реферальная ссылка: https://t.me/{}?start={}

💸Доход с рефералов 1 Уровня - 15%
💸Доход с рефералов 2 Уровня - 5%'''.format(
                            referal[0]['user_id'], referals, refs2nd, bot_info.username, user['user_id']),
                        'markup': messages.start['markup']
                    }
                    return send_message(message, ref_answ, disable_web_page_preview=True)
            else:
                ref_answ = {
                    'text': '''👤Вас пригласил: @{}
👥Ваши рефералы 1го уровня: {}
👥Ваши рефералы 2го уровня: {}
Реферальная ссылка: https://t.me/{}?start={}

💸Доход с рефералов 1 Уровня - 15%
💸Доход с рефералов 2 Уровня - 5%'''.format(
                        referal[0]['username'], referals, refs2nd, bot_info.username, user['user_id'], bot_info.username,
                        user['user_id']),
                    'markup': messages.start['markup']
                }
        return send_message(message, ref_answ, disable_web_page_preview=True)




    # Статистика todo в статистике ебнуть всю статистику проекта А именно: пользователей всего,пользователей за сегодня, постов всего,Заработаннт всего Выплачено всего

    if text == 'Навар':
        obj = {}
        obj.update(messages.stat)

        for i in to_replace:
            obj['text']=obj['text'].replace(i,str(round((lambda x: x if x is not None else 0)(to_replace[i]()),2)))

        return send_message(message, obj,parse_mode='Markdown')

    if text == '⚠ Рецепт':
     return send_message(message,{'text':'''
       ⛔️ПРАВИЛА использования бота "Горшочек Золота"

1. Отписываться от канала (в течение 14 дней).
 2. Спамить Горшочек повторными командами.
 3. На один кошелек выводить средства с 11 и более аккаунтов.
 4. Запрещается смена username.
 За несоблюдение правил баланс пользователя обнуляется в пользу запасов горшочка!

 Рекламадателям запрещено:

 1. Размещать каналы  порнографического и  мошеннического содержания. Заниматься негативным психологическим воздействием, пропагандой наркотиков и терроризма.
 Такое не нравится Горшочку и он будет вынужден заблокировать пользователя полностью без возврата средств.
 2. После оформления заказа убирать права у бота.
 В случае обнаружения ваш заказ удаляется, деньги не возвращаются.
 Права у Горшочка можно убрать после окончания заказа!
 
       ''','markup':messages.start['markup']})


    if text == '🏠 Личный горшочек':
        try:
            view_bal = round(list(db_api.sumof.transactions(row='count', type='view_pay',user_id=message.from_user.id))[0]['sum(count)'],2)
        except:
            view_bal = 0
        try:
            ref_pay = round(user['ref_pay'],2)
        except:
            ref_pay=0

        try:
            usr_chn =ast.literal_eval(user['channels'])
        except:
            usr_chn = []
        msg = {
            'text':'''🏠 Личный горшочек:
    🖥 Мой ID: {}
    ☑️Сделано подписок: {}
    💲 Заработано с подписок: {}p
    📣Доход с привлечения: {}p
    💰Всего заработано: {}p
    💸Выведено всего: {}p
    '''.format(message.from_user.id,len(usr_chn),view_bal,round(ref_pay,2),round(view_bal+round(ref_pay,2),2),round((lambda x: x if x is not None else 0)(list(db_api.sumof.transactions(row='count', type='pay_out',user_id=message.from_user.id))[0]['sum(count)']),2)),
            'markup':[['👥 Рефералы'],['🔚 Домой']]
        }
        send_message(message,msg)
        return

    if text== '💰 Запасы золота':
        answr = {'text':'''Ваш общий баланс: {}р
        Баланс: {}р
        Реферальный баланс: {}р'''.format(round(user['balance']+user['ref_balance'],2),round(user['balance'],2),round(user['ref_balance'],2 )),
        'markup':[['💸 Вывод','💰 Пополнение'],['🔚 Домой']]}
        send_message(message, answr)
        return

    if text == '💸 Вывод':
        answr = {'text':'''Выберете способ вывода:''',
        'markup':[['Яндекс деньги','QIWI'],['🔚 Домой']]}
        send_message(message,answr)
        return


    # ############### QIWI ###########
    if text == 'QIWI':
        obj = {}
        obj.update(messages.out_pay)
        obj['text'] = obj['text'].replace('%max_money%', str(round(user['balance'] + user['ref_balance'])))
        send_message(message, obj)
        db_api.insert.users(user_id=user['user_id'], menu='out_pay_qiwi')
        users_menu.update({message.from_user.id: 'out_pay_qiwi'})
        return

    if user['menu'] == 'out_pay_qiwi':
        count = helpers.ifloat(text)
        if count:
            if count< settings.min_out_pay:
                return send_message(message,messages.out_pay['error_min_pay'])
            if count> user['balance']+user['ref_balance']:
                return send_message(message,messages.out_pay['error_max_pay'])

            add_info = ast.literal_eval(user['add_info'])
            add_info.update({'count_to_out_pay': count})
            add_info = str(add_info)
            db_api.insert.users(user_id=user['user_id'], add_info=add_info, menu='enter_qiwi')
            users_menu.update({message.from_user.id: 'enter_qiwi'})
            return send_message(message,messages.out_pay['enter_qiwi'])

    if user['menu'] == 'enter_qiwi':
        number = text.replace(' ','').replace('+','').replace('-','')
        if number:
            add_info = ast.literal_eval(user['add_info'])
            add_info.update({'qiwi_number': number})
            answ.balance(type='pay_out',user=user,count=add_info['count_to_out_pay'],qiwi_number=number,username=message.from_user.username,out_type='QIWI')
            db_api.insert.users(user_id=user['user_id'], menu='home', add_info=str(add_info))
            users_menu.update({message.from_user.id: 'home'})
            return send_message(message, messages.out_pay['success'])
    ############ END QIWI #####################


    # ############### YAD ###########
    if text == 'Яндекс деньги':
        obj = {}
        obj.update(messages.out_pay['ya'])
        obj['text'] = obj['text'].replace('%max_money%', str(round(user['balance'] + user['ref_balance'],2)))
        send_message(message, obj)
        db_api.insert.users(user_id=user['user_id'], menu='out_pay_ya')
        users_menu.update({message.from_user.id: 'out_pay_ya'})
        return

    if user['menu'] == 'out_pay_ya':
        count = helpers.ifloat(text)
        if count:
            if count < settings.min_out_pay:
                return send_message(message, messages.out_pay['error_min_pay'])
            if count > user['balance'] + user['ref_balance']:
                return send_message(message, messages.out_pay['error_max_pay'])

            add_info = ast.literal_eval(user['add_info'])
            add_info.update({'count_to_out_pay': count})
            add_info = str(add_info)
            db_api.insert.users(user_id=user['user_id'], add_info=add_info, menu='enter_ya')
            users_menu.update({message.from_user.id: 'enter_ya'})
            return send_message(message, messages.out_pay['enter_ya'])

    if user['menu'] == 'enter_ya':
        number = text.replace(' ', '').replace('+', '').replace('-', '')
        if number:
            add_info = ast.literal_eval(user['add_info'])
            add_info.update({'qiwi_number': number})
            answ.balance(type='pay_out', user=user, count=add_info['count_to_out_pay'], qiwi_number=number,
                         username=message.from_user.username, out_type='YA')
            db_api.insert.users(user_id=user['user_id'], menu='home', add_info=str(add_info))
            users_menu.update({message.from_user.id: 'home'})
            return send_message(message, messages.out_pay['success'])

    ############ END QIWI #####################



            # ############### на Webmoney ###########
    if text == 'на Webmoney':
        obj = {}
        obj.update(messages.out_pay['ya'])
        obj['text'] = obj['text'].replace('%max_money%', str(round(user['balance'] + user['ref_balance'], 2)))
        send_message(message, obj)
        db_api.insert.users(user_id=user['user_id'], menu='out_pay_web')
        users_menu.update({message.from_user.id: 'out_pay_web'})
        return

    if user['menu'] == 'out_pay_web':
        count = helpers.ifloat(text)
        if count:
            if count < settings.min_out_pay:
                return send_message(message, messages.out_pay['error_min_pay'])
            if count > user['balance'] + user['ref_balance']:
                return send_message(message, messages.out_pay['error_max_pay'])

            add_info = ast.literal_eval(user['add_info'])
            add_info.update({'count_to_out_pay': count})
            add_info = str(add_info)
            db_api.insert.users(user_id=user['user_id'], add_info=add_info, menu='enter_web')
            users_menu.update({message.from_user.id: 'enter_web'})
            return send_message(message, messages.out_pay['enter_ya'])

    if user['menu'] == 'enter_web':
        number = text.replace(' ', '').replace('+', '').replace('-', '')

        add_info = ast.literal_eval(user['add_info'])
        add_info.update({'qiwi_number': number})
        answ.balance(type='pay_out', user=user, count=add_info['count_to_out_pay'], qiwi_number=number,
                     username=message.from_user.username, out_type='WEB')
        db_api.insert.users(user_id=user['user_id'], menu='home', add_info=str(add_info))
        users_menu.update({message.from_user.id: 'home'})
        return send_message(message, messages.out_pay['success'])
            ############ END QIWI #####################

    if text == '💰 Пополнение':
        answr = {'text':'''Выберете способ пополнения:''',
        'markup':[['Яндекс '],['Киви','Другой способ'],['🔚 Домой']]}
        send_message(message,answr)

        return

    if text == 'Другой способ':
        return send_message(message,{'text':'Если вы хотите пополнить свой баланс иным способом - пожалуйста напишите администратору @palapalaru','markup':messages.start['markup']})
    if text == 'Мои заказы':
        channels = db_api.get.channels(user_id=user['user_id'])
        text = 'Вот ваши заказы:\n'
        if len(channels)<1:
            return send_message(message,{'text':'''
                У вас нет активных заказов, чтобы добавить ваш канал для раскрутки - действуйте по инструкции. Пополните баланс и заказывайте тысячи подписчиков на ваши каналы за копейки!''','markup':messages.for_advert['markup']})
        else:

            for i in channels:
                text += '✴️ Канал: {} \n💸 Стоимость: {}\n 📥 Осталось вступлений: {}\n'.format(i['channel_name'],i['cost'],i['views'])
        return send_message(message,{'text':text,'markup':messages.for_advert['markup']})
    if text == 'Киви':
        answ.gen_code(user=user,send_message=send_message,message=message)
        return
    if text == 'Яндекс':
           return send_message(message,{'text':'''
            🔥 Для автоматического пополнения баланса переведите нужную сумму по ссылке https://money.yandex.ru/to/{} указав Ваш ID в комментарии к переводу.
⛔️Очень важно оставить ID в комментарии, иначе платеж не будет засчитан!
⚡️После перевода сумма зачислится вручную от 5 до 60 минут
            '''.format(settings.ya_number),'markup':messages.start['markup']})
   
            ##################### Вывод меню

    ########################

    # Возвращение на домашний экран
    if text =='🔚 Домой':
        obj = {}
        obj.update(messages.start)
        obj['text']=random.choice(['🏠'])
        return send_message(message,mobj=obj)
    else:
        if user['menu'] == 'advert':
            send_message(message,{'text':'''У вас нет заказов!⛔️
🔧🔨Чтобы добавить ваш канал для раскрутки - действуйте по инструкции, указанной выше.''','markup':messages.for_advert['markup']})


@tb.message_handler(content_types=["contact"])
def contact(message):
    text = message.text
    user = get_user(message.from_user.id, message)
    if not user:
        return


    if user['menu'] == 'enter_qiwi':
        add_info = ast.literal_eval(user['add_info'])
        add_info.update({'qiwi_number': message.contact.phone_number})
        answ.balance(type='pay_out',user=user,count=add_info['count_to_out_pay'],qiwi_number=message.contact.phone_number,username=message.from_user.username)
        db_api.insert.users(user_id=user['user_id'], menu='home',add_info=str(add_info))
        users_menu.update({message.from_user.id: 'home'})
        return send_message(message,messages.out_pay['success'])



@tb.callback_query_handler(lambda query: True)
def inl(query):
    data = query.data
    # try:

    user = get_user(query.from_user.id, query.message)

    if not user:
        return
    if 'acceptid' in data:
        db_api.insert.transactions(trans_id=int(data.split('_')[1]),status='done')
        return tb.edit_message_text(text='Заявка принята',chat_id=query.message.chat.id,message_id=query.message.message_id,reply_markup=answ.inline_requests(1))

    if 'decline' in data:
        tr =  db_api.get.transactions(trans_id=int(data.split('_')[1]))
        user = db_api.get.users(user_id=tr[0]['user_id'])
        if len(user)>0:
            db_api.insert.users(user_id=tr[0]['user_id'],balance=user[0]['balance']+tr[0]['count'])
        db_api.insert.transactions(trans_id=int(data.split('_')[1]),status='decline')
        return tb.edit_message_text(text='Заявка отклонена',chat_id=query.message.chat.id,message_id=query.message.message_id,reply_markup=answ.inline_requests(1))


    if 'tid' in data:
        tr = db_api.get.transactions(trans_id=int(data.split('_')[1]))[0]
        text = '''Пользователь: @{}
id: {}
Номер {}: {}
Сумма для вывода: {}
Дата: {}'''.format(tr['username'],tr['user_id'],tr['menu'],tr['qiwi_number'],tr['count'],tr['date'])


        return tb.edit_message_text(text=text,chat_id=query.message.chat.id,message_id=query.message.message_id,reply_markup=answ.gen_inl([[{'text':'✅ Принять','data':'acceptid_{}'.format(tr['trans_id'])},{'text':'❌ Отклонить','data':'decline_{}'.format(tr['trans_id'])}]]))
    if 'pgn' in data:
        return tb.edit_message_reply_markup(chat_id=query.message.chat.id,message_id=query.message.message_id,reply_markup=answ.inline_requests(int(data.replace('pgn_',''))))


    if data == 'cancel_check_admin':
        tb.delete_message(chat_id=query.message.chat.id,message_id=query.message.message_id)
        db_api.insert.users(user_id=query.message.from_user.id,menu='home')
        users_menu.update({query.from_user.id: 'home'})
        return send_message(query.message,messages.decline)
    if data == 'check_admin':
        add_info = ast.literal_eval(user['add_info'])
        admin = answ.chechk_admin(add_info['channel_name'], bot_info.username)
        if admin:
            send_message(query.message, messages.for_advert['success'])

            db_api.insert.users(user_id=query.from_user.id, menu='advert_enter_cost')
            return
        else:
            tb.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)
            tb.send_message(text='Всё еще не администратор',chat_id=query.message.chat.id,reply_markup=answ.gen_inl(messages.for_advert['error_not_admin']['markup']))
            return
    if 'chck-public-' in data:
        channel=data.split('-')[2]

        print(answ.check_sub(channel,user,send_message,query.message))

        return
    # except:
    #     return







app = flask.Flask(__name__)
# Empty webserver index, return nothing, just http 200
@app.route('/', methods=['GET', 'HEAD'])
def index():
    return ''


# Process webhook calls
@app.route(settings.WEBHOOK_URL_PATH, methods=['POST'])
def webhook():
    if flask.request.headers.get('content-type') == 'application/json':
        json_string = flask.request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        tb.process_new_updates([update])
        return ''
    else:
        flask.abort(403)
@app.route('/ya_pay', methods=['POST','GET'])
def ymon():
    token = api.Wallet.get_access_token(client_id='103703A821D04244A16FA4554553725282C76EF2E5491E3690FAC425D7665EB4', code=flask.request.args['code'],
                                    redirect_uri='https://37.60.177.245:8443/ya_pay')['access_token']

    return token


# @app.route('/ya_notif',methods=['POST','GET'])
# def ya():
#     params = flask.request.form
#     print(flask.request.form)
#     if len(params)>0:
#         if params['operation_id']!='test-notification':
#             operation = wallet.operation_details(operation_id=params['operation_id'])
#             if operation['status']=='success' and operation['direction']=='in':
#                 if 'message' in operation:
#                     answ.check_code(code=operation['message'],count=operation['amount'],send_message=send_message,number=operation['operation_id'])
#                 elif 'comment' in operation:
#                     answ.check_code(code=operation['comment'], count=operation['amount'], send_message=send_message, number=operation['operation_id'])
#                 elif 'details' in operation:
#                     answ.check_code(code=operation['details'], count=operation['amount'], send_message=send_message, number=operation['operation_id'])
#                 elif 'title' in operation:
#                     answ.check_code(code=operation['title'], count=operation['amount'], send_message=send_message, number=operation['operation_id'])
#         else:
#             operation = wallet.operation_details(operation_id='1122570744402048017')
#             print(operation)
#             if operation['status']=='success' and operation['direction']=='in':
#                 if 'message' in operation:
#                     answ.check_code(code=operation['message'],count=operation['amount'],send_message=send_message,number=operation['operation_id'])
#                 elif 'comment' in operation:
#                     answ.check_code(code=operation['comment'], count=operation['amount'], send_message=send_message, number=operation['operation_id'])
#                 elif 'details' in operation:
#                     answ.check_code(code=operation['details'], count=operation['amount'], send_message=send_message, number=operation['operation_id'])
#                 elif 'title' in operation:
#                     answ.check_code(code=operation['title'], count=operation['amount'], send_message=send_message, number=operation['operation_id'])
#
#
#
#     return "OK",200
    # if flask.request.headers.get('content-type') == 'application/json':
    #     json_string = flask.request.get_data().decode('utf-8')
    #     update = telebot.types.Update.de_json(json_string)
    #     tb.process_new_updates([update])
    #     return ''
    # else:
    #     flask.abort(403)


# Remove webhook, it fails sometimes the set if there is a previous webhook

print(tb.remove_webhook())
time.sleep(4)
# # Set webhook
s = settings.WEBHOOK_URL_BASE+settings.WEBHOOK_URL_PATH
print(s)
print(tb.set_webhook(url=settings.WEBHOOK_URL_BASE + settings.WEBHOOK_URL_PATH,
                certificate=open(settings.WEBHOOK_SSL_CERT, 'r'),allowed_updates=['update_id','message','edited_message','channel_post','edited_channel_post','inline_query','chosen_inline_result','callback_query','shipping_query','pre_checkout_query']))
threading.Thread(target=answ.check_qiwi,kwargs={'send_message':send_message}).start()
threading.Thread(target=answ.check_ya,kwargs={'send_message':send_message}).start()
app.run(host=settings.WEBHOOK_LISTEN,
        port=settings.WEBHOOK_PORT,
        ssl_context=(settings.WEBHOOK_SSL_CERT, settings.WEBHOOK_SSL_PRIV),threaded=True)

# while True:
#     try:
#         threading.Thread(target=answ.check_qiwi,kwargs={'send_message':send_message}).start()
#         tb.polling()
#     except:
#         time.sleep(10)
#         continue
