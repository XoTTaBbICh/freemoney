db_url='sqlite:///db.sqlite'

ref_pay_perc_1lvl=0.15 #столько получит от 1 уровная рефералов за оплату
ref_pay_perc_2lvl=0 #столько получит от 2 уровная рефералов за оплату
ref_view_pay_1lvl=0.15 #столько получит от 1 уровная рефералов за подписку
ref_view_pay_2lvl=0.05 #столько получит от 2 уровная рефералов за подписку
user_view_perc=0.25 #столько получит пользователь за вступление(проценты от стоимости установленной заказчиком)
min_out_pay=15 #минимальная сумма для вывода
min_post_cost=0.5 #минимальная стоимость 1 подписчика

number= 998977107142#тут твой номер киви в формате 79999999999
qiwi_token ='530c31139523466bed8449a2ced258b9'

ya_number= 410015178145654
ya_token=''

telegram_token='497864529:AAEVqh6_t-d2i9uBFee8dN5OcnC6f5cte-I'



uah_to_rub=2.16
usd_to_rub=57.85
eur_to_rub=67.73

admins = [204985443]


tutorial_url = 'http://telegra.ph/'



WEBHOOK_HOST = 'localhost'
WEBHOOK_PORT = 88
WEBHOOK_LISTEN = '0.0.0.0'


WEBHOOK_SSL_CERT = './webhook_cert.pem'
WEBHOOK_SSL_PRIV = './webhook_pkey.pem'

WEBHOOK_URL_BASE = "http://localhost/Tools/phpmyadmin/index.php:3306".format(WEBHOOK_HOST, WEBHOOK_PORT)

WEBHOOK_URL_PATH = "https://api.telegram.org/bot<AAEVqh6_t-d2i9uBFee8dN5OcnC6f5cte-I>".format(telegram_token)
