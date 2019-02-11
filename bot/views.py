# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
#from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
#from .models import Tarading_Bot_Data
import requests
import mysql.connector
from django.contrib.auth import logout

from django.http import HttpResponseRedirect
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .token import account_activation_token
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from .forms import SignupForm
from django.http import JsonResponse
import json
import datetime
import time
import ccxt
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
import numpy as np
from django.core.urlresolvers import reverse
import random
import string
import hashlib
import smtplib
from operator import itemgetter
#from datetime import timedelta
# Create your views here.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def Logout(request):
    logout(request)
    return HttpResponseRedirect('/')

def index(request):
    template = loader.get_template('pages/landingpage/index.html')
    conn = mysql.connector.Connect(host='localhost', user='cso', password='', database='trading_bot')
    c = conn.cursor(buffered=True)
    c.execute("""select content from landingpage where title_id='summary' """)
    summary = c.fetchone()
    c.execute("select content from landingpage where title_id='stepone'")
    steopone = c.fetchall()
    c.execute("select content from landingpage where title_id='steptwo'")
    steptwo = c.fetchall()
    c.execute("select content from landingpage where title_id='stepthree'")
    stepthree = c.fetchall()
    c.execute("select content from landingpage where title_id='feature1'")
    feature1 = c.fetchall()
    c.execute("select content from landingpage where title_id='feature2'")
    feature2 = c.fetchall()
    c.execute("select content from landingpage where title_id='feature3'")
    feature3 = c.fetchall()
    c.execute("select content from landingpage where title_id='feature4'")
    feature4 = c.fetchall()
    c.execute("select content from landingpage where title_id='feature5'")
    feature5 = c.fetchall()
    c.execute("select content from landingpage where title_id='feature6'")
    feature6 = c.fetchall()
    c.execute("select content from landingpage where title_id='risk_setting1'")
    risk_setting1 = c.fetchall()
    c.execute("select content from landingpage where title_id='risk_setting2'")
    risk_setting2 = c.fetchall()
    c.execute("select content from landingpage where title_id='risk_setting3'")
    risk_setting3 = c.fetchall()
    c.execute("select content from landingpage where title_id='risk_setting4'")
    risk_setting4 = c.fetchall()
    c.execute("select content from landingpage where title_id='safety1'")
    safety1 = c.fetchall()
    c.execute("select content from landingpage where title_id='safety2'")
    safety2 = c.fetchall()
    c.execute("select content from landingpage where title_id='safety3'")
    safety3 = c.fetchall()
    c.execute("select content from landingpage where title_id='safety4'")
    safety4 = c.fetchall()
    c.execute("select content from landingpage where title_id='safety5'")
    safety5 = c.fetchall()
    c.execute("select content from landingpage where title_id='profit'")
    profit = c.fetchall()
    c.execute("select content from landingpage where title_id='trade_style'")
    trade_style = c.fetchall()
    c.execute("select content from landingpage where title_id='risk_note'")
    risk_note = c.fetchall()
    c.execute("select content from landingpage where title_id='faq1'")
    faq1 = c.fetchall()
    c.execute("select content from landingpage where title_id='faq2'")
    faq2 = c.fetchall()
    c.execute("select content from landingpage where title_id='faq3'")
    faq3 = c.fetchall()
    c.execute("select content from landingpage where title_id='faq4'")
    faq4 = c.fetchall()
    c.execute("select content from landingpage where title_id='faq5'")
    faq5 = c.fetchall()
    c.execute("select content from landingpage where title_id='affiliate'")
    affiliate = c.fetchall()
    context = {
        'summary': summary[0],
        'stepone': steopone[0][0],
        'steptwo': steptwo[0][0],
        'stepthree': stepthree[0][0],
        'feature1': feature1[0][0],
        'feature2': feature2[0][0],
        'feature3': feature3[0][0],
        'feature4': feature4[0][0],
        'feature5': feature5[0][0],
        'feature6': feature6[0][0],
        'risk_setting1': risk_setting1[0][0],
        'risk_setting2': risk_setting2[0][0],
        'risk_setting3': risk_setting3[0][0],
        'risk_setting4': risk_setting4[0][0],
        'safety1': safety1[0][0],
        'safety2': safety2[0][0],
        'safety3': safety3[0][0],
        'safety4': safety4[0][0],
        'safety5': safety5[0][0],
        'profit': profit[0][0],
        'trade_style': trade_style[0][0],
        'risk_note': risk_note[0][0],
        'faq1': faq1[0][0],
        'faq2': faq2[0][0],
        'faq3': faq3[0][0],
        'faq4': faq4[0][0],
        'faq5': faq5[0][0],
        'affiliate': affiliate[0][0]
    }
    return HttpResponse(template.render(context, request))
# Create your views here.

def login(request):
    template = loader.get_template('pages/landingpage/login.html')
    context = {}

    return HttpResponse(template.render(context, request))
def two_step(request):
    conn = mysql.connector.Connect(host='localhost', user='cso', password='', database='trading_bot')
    c = conn.cursor(buffered=True)
    permission = request.session['permission']
    qr_code = request.POST['qr_code']
    user_id = request.session['user_id']
    print(user_id)
    c.execute("select * from user where absID=%s and qr_code=%s", (user_id, qr_code))
    if c.rowcount:
        if permission == "1":
            template = loader.get_template('pages/user/html/admin_dashboard.html')
            context = {}
            return HttpResponse(template.render(context, request))
        if permission == "4" or permission== "2" or permission == "3":
            template = loader.get_template('pages/user/html/dashboard.html')
            context = {}
            return HttpResponse(template.render(context, request))
    else:
        template = loader.get_template('pages/landingpage/login.html')
        context = {
            'login_error': "Failed Two Factor Authentication. Please retry"
        }

        return HttpResponse(template.render(context, request))

def signup(request):
    template = loader.get_template('pages/landingpage/signup.html')
    context = {}
    return HttpResponse(template.render(context, request))
def forgot_password(request):
    template = loader.get_template('pages/landingpage/password.html')
    if request.method =="POST":
        email = request.POST['email']
        #context = {}
        print()
        conn = mysql.connector.Connect(host='localhost', user='cso', password='', database='trading_bot')
        c = conn.cursor(buffered=True)
        c.execute("select username, absID from user where email=%s and verify='confirm'", (email,))
        #list1 = c.fetchall()
        user = User.objects.get(email=email)
        print(user)
        print(user.pk)
        #user = list1[0][0]
        #user_id = list1[0][1]
        if c.rowcount:
            current_site = get_current_site(request)
            mail_subject = 'Activate your new password.'
            message = render_to_string('change_password_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(
                mail_subject, message, 'admin@cexminer.nz', to=[to_email]
            )
            send_email.send()
            conn.commit()
            conn.close()
            print("change pass email success")
            context = {
                'verify_notice': "Please check your mail box to change password "
            }
        else:
            context = {
                'verify_notice': "Your email is not exist. Please retry again"
            }
            conn.commit()
            conn.close()
        return HttpResponse(template.render(context, request))
    context = {}
    return HttpResponse(template.render(context, request))
def forgot_password_activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        username = user.username
        user_email = user.email
        password = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
        hash_obj = hashlib.md5(password)
        new_password = hash_obj.hexdigest()
        #login(request, user)
        template = loader.get_template('pages/landingpage/login.html')
        conn = mysql.connector.Connect(host='localhost', user='cso', password='', database='trading_bot')
        c = conn.cursor(buffered=True)
        c.execute("update user set password=%s where username=%s and email=%s", (new_password, username, user_email))
        c.execute("update auth_user set password=%s where username=%s and email=%s", (new_password, username, user_email))
        conn.commit()
        current_site = get_current_site(request)
        mail_subject = 'New Password.'
        message = render_to_string('new_password_email.html', {
            'user': user,
            'domain': current_site.domain,
            'new_password': password,
        })
        to_email = user_email
        send_email = EmailMessage(
            mail_subject, message, 'admin@cexminer.nz', to=[to_email]
        )
        send_email.send()
        context = {
            'login_error': "Your password chage successful! Please check your mail box."
        }
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponse('Activation link is invalid!')
def about(request):
    template = loader.get_template('pages/landingpage/about.html')
    context = {}
    return HttpResponse(template.render(context, request))
def services(request):
    template = loader.get_template('pages/landingpage/services.html')
    context = {}
    return HttpResponse(template.render(context, request))
def pricing(request):
    template = loader.get_template('pages/landingpage/pricing.html')
    context = {}
    return HttpResponse(template.render(context, request))
def blog(request):
    template = loader.get_template('pages/landingpage/blog.html')
    context = {}
    return HttpResponse(template.render(context, request))
def article(request):
    template = loader.get_template('pages/landingpage/article.html')
    context = {}
    return HttpResponse(template.render(context, request))
def faq(request):
    template = loader.get_template('pages/landingpage/faq.html')
    context = {}
    return HttpResponse(template.render(context, request))
def index2(request):
    template = loader.get_template('pages/landingpage/index2.html')
    context = {}
    return HttpResponse(template.render(context, request))
### login page

def login_account(request):
    conn = mysql.connector.Connect(host='localhost', user='cso', password='', database='trading_bot')
    c = conn.cursor(buffered=True)
    mysql.connector.Connect()
    permissoin = []
    #s_p = request.session['permission']
    #s_id = request.session['user_id']

    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']
        hash_obj = hashlib.md5(password)
        password = hash_obj.hexdigest()
        recaptcha = request.POST['g-recaptcha-response']
        url = "https://www.google.com/recaptcha/api/siteverify"
        param = {'secret': '6LdtfFoUAAAAAK-X6OrMx5eYJZv34aIX2dvHlOwv', 'response': recaptcha}
        #param = {'secret': '6Ld7aV0UAAAAANVHIKLkHslgvbkD1tCiweBt4SwP', 'response': recaptcha}
        #result = requests.post(url=url, data=param, verify=True)
        result = requests.get(url='https://www.google.com/recaptcha/api/siteverify', params=param, verify=True)
        result = result.json()
        print(result)
        if result['success'] == True:
            c.execute("""select permission, username, email, absID, verify from user where email=%s and password=%s """, (email, password,))
            if c.rowcount > 0:
                data_list = c.fetchall()
                verify = data_list[0][4]
                if verify == "disable":
                    user = User.objects.get(email=email)
                    current_site = get_current_site(request)
                    mail_subject = 'Activate your blog account.'
                    message = render_to_string('acc_active_email.html', {
                        'user': user,
                        'domain': current_site.domain,
                        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                        'token': account_activation_token.make_token(user),
                    })
                    to_email = email
                    send_email = EmailMessage(
                        mail_subject, message, 'admin@cexminer.nz', to=[to_email]
                    )

                    send_email.send()

                    template = loader.get_template('pages/landingpage/login.html')
                    context = {'login_error': "Your account are not verified. Please check your mail box to verify"}
                    conn.commit()
                    return HttpResponse(template.render(context, request))
                if verify == "confirm":
                    request.session['permission'] = data_list[0][0]
                    request.session['username'] = data_list[0][1]
                    request.session['email'] = data_list[0][2]
                    request.session['user_id'] = data_list[0][3]
                    if data_list[0][0] == "4" or data_list[0][0] == "2" or data_list[0][0] == "3":
                        template = loader.get_template('pages/user/html/dashboard.html')
                        return HttpResponseRedirect(reverse('dashboard'))
                    #    request.session['permission'] = "4"
                    if data_list[0][0] == "1":
                        template = loader.get_template('pages/user/html/admin_dashboard.html')
                    #    request.session['permission'] = "1"

                    #user_id = data_list[0][3]
                    #qr_code = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(8))
                    #c.execute("update user set qr_code=%s where absID=%s", (qr_code, user_id))
                    #conn.commit()
                    #print(request.session)
                    #template = loader.get_template('pages/landingpage/qrcode.html')
                    context = {
                        #'qr_code': qr_code
                    }
                    return HttpResponse(template.render(context, request))

            else:
                template = loader.get_template('pages/landingpage/login.html')
                context = {'login_error': "Username and Password are incorrect"}
                conn.commit()
                return HttpResponse(template.render(context, request))
        else:
            template = loader.get_template('pages/landingpage/login.html')

            context = {}
            return HttpResponse(template.render(context, request))
        #print(permissoin[0][0])
    #if s_id:
    #    if s_p == "2" or s_p == "3" or s_p == "4":
    #        template = loader.get_template('pages/user/html/dashboard.html')
    #        context = {}
    #        return HttpResponse(template.render(context, request))
    #    if s_p == "1":
    #        template = loader.get_template('pages/user/html/admin_dashboard.html')
    #        context = {}
    #        return HttpResponse(template.render(context, request))
    #else:
    #    return HttpResponseRedirect(reverse('login'))
    template = loader.get_template('pages/landingpage/login.html')
    context = {}
    return HttpResponse(template.render(context, request))

def user_register(request):
    if request.method == "POST":
        conn = mysql.connector.Connect(host='localhost', user='cso', password='', database='trading_bot')
        c = conn.cursor(buffered=True)
        username = request.POST['username']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        #policy = request.POST['terms']
        password = request.POST['password']
        hash_obj = hashlib.md5(b'hello')
        print(request.POST)
        #print(policy)
        time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        hash_obj = hashlib.md5(password)
        password = hash_obj.hexdigest()
        if "terms" in request.POST:
            c.execute("select * from user where email=%s", (email,))
            data1 = c.fetchall()
            conn.commit()
            if len(data1) > 0:
                template = loader.get_template('pages/landingpage/login.html')
                context = {'login_error': "Your Email is already registered"}
                return HttpResponse(template.render(context, request))
            else:
                data = {'username': username, 'email': email, 'password': password}
                form = SignupForm(data)
                #form = SignupForm(request.POST)
                user = form.save(commit=False)
                user.is_active = False
                user.save()
#                print(user)
#               print(urlsafe_base64_encode(force_bytes(user.pk)))
#                print(account_activation_token.make_token(user))
                current_site = get_current_site(request)
                mail_subject = 'Activate your blog account.'
                message = render_to_string('acc_active_email.html', {
                    'username': username,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': account_activation_token.make_token(user),
                })
                to_email = email

                send_email = EmailMessage(
                    mail_subject, message, 'admin@cexminer.nz', to=[to_email]
                )
                try:
                    send_email.send()
                except smtplib.SMTPException, e:
                    template = loader.get_template('pages/landingpage/login.html')
                    context = {'login_error': e}
                    return HttpResponse(template.render(context, request))
                #user.save()
                c.execute(
                    """insert into `user` (`username`,`first_name`,`last_name`,`email`,`permission`,`create_date`, `password`) values (%s, %s, %s, %s, %s, %s, %s )""",
                    (username, first_name, last_name, email, '4', time, password))
                conn.commit()
                conn.close()
                # user.save()

            template = loader.get_template('pages/landingpage/login.html')
            context = {'login_error': "Please check your email to verify "}
            return HttpResponse(template.render(context, request))
        else:
            template = loader.get_template('pages/landingpage/signup.html')
            context = {'login_error': "You have to confirm Privacy Policy. Please check..."}
            return HttpResponse(template.render(context, request))

        #return redirect('https://mail.google.com/mail/u/0/#inbox')


### User Admin
def history(request):
    template = loader.get_template('pages/user/html/history.html')
    conn = mysql.connector.Connect(host='localhost', user='cso', password='', database='trading_bot')
    c = conn.cursor(buffered=True)
    user_id = request.session['user_id']
    history_list = []
    context = {}
    if request.method == "POST":
        print("there is history post")
        c.execute(
            "select bot.bot_name, bot.exchange1, bot.selected_coin, bot.trading_volume, bot.bot_type, trading_history.* from bot inner join trading_history on bot.absID=trading_history.bot_id where bot.bot_type='Demo'")
        l1 = c.fetchall()
        conn.commit()
        if c.rowcount:
            for t in l1:
                if t[8] == "complete":
                    history_list.append([t[4], t[0], 'Buy', t[1], t[2], t[3], round(float(t[11]), 2), t[9]])
                    history_list.append([t[4], t[0], 'Sell', t[1], t[2], t[3], round(float(t[12]), 2), t[10]])
                else:
                    if t[7] == "buy":
                        history_list.append([t[4], t[0], t[7], t[1], t[2], t[3], round(float(t[11]), 2), t[9]])
                    elif t[7] == "sell":
                        history_list.append([t[4], t[0], t[7], t[1], t[2], t[3], round(float(t[12]), 2), t[10]])
            context = {
                'history_data_list': history_list
            }
        else:
            context = {}
        return JsonResponse(context)
    c.execute("select absID, bot_name from bot where user_id=%s and bot_type='Demo'", (user_id,))
    bot_list = c.fetchall()
    conn.commit()
    c.execute("select bot.bot_name, bot.exchange1, bot.selected_coin, bot.trading_volume, bot.bot_type, trading_history.* from bot inner join trading_history on bot.absID=trading_history.bot_id where bot.bot_type='Demo'")
    l1 = c.fetchall()
    conn.commit()
    if bot_list:
        if c.rowcount:
            for t in l1:
                if t[8] == "complete":
                    history_list.append([t[4], t[0], 'Buy', t[1], t[2], t[3], round(float(t[11]), 2), t[9]])
                    history_list.append([t[4], t[0], 'Sell', t[1], t[2], t[3], round(float(t[12]), 2), t[10]])
                else:
                    if t[7] == "buy":
                        history_list.append([t[4], t[0], t[7], t[1], t[2], t[3], round(float(t[11]), 2), t[9]])
                    elif t[7] == "sell":
                        history_list.append([t[4], t[0], t[7], t[1], t[2], t[3], round(float(t[12]), 2), t[10]])
            context = {
                'bot_list': bot_list,
                'history_data_list': history_list
            }
        else:
            context = {
                'bot_list': bot_list
            }
    else:
        context = {}
    conn.close()
    return HttpResponse(template.render(context, request))
def bot_type_change(request):
    conn = mysql.connector.Connect(host='localhost', user='cso', password='', database='trading_bot')
    c = conn.cursor(buffered=True)
    history_list = []
    user_id = request.session['user_id']
    if request.method == "POST":
        bot_type = request.POST['bot_type']
        c.execute("select absID, bot_name from bot where user_id=%s and bot_type=%s", (user_id, bot_type))
        bot_list = c.fetchall()
        conn.commit()
        c.execute(
            "select bot.bot_name, bot.exchange1, bot.selected_coin, bot.trading_volume, bot.bot_type, trading_history.* from bot inner join trading_history on bot.absID=trading_history.bot_id where bot.bot_type=%s", (bot_type,))
        l1 = c.fetchall()
        conn.commit()
        if bot_list:
            if c.rowcount:
                for t in l1:
                    if t[8] == "complete":
                        history_list.append([t[4], t[0], 'Buy', t[1], t[2], t[3], round(float(t[11]), 2), t[9]])
                        history_list.append([t[4], t[0], 'Sell', t[1], t[2], t[3], round(float(t[12]), 2), t[10]])
                    else:
                        if t[7] == "buy":
                            history_list.append([t[4], t[0], 'Buy', t[1], t[2], t[3], round(float(t[11]), 2), t[9]])
                        elif t[7] == "sell":
                            history_list.append([t[4], t[0], 'Sell', t[1], t[2], t[3], round(float(t[12]), 2), t[10]])
                context = {
                    'bot_list': bot_list,
                    'history_data_list': history_list
                }
            else:
                context = {
                    'bot_list': bot_list
                }
        else:
            context = {}
        conn.close()
        return JsonResponse(context)
def bot_name_change(request):
    conn = mysql.connector.Connect(host='localhost', user='cso', password='', database='trading_bot')
    c = conn.cursor(buffered=True)
    history_list = []
    user_id = request.session['user_id']
    if request.method == "POST":
        bot_name = request.POST['bot_name']

        c.execute(
            "select bot.bot_name, bot.exchange1, bot.selected_coin, bot.trading_volume, bot.bot_type, trading_history.* from bot inner join trading_history on bot.absID=trading_history.bot_id where bot.absID=%s", (bot_name,))
        l1 = c.fetchall()
        conn.commit()
        print(l1)
        if c.rowcount:
            for t in l1:
                if t[8] == "complete":
                    history_list.append([t[4], t[0], 'Buy', t[1], t[2], t[3], round(float(t[11]), 2), t[9]])
                    history_list.append([t[4], t[0], 'Sell', t[1], t[2], t[3], round(float(t[12]), 2), t[10]])
                else:
                    history_list.append([t[4], t[0], 'Buy', t[1], t[2], t[3], round(float(t[11]), 2), t[9]])
            context = {
                'history_data_list': history_list
            }
        else:
            context = {}
        conn.close()
        return JsonResponse(context)
def view_history_graph(request):
    conn = mysql.connector.Connect(host='localhost', user='cso', password='', database='trading_bot')
    c = conn.cursor(buffered=True)
    context = {}
    if request.method == "POST":
        print(request.POST['bot_id'])
        print("why")
        bot_id = request.POST['bot_id']
        user_id = request.session['user_id']
        c.execute("select trading_history.*, bot.exchange1, bot.candle_interval, bot.selected_coin, bot.base_currency, bot.bot_kind, bot.bot_name from trading_history inner join bot on bot.absID=trading_history.bot_id where trading_history.bot_id=%s order by trading_history.absID", (bot_id,))
        hist_data = c.fetchall()
        conn.commit()
        print(hist_data)
        start_date = ""
        end_date = ""
        chart_data = []
        candle_data = []
        flag_buy_data = []
        flag_sell_data = []
        flag_temp_data = []

        flag_index = 0
        exchange = hist_data[0][11]
        interval = hist_data[0][12]
        selected_coin = hist_data[0][13]
        base_currency = hist_data[0][14]
        bot_kind = hist_data[0][15]
        bot_name = hist_data[0][16]
        coin_pair = selected_coin + "/" + base_currency

        interval1 = 0
        if interval == "1m":
            interval1 = 60000
        if interval == "5m":
            interval1 = 300000
        elif interval == "15m":
            interval1 = 900000
        elif interval == "30m":
            interval1 = 1800000
        elif interval == "1h":
            interval1 = 3600000
        elif interval == "2h":
            interval1 = 7200000
        elif interval == "4h":
            interval1 = 14400000
        elif interval == "1d":
            interval1 == 86400000

        v = str(datetime.datetime.now())
        print(v)
        # v = "2018:01:01 06-05-03"
        y1 = v[:4]
        m1 = v[5:7]
        d1 = v[8:10]
        h1 = v[11:13]
        n1 = v[14:16]
        s1 = v[17:19]

        if hist_data[0][4] > hist_data[0][5]:
            start_date = str(hist_data[0][5])
        else:
            start_date = str(hist_data[0][4])
        print(start_date)
        if bot_kind == "Indicator BB Bot":
            c.execute("select bb_period, bb_upper, bb_lower from bot where absID=%s", (bot_id,))
            bb_data = c.fetchall()
            conn.commit()
            period = int(bb_data[0][0])
            upper = float(bb_data[0][1])
            lower = float(bb_data[0][2])
            bb_temp = []
            middle_data = []
            upper_data = []
            lower_data = []
            date_from = datetime.datetime(int(start_date[:4]), int(start_date[5:7]), int(start_date[8:10]), int(start_date[11:13]), int(start_date[14:16]), int(start_date[17:19]))
            date_to = datetime.datetime(int(y1), int(m1), int(d1), int(h1), int(n1), int(s1))
            date_from = int(time.mktime(date_from.timetuple()) * 1000) - (int(period)-1) * interval1
            date_to = int(time.mktime(date_to.timetuple()) * 1000)
            print(date_from)
            print(date_to)
            if exchange == "binance":
                c.execute(" select api_key, secret from exchange_info where user_id=%s and exchange=%s",
                          (user_id, 'binance'))
                key_data = c.fetchone()
                api = key_data[0]
                secret = key_data[1]
                exchange_obj = ccxt.binance({
                    #'proxies': {
                    #    'http': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                    #    'https': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                    #},
                    'apiKey': api,
                    'secret': secret,
                })
                get_data_continue = True
                print("binance info get")
                # exchange_obj.proxy = 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280'
                while get_data_continue:
                    temp_data = exchange_obj.fetch_ohlcv(coin_pair, interval, int(date_from))
                    if len(temp_data) > 0:
                        chart_data.extend(temp_data)
                        date_from = temp_data[len(temp_data) - 1][0] + 1000
                        if int(temp_data[len(temp_data) - 1][0]) >= (int(date_to) - int(interval1)):
                            get_data_continue = False
                    else:
                        get_data_continue = False
            elif exchange == "cryptopia":
                c.execute(" select api_key, secret from exchange_info where user_id=%s and exchange=%s",
                          (user_id, "cryptopia"))
                key_data = c.fetchone()
                api = key_data[0]
                secret = key_data[1]
                exchange_obj = ccxt.cryptopia({
                    'proxies': {
                        'http': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                        'https': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                    },
                    'apiKey': api,
                    'secret': secret,
                })
                # exchange_obj.proxy = 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280'
                exchange_obj.has['fetchOHLCV'] = 'emulated'
                chart_data = exchange_obj.fetch_ohlcv(coin_pair, interval)
            elif exchange == "cexio":
                c.execute(" select api_key, secret from exchange_info where user_id=%s and exchange=%s",
                          (user_id, "cexio"))
                key_data = c.fetchone()
                api = key_data[0]
                secret = key_data[1]
                exchange_obj = ccxt.cex({
                    'proxies': {
                        'http': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                        'https': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                    },
                    'apiKey': api,
                    'secret': secret,
                })
                # exchange_obj.proxy = 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280'
                exchange_obj.has['fetchOHLCV'] = 'emulated'
                chart_data = exchange_obj.fetch_ohlcv(coin_pair, interval)
            elif exchange == "bittrex":
                c.execute(" select api_key, secret from exchange_info where user_id=%s and exchange=%s",
                          (user_id, "bittrex"))
                key_data = c.fetchone()
                api = key_data[0]
                secret = key_data[1]
                exchange_obj = ccxt.bittrex({
                    'proxies': {
                        'http': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                        'https': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                    },
                    'apiKey': api,
                    'secret': secret,
                })
                get_data_continue = True
                while get_data_continue:
                    temp_data = exchange_obj.fetch_ohlcv(coin_pair, interval, int(date_from), 1000)
                    chart_data.extend(temp_data)
                    print(date_from)
                    print(temp_data)
                    print(len(temp_data))
                    print(temp_data[len(temp_data) - 1][0])
                    print(date_to)
                    print(interval1)
                    date_from = temp_data[len(temp_data) - 1][0] + 1000
                    if int(temp_data[len(temp_data) - 1][0]) >= (int(date_to) - int(interval1)):
                        get_data_continue = False
            elif exchange == "hitbtc":
                c.execute(" select api_key, secret from exchange_info where user_id=%s and exchange=%s",
                          (user_id, "hitbtc"))
                key_data = c.fetchone()
                api = key_data[0]
                secret = key_data[1]
                exchange_obj = ccxt.hitbtc2({
                    'proxies': {
                        'http': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                        'https': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                    },
                    'secret': secret,
                })
                get_data_continue = True
                while get_data_continue:
                    temp_data = exchange_obj.fetch_ohlcv(coin_pair, interval, int(date_from), 1000)
                    chart_data.extend(temp_data)
                    print(date_from)
                    print(temp_data)
                    print(len(temp_data))
                    print(temp_data[len(temp_data) - 1][0])
                    print(date_to)
                    print(temp_data[len(temp_data) - 1][0])
                    print(interval1)
                    date_from = temp_data[len(temp_data) - 1][0] + 1000
                    if int(temp_data[len(temp_data) - 1][0]) >= (int(date_to) - int(interval1)):
                        get_data_continue = False
            elif exchange == "okex":
                c.execute(" select api_key, secret from exchange_info where user_id=%s and exchange=%s",
                          (user_id, "okex"))
                key_data = c.fetchone()
                api = key_data[0]
                secret = key_data[1]
                exchange_obj = ccxt.okex({
                    'proxies': {
                        'http': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                        'https': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                    },
                    'apiKey': api,
                    'secret': secret,
                })
                # exchange_obj.has['fetchOHLCV'] = 'emulated'
                print(exchange_obj.last_http_response)
                get_data_continue = True
                while get_data_continue:
                    temp_data = exchange_obj.fetch_ohlcv(coin_pair, interval)
                    chart_data.extend(temp_data)
                    print(date_from)
                    print(temp_data)
                    print(len(temp_data))
                    print(temp_data[len(temp_data) - 1][0])
                    print(date_to)
                    print(interval1)
                    date_from = temp_data[len(temp_data) - 1][0] + 1000
                    if int(temp_data[len(temp_data) - 1][0]) >= (int(date_to) - int(interval1)):
                        get_data_continue = False
            print(chart_data)
            data_len = len(chart_data)
            print(chart_data)
            print(data_len)
            for i in range(int(period) - 1, data_len):
                data = chart_data[i - int(period) + 1]
                data.pop(5)
                t1 = data[0] / 1000
                for k in range(i - period + 1, i + 1):
                    bb_temp.append(chart_data[k][4])
                ave = np.mean(bb_temp)
                sd = np.std(bb_temp)
                middle_data.append([data[0], ave])
                upper_data.append([data[0], ave + sd * upper])
                lower_data.append([data[0], ave - sd * lower])
                candle_data.append(data)
                bb_temp = []
            print(candle_data)
            for bot_data in hist_data:
                if bot_data[3] == "complete":
                    flag_temp_data.append([bot_data[4], 'Buy', bot_data[6]])
                    flag_temp_data.append([bot_data[5], 'Sell', bot_data[7]])
                elif bot_data[4] == "create":
                    if bot_data[2] == "buy":
                        flag_temp_data.append([bot_data[4], 'Buy', bot_data[6]])
                    elif bot_data[2] == "sell":
                        flag_temp_data.append([bot_data[5], 'Sell', bot_data[7]])
            flag_temp_data = sorted(flag_temp_data)
            print(flag_temp_data)
            for i in range(0, len(chart_data) - 1):
                t1 = chart_data[i][0]
                t2 = chart_data[i + 1][0]
                for j in range(0, len(flag_temp_data)):
                    t3 = flag_temp_data[j][0]
                    p = flag_temp_data[j][2]
                    t4 = datetime.datetime(int(t3[:4]), int(t3[5:7]), int(t3[8:10]), int(t3[11:13]), int(t3[14:16]), int(t3[17:19]))
                    t4 = int(time.mktime(t4.timetuple()) * 1000)
                    if t4 > t1 and t4 < t2:
                        if flag_temp_data[j][1] == "Buy":
                            #d = "Buy" + "(" + t3 + ")"
                            flag_buy_data.append({'x': t1, 'title': 'Buy', 'text': 'price='+p+', tiem='+t3})
                        elif flag_temp_data[j][1] == "Sell":
                            #d = "Sell" + "(" + t3 + ")"
                            flag_sell_data.append({'x': t1, 'title': 'Sell', 'text': 'price='+p+', tiem='+t3})
            title = "Indicator BB Bot-" + bot_name + " Trading History Graph"
            print(flag_sell_data)
            print(flag_buy_data)
            context = {
                'bot_kind': 'Indicator BB Bot',
                'title': title,
                'chart_data': candle_data,
                'middle_data': middle_data,
                'upper_data': upper_data,
                'lower_data': lower_data,
                'flag_buy_data': flag_buy_data,
                'flag_sell_data': flag_sell_data
            }
            return JsonResponse(context)
    return JsonResponse(context)

def dashboard(request):
    template = loader.get_template('pages/user/html/dashboard.html')
    conn = mysql.connector.Connect(host='localhost', user='cso', password='', database='trading_bot')
    c = conn.cursor(buffered=True)
    print(request.session['username'])
    print(request.session['email'])
    print(request.session['user_id'])
    user_id = request.session['user_id']
    total_profit = 0
    total_loss = 0
    portfolio_value = 0
    portfolio_percent = 0
    portfolio_base = 0
    standing_order = 0
    running_bot = ""
    indicator_num = 0
    ml_num = 0
    arbitrage_num = 0
    market_num = 0
    bot_name = ""
    coin_name = ""
    bot_profit = 0
    bot_loss = 0
    coin_profit = 0
    coin_loss = 0
    day_profit = 0
    day_loss = 0
    profit_sum = 0
    loss_sum = 0
    best_bot_name = ""
    best_bot_value = 0
    best_bot_percent = 0
    worst_bot_name = ""
    worst_bot_value = 0
    worst_bot_percent = 0
    best_coin_name = ""
    best_coin_value = 0
    best_coin_percent = 0
    worst_coin_name = ""
    worst_coin_value = 0
    worst_coin_percent = 0
    best_day_name = ""
    best_day_value = 0
    best_day_percent = 0
    worst_day_name = ""
    worst_day_value = 0
    worst_day_percent = 0
    date_list = []
    coin_list = []
    number_order_date_data = []
    number_order_sell_data = []
    number_order_buy_data = []
    each_coin_date_data = []
    each_coin_portfolio_dat = []
    each_coin_name_data = []
### Portfolio and Best Bot, Worst Bot
    c.execute("select trading_history.*, bot.trading_volume, bot.bot_name from bot inner join trading_history on bot.absID=trading_history.bot_id where bot.user_id=%s and order_status='complete'", (user_id,))
    #c.execute("select * from trading_history where user_id=%s", (user_id,))
    data_list = c.fetchall()
    conn.commit()
    if len(data_list)>0:
        for i in data_list:
            if i[3] == "complete":
                portfolio_base += float(i[6]) * float(i[10])
                portfolio_value += (float(i[7]) - float(i[6])) * float(i[10])
            if (float(i[7]) - float(i[6])) > 0:
                total_profit += (float(i[7]) - float(i[6])) * float(i[10])
            else:
                total_loss += ((float(i[7]) - float(i[6]))) * float(i[10])
        portfolio_percent = round(100 * portfolio_value / portfolio_base, 2)
        portfolio_value = round(portfolio_value, 2)
    #print(portfolio_percent)
    #print(portfolio_value)
    #print(total_profit)
    #print(total_loss)
### Outstanding Order
    c.execute("select count(bot_id) from trading_history where order_status='create'")
    data_list = c.fetchall()
    standing_order = data_list[0][0]
    conn.commit()
### Number of Running Bot
    c.execute("select bot_kind from bot where user_id=%s", (user_id,))
    data_list = c.fetchall()
    conn.commit()
    if len(data_list)>0:
        for i in data_list:
            print(i[0])
            s1 = str(i[0])
            if s1.find("Indicator") >= 0:
                indicator_num += 1
            if s1.find("ML") >= 0:
                ml_num += 1
            if s1.find("Arbitrage") >= 0:
                arbitrage_num += 1
            if s1.find("Market") >= 0:
                market_num += 1
        if indicator_num > 0:
            running_bot += str(indicator_num) + " Indicator Bot, "
        if ml_num > 0:
            running_bot += str(ml_num) + " ML Bot, "
        if arbitrage_num > 0:
            running_bot += str(arbitrage_num) + " Arbitrage Bot, "
        if market_num > 0:
            running_bot += str(market_num) + " Market Maker Bot"
### Best and Worst Bot
        c.execute("select absID from bot where user_id=%s", (user_id,))
        d1 = c.fetchall()
        conn.commit()
        if len(d1)>0:
            for bot in d1:
                b_id = bot[0]
                c.execute(
                    "select trading_history.*, bot.trading_volume, bot.bot_name from bot inner join trading_history on bot.absID=trading_history.bot_id where trading_history.bot_id=%s and order_status='complete'",
                    (b_id,))
                d2 = c.fetchall()
                conn.commit()
                if len(d2) > 0:
                    for l1 in d2:
                        if (float(l1[7]) - float(l1[6])) > 0:
                            profit_sum += (float(l1[7]) - float(l1[6])) * float(l1[10])
                        else:
                            loss_sum += (float(l1[7]) - float(l1[6])) * float(l1[10])
                        bot_name = l1[11]
                    if bot_profit < profit_sum:
                        bot_profit = profit_sum
                        best_bot_name = bot_name
                        best_bot_value = profit_sum
                    if bot_loss == 0:
                        bot_loss = loss_sum
                        worst_bot_name = bot_name
                        worst_bot_value = loss_sum
                    elif bot_loss > loss_sum:
                        bot_loss = loss_sum
                        worst_bot_name = bot_name
                        worst_bot_value = loss_sum
                    profit_sum = 0
                    loss_sum = 0
            if len(d2)>0:
                best_bot_percent = round(100 * best_bot_value / total_profit, 2)
                worst_bot_percent = round(abs(100 * worst_bot_value / total_loss), 2)
                best_bot_value = round(best_bot_value, 2)
                worst_bot_value = round(worst_bot_value, 2)



    #print(best_bot_value)
    #print(best_bot_name)
    #print(best_bot_percent)
    #print(worst_bot_value)
    #print(worst_bot_name)
    #print(worst_bot_percent)
### Best coin and Worst Coin
    c.execute(
        "select distinct(bot.selected_coin) from bot inner join trading_history on bot.absID=trading_history.bot_id where bot.user_id=%s and order_status='complete' order by bot.selected_coin",
        (user_id,))
    list1 = c.fetchall()
    conn.commit()
    if len(list1)>0:
        for coin in list1:
            c.execute(
                "select trading_history.*, bot.trading_volume, bot.selected_coin from bot inner join trading_history on bot.absID=trading_history.bot_id where bot.user_id=%s and bot.selected_coin=%s and order_status='complete'",
                (user_id, coin[0]))
            data_list = c.fetchall()
            conn.commit()
            if len(data_list)>0:
                for data in data_list:
                    if (float(data[7]) - float(data[6])) > 0:
                        profit_sum += (float(data[7]) - float(data[6])) * float(data[10])
                    else:
                        loss_sum += (float(data[7]) - float(data[6])) * float(data[10])
                if profit_sum > coin_profit:
                    coin_profit = profit_sum
                    best_coin_name = coin[0]
                    best_coin_value = profit_sum
                if coin_loss == 0:
                    coin_loss = loss_sum
                    worst_coin_name = coin[0]
                    worst_coin_value = loss_sum
                elif coin_loss > loss_sum:
                    coin_loss = loss_sum
                    worst_coin_name = coin[0]
                    worst_coin_value = loss_sum
                profit_sum = 0
                loss_sum = 0
        if len(data_list)>0:
            best_coin_percent = round(100 * best_coin_value / total_profit, 2)
            worst_coin_percent = round(abs(100 * worst_coin_value / total_loss), 2)
            best_coin_value = round(best_coin_value, 2)
            worst_coin_value = round(worst_coin_value, 2)

    #print(best_coin_value)
    #print(best_coin_name)
    #print(best_coin_percent)
    #print(worst_coin_value)
    #print(worst_coin_name)
    #print(worst_coin_percent)
### Best Day and Worst Day
    c.execute(
        "select trading_history.sell_time from bot inner join trading_history on bot.absID=trading_history.bot_id where bot.user_id=%s and order_status='complete'",
        (user_id, ))
    list2 = c.fetchall()
    conn.commit()
    if len(list2)>0:
        for d in list2:
            str1 = str(d[0])
            str1 = str1[:10]
            if str1 not in date_list:
                date_list.append(str1)

        for d in date_list:
            c.execute(
                """select trading_history.*, bot.trading_volume from bot inner join trading_history on bot.absID=trading_history.bot_id where bot.user_id=%s and trading_history.sell_time like %s and order_status='complete'""",
                (user_id, d + "%"))
            d3 = c.fetchall()
            conn.commit()
            if len(d3)>0:
                for t in d3:
                    if (float(t[7]) - float(t[6])) > 0:
                        profit_sum += (float(t[7]) - float(t[6])) * float(t[10])
                    else:
                        loss_sum += (float(t[7]) - float(t[6])) * float(t[10])
                if profit_sum > day_profit:
                    day_profit = profit_sum
                    best_day_name = d
                    best_day_value = profit_sum
                if day_loss == 0:
                    day_loss = loss_sum
                    worst_day_name = d
                    worst_day_value = loss_sum
                elif day_loss > loss_sum:
                    day_loss = loss_sum
                    worst_day_name = d
                    worst_day_value = loss_sum
                profit_sum = 0
                loss_sum = 0
        if len(d3)>0:
            best_day_percent = round(100 * best_day_value / total_profit, 2)
            worst_day_percent = round(abs(100 * worst_day_value / total_loss), 2)
            best_day_value = round(best_day_value, 2)
            worst_day_value = round(worst_day_value, 2)


    #print(best_day_value)
    #print(best_day_name)
    #print(best_day_percent)
    #print(worst_day_value)
    #print(worst_day_name)
    #print(worst_day_percent)
### Portfolio of Each Coin
    c.execute(
        "select trading_history.sell_time from bot inner join trading_history on bot.absID=trading_history.bot_id where bot.user_id=%s and order_status='complete' order by trading_history.sell_time",
        (user_id,))
    list2 = c.fetchall()
    date_list = []
    date_portfolio = []
    conn.commit()
    if len(list2)>0:
        for d in list2:
            str1 = str(d[0])
            str1 = str1[:10]
            if str1 not in date_list:
                date_list.append(str1)

        c.execute(
            "select distinct(bot.selected_coin) from bot inner join trading_history on bot.absID=trading_history.bot_id where bot.user_id=%s and order_status='complete'",
            (user_id,))
        list3 = c.fetchall()
        conn.commit()
        if len(list3)>0:
            for e1 in list3:
                date_portfolio = []
                for e2 in date_list:
                    c.execute(
                        """select trading_history.*, bot.trading_volume from bot inner join trading_history on bot.absID=trading_history.bot_id where bot.user_id=%s and trading_history.sell_time like %s and bot.selected_coin=%s and order_status='complete'""",
                        (user_id, e2 + "%", e1[0]))
                    e3 = c.fetchall()
                    conn.commit()
                    for t in e3:
                        if (float(t[7]) - float(t[6])) > 0:
                            profit_sum += (float(t[7]) - float(t[6])) * float(t[10])
                        else:
                            loss_sum += (float(t[7]) - float(t[6])) * float(t[10])
                    each_coin_date_data.append(e2)
                    date_portfolio.append(round(profit_sum + loss_sum, 2))
                    profit_sum = 0
                    loss_sum = 0
                each_coin_portfolio_dat.append([e1[0], date_portfolio])
                each_coin_name_data.append(e1[0])


    #print(len(each_coin_portfolio_dat[0][1]))
    #print(each_coin_portfolio_dat)
    #print(len(each_coin_date_data))
    #print(each_coin_date_data)
    #print(each_coin_name_data)
### Number of Orders
    c.execute(
        "select trading_history.buy_time, trading_history.sell_time from bot inner join trading_history on bot.absID=trading_history.bot_id where bot.user_id=%s and order_status='complete' order by trading_history.buy_time",
        (user_id,))
    list2 = c.fetchall()
    date_list = []
    conn.commit()
    if len(list2)>0:
        for d in list2:
            for i in range(0, 2):
                str1 = str(d[i])
                str1 = str1[:10]
                if str1 not in date_list:
                    date_list.append(str1)
        for t in date_list:
            number_order_date_data.append(t)
            c.execute(
                "select count(trading_history.bot_id) from bot inner join trading_history on bot.absID=trading_history.bot_id where bot.user_id=%s and trading_history.buy_time like %s and order_status='complete'",
                (user_id, t + "%"))
            b = c.fetchall()
            number_order_buy_data.append(b[0][0])
            conn.commit()
            c.execute(
                "select count(trading_history.bot_id) from bot inner join trading_history on bot.absID=trading_history.bot_id where bot.user_id=%s and trading_history.sell_time like %s and order_status='complete'",
                (user_id, t + "%"))
            s = c.fetchall()
            number_order_sell_data.append(s[0][0])

    #print(len(number_order_date_data))
    #print(number_order_date_data)
    #print(len(number_order_buy_data))
    #print(number_order_buy_data)
    #print(len(number_order_sell_data))
    #print(number_order_sell_data)
    context = {
        'portfolio_value': portfolio_value,
        'portfolio_percent': portfolio_percent,
        'standing_order': standing_order,
        'running_bot': running_bot,
        'best_bot_name': best_bot_name,
        'best_bot_value': best_bot_value,
        'best_bot_percent': best_bot_percent,
        'worst_bot_name': worst_bot_name,
        'worst_bot_value': worst_bot_value,
        'worst_bot_percent': worst_bot_percent,
        'best_coin_name': best_coin_name,
        'best_coin_value': best_coin_value,
        'best_coin_percent': best_coin_percent,
        'worst_coin_name': worst_coin_name,
        'worst_coin_value': worst_coin_value,
        'worst_coin_percent': worst_coin_percent,
        'best_day_name': best_day_name,
        'best_day_value': best_day_value,
        'best_day_percent': best_day_percent,
        'worst_day_name': worst_day_name,
        'worst_day_value': worst_day_value,
        'worst_day_percent': worst_day_percent,
        'number_order_date_data': number_order_date_data,
        'number_order_buy_data': number_order_buy_data,
        'number_order_sell_data': number_order_sell_data,
        'each_coin_date_data': each_coin_date_data,
        'each_coin_portfolio_data': date_portfolio,
        'each_coin_name_data': each_coin_name_data
    }
    return HttpResponse(template.render(context, request))
def profit_loss(request):
    template = loader.get_template('pages/user/html/profit_loss.html')
    conn = mysql.connector.Connect(host='localhost', user='cso', password='', database='trading_bot')
    c = conn.cursor(buffered=True)
    print(request.session['username'])
    print(request.session['email'])
    print(request.session['user_id'])
    print(request.session['permission'])
    user_id = request.session['user_id']
    total_profit = 0
    total_loss = 0
    portfolio_value = 0
    portfolio_percent = 0
    portfolio_base = 0
    total_fee = 0.0
    subscription_price = 0
    profit = 0
    profit_percent = 0
    bot_profit = 0
    bot_loss = 0
    coin_profit = 0
    coin_loss = 0
    day_profit = 0
    day_loss = 0
    profit_sum = 0
    loss_sum = 0
    profit_min = 0
    profit_min_coin = ""
    profit_min_percent = 0
    profit_max = 0
    profit_max_coin = ""
    profit_max_percent = 0
    portfolio_min = 0
    portfolio_min_time = 0
    portfolio_max = 0
    portfolio_max_time = 0
    portfolio_buy_data = []
    portfolio_sell_data = []
    portfolio_date_data = []
### Profit and Loss
    c.execute(
        "select trading_history.*, bot.trading_volume, bot.bot_name from bot inner join trading_history on bot.absID=trading_history.bot_id where bot.user_id=%s and order_status='complete'",
        (user_id,))
    # c.execute("select * from trading_history where user_id=%s", (user_id,))
    data_list = c.fetchall()
    conn.commit()
    if len(data_list)>0:
        for i in data_list:
            if i[3] == "complete":
                portfolio_base += float(i[6]) * float(i[10])
                portfolio_value += (float(i[7]) - float(i[6])) * float(i[10])
                portfolio_percent += (float(i[7]) - float(i[6])) / float(i[6])
                total_fee += (float(i[8]) + float(i[9]))
            if (float(i[7]) - float(i[6])) > 0:
                total_profit += (float(i[7]) - float(i[6])) * float(i[10])
            else:
                total_loss += ((float(i[7]) - float(i[6]))) * float(i[10])
        portfolio_percent = round(100 * portfolio_value / portfolio_base, 2)
        portfolio_value = round(portfolio_value, 2)

### Subscription Price and Total Expense
        permission = request.session['permission']
        if permission == "2":
            subscription_price = 99
        elif permission == "3":
            subscription_price = 49
        elif permission == "4":
            subscription_price = 9
        profit = portfolio_value-total_fee-subscription_price
        profit_percent = round(100*profit/portfolio_base, 2)
### Portfolio and Profitable and Crypto
    c.execute(
        "select trading_history.*, bot.trading_volume, bot.selected_coin from bot inner join trading_history on bot.absID=trading_history.bot_id where bot.user_id=%s and order_status='complete'",
        (user_id,))
    data_list = c.fetchall()
    conn.commit()
    if len(data_list)>0:
        for i in data_list:
            if i[3] == "complete":
                p1 = (float(i[7]) - float(i[6])) * float(i[10])
                if p1 > portfolio_max:
                    portfolio_max = p1
                    portfolio_max_time = str(i[5])
                if portfolio_min == 0:
                    portfolio_min = p1
                    portfolio_min_time = i[5]
                elif p1 < portfolio_min:
                    portfolio_min = p1
                    portfolio_min_time = str(i[5])

                p2 = (float(i[7]) - float(i[6])) * float(i[10])
                if p2 > 0:
                    if p2 > profit_max:
                        profit_max = p2
                        profit_max_coin = i[11]
                        profit_max_percent = round((float(i[7]) - float(i[6])) / float(i[6]), 4)
                    if profit_min == 0:
                        profit_min = p2
                        profit_min_coin = i[11]
                        profit_min_percent = round((float(i[7]) - float(i[6])) / float(i[6]), 4)
                    elif p2 < profit_min:
                        profit_min = p2
                        profit_min_coin = i[11]
                        profit_min_percent = round((float(i[7]) - float(i[6])) / float(i[6]), 4)
        portfolio_min_time = portfolio_min_time[2:]
        portfolio_min_time = datetime.datetime.strptime(portfolio_min_time, "%y-%m-%d %H:%M:%S")
        portfolio_min_time = portfolio_min_time.strftime("%A, %d %B %Y at %I:%M%p")
        portfolio_max_time = portfolio_max_time[2:]
        portfolio_max_time = datetime.datetime.strptime(portfolio_max_time, "%y-%m-%d %H:%M:%S")
        portfolio_max_time = portfolio_max_time.strftime("%A, %d %B %Y at %I:%M%p")

### Portfolio Chart
    c.execute("select trading_history.buy_time, trading_history.sell_time from trading_history inner join bot on bot.absID=trading_history.bot_id where bot.user_id=%s order by trading_history.buy_time, trading_history.sell_time", (user_id,))
    l1 = c.fetchall()
    conn.commit()
    date_list = []
    buy_data = 0
    sell_data = 0
    if len(data_list)>0:
        for i in l1:
            for k in range(0, 2):
                str1 = str(i[k])
                str1 = str1[:10]
                if str1 not in date_list and str1 != "None":
                    date_list.append(str1)
        # print(date_list)
        for i in date_list:
            if i != "":
                portfolio_date_data.append(i)
            # print(portfolio_date_data)
            c.execute(
                "select trading_history.*, bot.trading_volume, bot.selected_coin from bot inner join trading_history on bot.absID=trading_history.bot_id where bot.user_id=%s and trading_history.buy_time like %s and order_status='complete'",
                (user_id, i + '%'))
            l2 = c.fetchall()
            conn.commit()
            if len(l2) > 0:
                for k in l2:
                    buy_data += float(k[6]) * float(k[10])
                portfolio_buy_data.append(round(buy_data, 2))
                buy_data = 0
            else:
                portfolio_buy_data.append(0)
            c.execute(
                "select trading_history.*, bot.trading_volume, bot.selected_coin from bot inner join trading_history on bot.absID=trading_history.bot_id where bot.user_id=%s and trading_history.sell_time like %s and order_status='complete'",
                (user_id, i + '%'))
            l3 = c.fetchall()
            conn.commit()
            if len(l3) > 0:
                for k in l3:
                    sell_data += float(k[7]) * float(k[10])
                portfolio_sell_data.append(round(sell_data, 2))
                sell_data = 0
            else:
                portfolio_sell_data.append(0)

    #print(portfolio_sell_data)
    #print(portfolio_buy_data)
    context = {
        'total_profit': str(round(portfolio_value, 2)),
        'total_fee': str(round(total_fee, 2)),
        'total_revenue': str(round(float(portfolio_value-total_fee), 2)),
        'subscription_price': str(round(subscription_price, 2)),
        'profit': str(round(profit, 2)),
        'profit_percent': portfolio_percent,
        'portfolio_min': portfolio_min,
        'portfolio_min_time': portfolio_min_time,
        'portfolio_max': portfolio_max,
        'portfolio_max_time': portfolio_max_time,
        'profit_min': profit_min,
        'profit_min_coin': profit_min_coin,
        'profit_min_percent': profit_min_percent,
        'profit_max': profit_max,
        'profit_max_coin': profit_max_coin,
        'profit_max_percent': profit_max_percent,
        'portfolio_date_data': portfolio_date_data,
        'portfolio_buy_data': portfolio_buy_data,
        'portfolio_sell_data': portfolio_sell_data,
    }
    return HttpResponse(template.render(context, request))
def trading(request):
    proxy = {'http': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280'}
    #print(binance.build_ohlcv('ADA/BNB', '5m', '2150000000000', '50'))
    template = loader.get_template('pages/user/html/trading.html')
    conn = mysql.connector.Connect(host='localhost', user='cso', password='', database='trading_bot')
    c = conn.cursor(buffered=True)
    user_id = str(request.session['user_id'])
    if not user_id:
        return HttpResponseRedirect(reverse('index'))
    print(request.session['user_id'])
    c.execute("""select * from bot where user_id=%s order by bot_kind, bot_type, bot_status""", (user_id,))
    bot_list = c.fetchall()
    conn.commit()
    context = {}
    rsi = 0
    k = 0
    d = 0
    sum_plus = 0
    sum_minus = 0
    candle_data = []
    temp_data = []
    value_dif = []

    chart_data = []
    result_list = []
    rsi_min = 0
    rsi_max = 0
    rsi_prev_min = 0
    rsi_prev_max = 0
    stoch_data = []
    stoch_k = []
    stoch_d = []
    stoch_min = []
    stoch_max = []
    k_data = []
    stoch_prev_min = 0
    stoch_prev_max = 0
    k_max = 0
    k_min = 0

    ema_high_max = 0
    ema_high_min = 0
    ema_dif1 = 0
    ema_dif2 = 0
    # ema_length = 0
    last_sell_price = 0
    last_buy_price = 0
    chartData = []
    chartData_index = 0
    trade_list = []
    indicator_trade_list = []
    temp = []
    gain = []
    loss = []
    long_price = 0
    short_price = 0
    trade_result = ""
    v = str(datetime.datetime.now())
    date_now = v[:10]
    # v = "2018:01:01 06-05-03"
    y1 = y2 = v[:4]
    m1 = m2 = v[5:7]
    d1 = d2 = v[8:10]
    h1 = v[11:13]
    n1 = v[14:16]
    s1 = v[17:19]
    h2 = "00"
    n2 = "00"
    s2 = "00"
    if int(m2) > 2:
        m2 = str(int(m2) - 2)
    else:
        y2 = str(int(y2) - 1)
        m2 = str(int(m2) + 10)
    indicator_show = False
    arbitrage_show = False
    ml_show = False
    market_show = False
    #print(binance.fetch_ohlcv('BTC/USDT', '2h', 1525950000000, 1000))
    # print(bittrex.load_markets())
    # print(bittrex.fetch_ohlcv('USDT/BTC', '2h', 1525950000000, 1000))
    #print(cryptopia.fetch_ohlcv('BTC/USDT', '2h', 1525950000000, 1000))
    #cex.options['fetchOHLCVWarning'] = False
    #print(cex.fetch_ohlcv('BTC/USD', '1m', 1525950000000, 1000))
    #print(hitbtc.fetch_ohlcv('BTC/USDT', '5m', 1525950000000, 1000))
    #okex = ccxt.okex({
    #    'apiKey': '2060f308-6e2d-42b9-822b-b06df5ae3de9',
    #    'secret': '1F8EE9EEC0155EEEB534AFBEA4273A98'
    #})
    #print(okex.fetch_ohlcv('BTC/USDT', '15m', 1525950000000))
    #context = {'bot_list': bot_list}
    #return HttpResponse(template.render(context, request))
    if request.method == "POST":
        bot_id = request.POST['bot_id']
        c.execute("""select * from bot where absID=%s""", (bot_id,))
        bot = c.fetchone()
        conn.commit()
        bot_kind = bot[3]
        interval = bot[35]
        interval1 = ""
        if interval == "1m":
            interval1 = 60000
        if interval == "5m":
            interval1 = 300000
        elif interval == "15m":
            interval1 = 900000
        elif interval == "30m":
            interval1 = 1800000
        elif interval == "1h":
            interval1 = 3600000
        elif interval == "2h":
            interval1 = 7200000
        elif interval == "4h":
            interval1 = 14400000
        elif interval == "1d":
            interval1 == 86400000
        date_to = datetime.datetime(int(y1), int(m1), int(d1), int(h1), int(n1), int(s1))
        date_from = datetime.datetime(int(y2), int(m2), int(d2), int(h2), int(n2), int(s2))
        print(date_from)
        print(date_to)
        bot_id = str(bot[0])
        bot_name = str(bot[1])
        base_currency = str(bot[8])
        selected_coin = str(bot[9])
        coin_pair = selected_coin + "/" + base_currency
        buy_higher = str(bot[11])
        sell_cheaper = str(bot[12])
        profit = float(bot[15])
        stop_loss = float(bot[16])
        stay_profitable = str(bot[14])
        double_fee = str(bot[13])
        trading_volume = float(bot[10])
        exchange_fee = 0.0
        indicator_profit = 0
        total_profit = 0
        total_trade_number = 0
        total_win = 0
        max_drawdown = 0
        profit_sum = 0
        profit_min = 0
        profit_max = 0
        exchange_obj = None
        c.execute("""delete from backtest where bot_id=%s """, (bot_id, ))
        #c.execute("""delete from backtest_balance where bot_id=%s """, (bot_id,))
        conn.commit()
        if bot_kind == "Indicator RSI Bot":
            indicator_data = []
            indicator_parameter = []
            exchange = str(bot[6])
            rsi_top = float(bot[24])
            rsi_bottom = float(bot[25])
            rsi_length = int(bot[23])
            date_from = int(time.mktime(date_from.timetuple()) * 1000) - rsi_length * interval1
            date_to = int(time.mktime(date_to.timetuple()) * 1000)
            if exchange == "binance":
                c.execute(" select api_key, secret from exchange_info where user_id=%s and exchange=%s",
                          (user_id, 'binance'))
                key_data = c.fetchone()
                api = key_data[0]
                secret = key_data[1]
                exchange_obj = ccxt.binance({
                    'proxies': {
                        'http': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                        'https': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                    },
                    'apiKey': api,
                    'secret': secret,
                })
                get_data_continue = True

                # exchange_obj.proxy = 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280'
                while get_data_continue:
                    temp_data = exchange_obj.fetch_ohlcv(coin_pair, interval, int(date_from), 1000)
                    chart_data.extend(temp_data)
                    date_from = temp_data[len(temp_data) - 1][0] + 1000
                    if int(temp_data[len(temp_data) - 1][0]) >= (int(date_to) - int(interval1)):
                        get_data_continue = False
            elif exchange == "cryptopia":
                c.execute(" select api_key, secret from exchange_info where user_id=%s and exchange=%s",
                          (user_id, "cryptopia"))
                key_data = c.fetchone()
                api = key_data[0]
                secret = key_data[1]
                exchange_obj = ccxt.cryptopia({
                    'proxies': {
                        'http': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                        'https': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                    },
                    'apiKey': api,
                    'secret': secret,
                })
                # exchange_obj.proxy = 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280'
                exchange_obj.has['fetchOHLCV'] = 'emulated'
                chart_data = exchange_obj.fetch_ohlcv(coin_pair, interval)
            elif exchange == "cexio":
                c.execute(" select api_key, secret from exchange_info where user_id=%s and exchange=%s",
                          (user_id, "cexio"))
                key_data = c.fetchone()
                api = key_data[0]
                secret = key_data[1]
                exchange_obj = ccxt.cex({
                    'proxies': {
                        'http': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                        'https': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                    },
                    'apiKey': api,
                    'secret': secret,
                })
                # exchange_obj.proxy = 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280'
                exchange_obj.has['fetchOHLCV'] = 'emulated'
                chart_data = exchange_obj.fetch_ohlcv(coin_pair, interval)

            elif exchange == "bittrex":
                c.execute(" select api_key, secret from exchange_info where user_id=%s and exchange=%s",
                          (user_id, "bittrex"))
                key_data = c.fetchone()
                api = key_data[0]
                secret = key_data[1]
                exchange_obj = ccxt.bittrex({
                    'proxies': {
                        'http': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                        'https': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                    },
                    'apiKey': api,
                    'secret': secret,
                })
                get_data_continue = True
                while get_data_continue:
                    temp_data = exchange_obj.fetch_ohlcv(coin_pair, interval, int(date_from), 1000)
                    chart_data.extend(temp_data)
                    print(date_from)
                    print(temp_data)
                    print(len(temp_data))
                    print(temp_data[len(temp_data) - 1][0])
                    print(date_to)
                    print(interval1)
                    date_from = temp_data[len(temp_data) - 1][0] + 1000
                    if int(temp_data[len(temp_data) - 1][0]) >= (int(date_to) - int(interval1)):
                        get_data_continue = False
            elif exchange == "hitbtc":
                c.execute(" select api_key, secret from exchange_info where user_id=%s and exchange=%s",
                          (user_id, "hitbtc"))
                key_data = c.fetchone()
                api = key_data[0]
                secret = key_data[1]
                exchange_obj = ccxt.hitbtc2({
                    'proxies': {
                        'http': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                        'https': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                    },
                    'secret': secret,
                })
                get_data_continue = True
                while get_data_continue:
                    temp_data = exchange_obj.fetch_ohlcv(coin_pair, interval, int(date_from), 1000)
                    chart_data.extend(temp_data)
                    print(date_from)
                    print(temp_data)
                    print(len(temp_data))
                    print(temp_data[len(temp_data) - 1][0])
                    print(date_to)
                    print(temp_data[len(temp_data) - 1][0])
                    print(interval1)
                    date_from = temp_data[len(temp_data) - 1][0] + 1000
                    if int(temp_data[len(temp_data) - 1][0]) >= (int(date_to) - int(interval1)):
                        get_data_continue = False
            elif exchange == "okex":
                c.execute(" select api_key, secret from exchange_info where user_id=%s and exchange=%s",
                          (user_id, "okex"))
                key_data = c.fetchone()
                api = key_data[0]
                secret = key_data[1]
                exchange_obj = ccxt.okex({
                    'proxies': {
                        'http': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                        'https': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                    },
                    'apiKey': api,
                    'secret': secret,
                })
                # exchange_obj.has['fetchOHLCV'] = 'emulated'
                print(exchange_obj.last_http_response)
                get_data_continue = True
                while get_data_continue:
                    temp_data = exchange_obj.fetch_ohlcv(coin_pair, interval)
                    chart_data.extend(temp_data)
                    print(date_from)
                    print(temp_data)
                    print(len(temp_data))
                    print(temp_data[len(temp_data) - 1][0])
                    print(date_to)
                    print(interval1)
                    date_from = temp_data[len(temp_data) - 1][0] + 1000
                    if int(temp_data[len(temp_data) - 1][0]) >= (int(date_to) - int(interval1)):
                        get_data_continue = False
            num1 = len(chart_data)
            for i in range(0, num1):
                data = chart_data[i]
                data.pop(5)
                t1 = data[0] / 1000
                temp_data.append([data[1], data[2], data[3], data[4]])
                if rsi > 0:
                    value_dif.append(temp_data[rsi][3] - temp_data[rsi - 1][3])
                if rsi > (rsi_length - 1):
                    if rsi == rsi_length:
                        for j in range(0, rsi):
                            if value_dif[j] > 0:
                                sum_plus += value_dif[j]
                            else:
                                sum_minus += value_dif[j]
                        gain.append(float(sum_plus) / float(rsi_length))
                        loss.append(float(abs(sum_minus)) / float(rsi_length))
                        # rsi_data.append(float(sum_plus) / (float(sum_plus) - float(sum_minus)) * 100)
                        indicator_data.append([data[0], float(100 - 100 / (1 + float(float(gain[rsi - rsi_length]) /
                                                                           float(loss[rsi - rsi_length]))))])
                        chartData.append(data)

                    elif rsi > rsi_length:
                        if value_dif[rsi - 1] > 0:
                            gain.append(float(((rsi_length - 1) * float(gain[rsi - rsi_length - 1]) + float(
                                value_dif[rsi - 1])) / rsi_length))
                            loss.append(float(((rsi_length - 1) * float(loss[rsi - rsi_length - 1]) / rsi_length)))
                        elif value_dif[rsi - 1] < 0:
                            gain.append(float(((rsi_length - 1) * float(gain[rsi - rsi_length - 1])) / rsi_length))
                            loss.append(float(((rsi_length - 1) * float(loss[rsi - rsi_length - 1]) + float(
                                abs(value_dif[rsi - 1]))) / rsi_length))
                        elif value_dif[rsi - 1] == 0:
                            gain.append(float(((rsi_length - 1) * float(gain[rsi - rsi_length - 1])) / rsi_length))
                            loss.append(float(((rsi_length - 1) * float(loss[rsi - rsi_length - 1]) / rsi_length)))
                        # rsi_data.append(float(100 - 100 / (1 + float(float(gain[rsi - rsi_length]) / float(loss[rsi - rsi_length])))))
                        # t = float(sum_plus) / (float(sum_plus) - float(sum_minus)) * 100
                        t = float(100 - 100 / (1 + float(
                                float(gain[rsi - rsi_length]) / float(loss[rsi - rsi_length]))))
                        indicator_data.append([data[0], t])
                        chartData.append(data)
                    chartData_index += 1
                    if chartData_index > 0:
                        #print(chartData_index)
                        #print(rsi_top)
                        #print(indicator_data[chartData_index-1][1])
                        if indicator_data[chartData_index - 1][1] <= rsi_bottom:
                            #print("come here")
                            exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'sell', trading_volume,
                                                                      data[4], 'maker')
                            exchange_fee = float(data[4]) * float(exchange_fee['rate'])*trading_volume
                            trade_result = rsi_backtest(user_id, bot_id, 'bottom', data[4], last_buy_price, last_sell_price, buy_higher,
                                              sell_cheaper, trading_volume, stay_profitable, double_fee, exchange_fee, t1)
                        elif indicator_data[chartData_index - 1][1] >= rsi_top:
                            exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'sell', trading_volume,
                                                                      data[4], 'maker')
                            exchange_fee = float(data[4]) * float(exchange_fee['rate'])*trading_volume
                            trade_result = rsi_backtest(user_id, bot_id, 'top', data[4], last_buy_price, last_sell_price, buy_higher,
                                              sell_cheaper, trading_volume, stay_profitable, double_fee, exchange_fee, t1)
                    if trade_result.find("open long"):
                        long_price = data[4]
                        last_buy_price = data[4]
                        trade_result = ""
                        # short_price = 0
                    if trade_result.find("close long"):
                        long_price = 0
                        last_sell_price = data[4]
                        trade_result = ""
                    if profit > 0:
                        if long_price > 0:
                            if float(data[4] >= (float(long_price) + float(profit) * float(long_price) / 100)):
                                print("close long profit")
                                print(data[4])
                                # print((float(long_price) + float(profit)*float(long_price)/100))
                                # print((float(long_price) - float(stop_loss)*float(long_price)/100))
                                order_time = datetime.datetime.fromtimestamp(t1)
                                c.execute(
                                    """update backtest set order_status='complete', order_type='sell', sell_price=%s, sell_time=%s where position='long' and order_type='buy' and order_status='create'""",
                                    (data[4], order_time,))
                                conn.commit()
                                long_price = 0
                                last_buy_price = data[4]
                                trade_result = "close long"
                    if stop_loss > 0:
                        if long_price > 0:
                            if float(data[4]) <= (float(long_price) - float(stop_loss) * float(long_price) / 100):
                                print("close long stoploss")
                                print(data[4])
                                # print((float(long_price) + float(profit)*float(long_price)/100))
                                # print((float(long_price) - float(stop_loss)*float(long_price)/100))
                                order_time = datetime.datetime.fromtimestamp(t1)
                                c.execute(
                                    """update backtest set order_status='complete', order_type='sell', sell_price=%s, sell_time=%s where position='long' and order_type='buy' and order_status='create'""",
                                    (data[4], order_time,))
                                conn.commit()
                                long_price = 0
                                last_buy_price = data[4]
                                trade_result = "close long"

                sum_minus = 0
                sum_plus = 0

                rsi += 1
                conn.commit()
            chartData_index = 0

            conn.commit()
            c.execute(
                """select backtest.*, bot.trading_volume, bot.bot_name from backtest INNER JOIN bot ON bot.absID=backtest.bot_id where backtest.user_id=%s order by buy_time""",
                (user_id,))
            list1 = c.fetchall()
            conn.commit()
            trade_index = 1
            for trade in list1:
                if trade[4] == "sell" and trade[5] == "complete":
                    print("list in")
                    trade_list.append([trade_index, trade[11], 'Open Long', trade[6], trade[8], trade[10], ''])
                    profit = float(trade[10]) * (float(trade[9]) - float(trade[8]))
                    trade_index += 1
                    trade_list.append([trade_index, trade[11], 'Close Long', trade[7], trade[9], trade[10], profit])
                    trade_index += 1
                    if indicator_profit == 0:
                        indicator_profit = 100 * (float(trade[9]) - float(trade[8])) / float(trade[9])
                    elif indicator_profit > 0:
                        if indicator_profit < 100 * (float(trade[9]) - float(trade[8])) / float(trade[9]):
                            indicator_profit = 100 * (float(trade[9]) - float(trade[8])) / float(trade[9])
            title = bot_name + "-" + bot_kind + "(Coin Pair=" + selected_coin + "/" + base_currency + ")"
            c.execute("select backtest.buy_price, backtest.sell_price, backtest.order_status, bot.trading_volume from backtest inner join bot on bot.absID=backtest.bot_id ")
            r1 = c.fetchall()
            conn.commit()
            if len(r1) > 0:
                for i in r1:
                    if i[2] == "complete":
                        total_trade_number += 2
                        total_profit += (float(i[1]) - float(i[0])) * float(i[3])
                        if (float(i[1]) - float(i[0])) > 0:
                            profit_sum += (float(i[1]) - float(i[0])) * float(i[3])
                        if (float(i[1]) - float(i[0])) > profit_max:
                            profit_max = (float(i[1]) - float(i[0]))
                        if profit_min == 0:
                            profit_min = (float(i[1]) - float(i[0]))
                        else:
                            if (float(i[1]) - float(i[0])) < profit_min:
                                profit_min = (float(i[1]) - float(i[0]))
                    else:
                        total_trade_number += 1


                total_win = float(100*total_profit/profit_sum)
                max_drawdown = profit_max - profit_min
            context = {
                'bot_kind': 'rsi',
                'title': title,
                'rsi_top': rsi_top,
                'rsi_bottom': rsi_bottom,
                'chart_data': chartData,
                'indicator_chart_data': indicator_data,
                'indicator_trade_list': indicator_trade_list,
                'indicator_profit': indicator_profit,
                'trade_list': trade_list,
                'total_profit': round(total_profit, 2),
                'total_trade_number': total_trade_number,
                'total_win': round(total_win, 2),
                'max_drawdown': round(max_drawdown, 2)
            }
            #print(chartData)
            #print(indicator_data)
            return JsonResponse(context)
            #return HttpResponse(template.render(context, request))
        if bot_kind == "Indicator MACD Bot":
            macd_data = []
            macd_long_data = []
            macd_short_data = []
            macd_signal_data = []
            macd_chart = []
            macd_signal_chart = []
            macd_long = int(bot[26])
            macd_short = int(bot[27])
            macd_signal = int(bot[28])
            macd_index = 0
            temp_data1 = 0
            exchange = str(bot[6])
            print((macd_long + macd_signal)*interval1)
            date_from = int(time.mktime(date_from.timetuple()) * 1000) - ((macd_long + macd_signal) * (interval1))
            date_to = int(time.mktime(date_to.timetuple()) * 1000)
            if exchange == "binance":
                c.execute(" select api_key, secret from exchange_info where user_id=%s and exchange=%s",
                          (user_id, 'binance'))
                key_data = c.fetchone()
                api = key_data[0]
                secret = key_data[1]
                exchange_obj = ccxt.binance({
                    'proxies': {
                        'http': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                        'https': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                    },
                    'apiKey': api,
                    'secret': secret,
                })
                get_data_continue = True

                #exchange_obj.proxy = 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280'
                while get_data_continue:
                    temp_data = exchange_obj.fetch_ohlcv(coin_pair, interval, int(date_from), 1000)
                    chart_data.extend(temp_data)
                    date_from = temp_data[len(temp_data) - 1][0] + 1000
                    if int(temp_data[len(temp_data) - 1][0]) >= (int(date_to) - int(interval1)):
                        get_data_continue = False
            elif exchange == "cryptopia":
                c.execute(" select api_key, secret from exchange_info where user_id=%s and exchange=%s",
                          (user_id, "cryptopia"))
                key_data = c.fetchone()
                api = key_data[0]
                secret = key_data[1]
                exchange_obj = ccxt.cryptopia({
                    'proxies': {
                        'http': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                        'https': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                    },
                    'apiKey': api,
                    'secret': secret,
                })
                # exchange_obj.proxy = 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280'
                exchange_obj.has['fetchOHLCV'] = 'emulated'
                chart_data = exchange_obj.fetch_ohlcv(coin_pair, interval)
            elif exchange == "cexio":
                c.execute(" select api_key, secret from exchange_info where user_id=%s and exchange=%s",
                          (user_id, "cexio"))
                key_data = c.fetchone()
                api = key_data[0]
                secret = key_data[1]
                exchange_obj = ccxt.cex({
                    'proxies': {
                        'http': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                        'https': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                    },
                    'apiKey': api,
                    'secret': secret,
                })
                # exchange_obj.proxy = 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280'
                exchange_obj.has['fetchOHLCV'] = 'emulated'
                chart_data = exchange_obj.fetch_ohlcv(coin_pair, interval)

            elif exchange == "bittrex":
                c.execute(" select api_key, secret from exchange_info where user_id=%s and exchange=%s",
                          (user_id, "bittrex"))
                key_data = c.fetchone()
                api = key_data[0]
                secret = key_data[1]
                exchange_obj = ccxt.bittrex({
                    'proxies': {
                        'http': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                        'https': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                    },
                    'apiKey': api,
                    'secret': secret,
                })
                get_data_continue = True
                while get_data_continue:
                    temp_data = exchange_obj.fetch_ohlcv(coin_pair, interval, int(date_from), 1000)
                    chart_data.extend(temp_data)
                    print(date_from)
                    print(temp_data)
                    print(len(temp_data))
                    print(temp_data[len(temp_data) - 1][0])
                    print(date_to)
                    print(interval1)
                    date_from = temp_data[len(temp_data) - 1][0] + 1000
                    if int(temp_data[len(temp_data) - 1][0]) >= (int(date_to) - int(interval1)):
                        get_data_continue = False
            elif exchange == "hitbtc":
                c.execute(" select api_key, secret from exchange_info where user_id=%s and exchange=%s",
                          (user_id, "hitbtc"))
                key_data = c.fetchone()
                api = key_data[0]
                secret = key_data[1]
                exchange_obj = ccxt.hitbtc2({
                    'proxies': {
                        'http': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                        'https': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                    },
                    'secret': secret,
                })
                get_data_continue = True
                while get_data_continue:
                    temp_data = exchange_obj.fetch_ohlcv(coin_pair, interval, int(date_from), 1000)
                    chart_data.extend(temp_data)
                    print(date_from)
                    print(temp_data)
                    print(len(temp_data))
                    print(temp_data[len(temp_data) - 1][0])
                    print(date_to)
                    print(temp_data[len(temp_data) - 1][0])
                    print(interval1)
                    date_from = temp_data[len(temp_data) - 1][0] + 1000
                    if int(temp_data[len(temp_data) - 1][0]) >= (int(date_to) - int(interval1)):
                        get_data_continue = False
            elif exchange == "okex":
                c.execute(" select api_key, secret from exchange_info where user_id=%s and exchange=%s",
                          (user_id, "okex"))
                key_data = c.fetchone()
                api = key_data[0]
                secret = key_data[1]
                exchange_obj = ccxt.okex({
                    'proxies': {
                        'http': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                        'https': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                    },
                    'apiKey': api,
                    'secret': secret,
                })
                #exchange_obj.has['fetchOHLCV'] = 'emulated'
                print(exchange_obj.last_http_response)
                get_data_continue = True
                while get_data_continue:
                    temp_data = exchange_obj.fetch_ohlcv(coin_pair, interval)
                    chart_data.extend(temp_data)
                    print(date_from)
                    print(temp_data)
                    print(len(temp_data))
                    print(temp_data[len(temp_data) - 1][0])
                    print(date_to)
                    print(interval1)
                    date_from = temp_data[len(temp_data) - 1][0] + 1000
                    if int(temp_data[len(temp_data) - 1][0]) >= (int(date_to) - int(interval1)):
                        get_data_continue = False
            print(chart_data)
            num1 = len(chart_data)
            print(num1)
            for i in range(0, num1):
                data = chart_data[i]
                data.pop(5)
                t1 = data[0] / 1000
                long_k = float(2/float(macd_long + 1))
                short_k = float(2/float(macd_short + 1))
                if i == 0:
                    macd_long_data.append(data[4])
                    macd_short_data.append(data[4])
                if i > 0:
                    macd_long_data.append(float(data[4] * float(long_k)) + float(macd_long_data[i-1]) * float(1-float(long_k)))
                    macd_short_data.append(float(data[4] * float(short_k)) + float(macd_short_data[i-1]) * float(1-float(short_k)))
                    #print(macd_long_data[i])
                    #print(macd_short_data[i])
                if i >= macd_long:
                    macd_data.append(float(macd_short_data[i] - macd_long_data[i]))
                if i >= (macd_long + macd_signal - 1):
                    for k in range(i-macd_long-macd_signal+1, i-macd_long+1):
                        temp_data1 += macd_data[k]
                    #macd_signal_data.append(float(temp_data1 / macd_signal))
                    #print("here")
                    #print(str(i))
                    #print(str(macd_long + macd_signal - 1))
                    #print(macd_data[i-macd_long])
                    macd_chart.append([data[0], macd_data[i-macd_long]])
                    macd_signal_chart.append([data[0], float(temp_data1 / macd_signal)])
                    chartData.append(data)
                    macd_index += 1
                    temp_data1 = 0

                if macd_index > 1:
                    #print(macd_index)
                    #print(macd_chart)
                    #print(macd_signal_chart)
                    m1 = macd_chart[macd_index - 1][1]
                    m2 = macd_chart[macd_index - 2][1]
                    s1 = macd_signal_chart[macd_index - 1][1]
                    s2 = macd_signal_chart[macd_index - 2][1]
                    if m1 > m2:
                        if s1 > s2:
                            if ((m1 > s1 and s2 > m2) or (s1 > m1 and m2 > s2)):
                                exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'buy', trading_volume, data[4], 'maker')
                                exchange_fee = float(data[4]) * float(exchange_fee['rate'])*trading_volume
                                print(exchange_fee)
                                trade_result = macd_backtest(user_id, bot_id, "up_trend", data[4], last_buy_price, last_sell_price,
                                    buy_higher, sell_cheaper, trading_volume, stay_profitable, double_fee, exchange_fee, t1)
                        if s1 < s2:
                            if ((s2 > m2 and s2 < m1) or (s2 > m1 and s1 < m1)):
                                exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'buy', trading_volume, data[4], 'maker')
                                exchange_fee = float(data[4]) * float(exchange_fee['rate'])*trading_volume
                                print(exchange_fee)
                                trade_result = macd_backtest(user_id, bot_id, "up_trend", data[4], last_buy_price, last_sell_price,
                                    buy_higher, sell_cheaper, trading_volume, stay_profitable, double_fee, exchange_fee, t1)
                    elif m1 < m2:
                        if s1 > s2:
                            if ((s2 > m1 and s2 < m2) or (s1 > m1 and s1 <m2)):
                                exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'sell', trading_volume,
                                                                          data[4], 'maker')
                                exchange_fee = float(data[4]) * float(exchange_fee['rate'])
                                print(exchange_fee)
                                trade_result = macd_backtest(user_id, bot_id, "down_trend", data[4], last_buy_price, last_sell_price, buy_higher, sell_cheaper, trading_volume, stay_profitable, double_fee, exchange_fee, t1)
                        if s1 < s2:
                            if ((s2 > m2 and m1 > s1) or (s2 < m2 and s1 > m1)):
                                exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'sell', trading_volume,
                                                                          data[4], 'maker')
                                exchange_fee = float(data[4]) * float(exchange_fee['rate'])
                                print(exchange_fee)
                                trade_result = macd_backtest(user_id, bot_id, "down_trend", data[4], last_buy_price, last_sell_price,
                                    buy_higher, sell_cheaper, trading_volume, stay_profitable, double_fee, exchange_fee, t1)
                if trade_result.find("open long"):
                    long_price = data[4]
                    last_buy_price = data[4]
                    trade_result = ""
                if trade_result.find("close long"):
                    long_price = 0
                    last_sell_price = data[4]
                    trade_result = ""
                if profit > 0:
                    if long_price > 0:
                        if float(data[4] >= (float(long_price) + float(profit) * float(long_price) / 100)):
                            print("close long profit")
                            print(data[4])
                            # print((float(long_price) + float(profit)*float(long_price)/100))
                            # print((float(long_price) - float(stop_loss)*float(long_price)/100))
                            order_time = datetime.datetime.fromtimestamp(t1)
                            c.execute(
                                """update backtest set order_status='complete', order_type='sell', sell_price=%s, sell_time=%s where position='long' and order_type='buy' and order_status='create'""",
                                (data[4], order_time,))
                            conn.commit()
                            long_price = 0
                            last_buy_price = 0
                            last_sell_price = data[4]
                            trade_result = "close long"

                if stop_loss > 0:
                    if long_price > 0:
                        if float(data[4]) <= (float(long_price) - float(stop_loss) * float(long_price) / 100):
                            print("close long stoploss")
                            print(data[4])
                            # print((float(long_price) + float(profit)*float(long_price)/100))
                            # print((float(long_price) - float(stop_loss)*float(long_price)/100))
                            order_time = datetime.datetime.fromtimestamp(t1)
                            c.execute(
                                """update backtest set order_status='complete', order_type='sell', sell_price=%s, sell_time=%s where position='long' and order_type='buy' and order_status='create'""",
                                (data[4], order_time,))
                            conn.commit()
                            long_price = 0
                            last_buy_price = 0
                            last_sell_price = data[4]
                            trade_result = "close long"
            conn.commit()
            c.execute(
                """select backtest.*, bot.trading_volume, bot.bot_name from backtest INNER JOIN bot ON bot.absID=backtest.bot_id where backtest.user_id=%s order by buy_time""",
                (user_id,))
            list1 = c.fetchall()
            trade_index = 1
            for trade in list1:
                if trade[4] == "sell" and trade[5] == "complete":
                    print("list in")
                    trade_list.append([trade_index, trade[11], 'Open Long', trade[6], trade[8], trade[10], ''])
                    profit = float(trade[10]) * (float(trade[9]) - float(trade[8]))
                    trade_index += 1
                    trade_list.append([trade_index, trade[11], 'Close Long', trade[7], trade[9], trade[10], profit])
                    trade_index += 1
                    if indicator_profit == 0:
                        indicator_profit = 100 * (float(trade[9]) - float(trade[8])) / float(trade[9])
                    elif indicator_profit > 0:
                        if indicator_profit < 100 * (float(trade[9]) - float(trade[8])) / float(trade[9]):
                            indicator_profit = 100 * (float(trade[9]) - float(trade[8])) / float(trade[9])
            title = bot_name + "-" + bot_kind + "(Coin Pair=" + selected_coin + "/" + base_currency + ")"
            #print(chartData)
            #print(macd_chart)
            #print(macd_signal_chart)
            #print(macd_short)
            #print(macd_long)
            #print(macd_signal)
            c.execute(
                "select backtest.buy_price, backtest.sell_price, backtest.order_status, bot.trading_volume from backtest inner join bot on bot.absID=backtest.bot_id ")
            r1 = c.fetchall()
            conn.commit()
            if len(r1) > 0:
                for i in r1:
                    if i[2] == "complete":
                        total_trade_number += 2
                        total_profit += (float(i[1]) - float(i[0])) * float(i[3])
                        if (float(i[1]) - float(i[0])) > 0:
                            profit_sum += (float(i[1]) - float(i[0])) * float(i[3])
                        if (float(i[1]) - float(i[0])) > profit_max:
                            profit_max = (float(i[1]) - float(i[0]))
                        if profit_min == 0:
                            profit_min = (float(i[1]) - float(i[0]))
                        else:
                            if (float(i[1]) - float(i[0])) < profit_min:
                                profit_min = (float(i[1]) - float(i[0]))
                    else:
                        total_trade_number += 1


                total_win = float(100*total_profit/profit_sum)
                max_drawdown = profit_max - profit_min
            context = {
                'bot_kind': 'macd',
                'title': title,
                'macd_fast': macd_short,
                'macd_slow': macd_long,
                'macd_signal': macd_signal,
                'chart_data': chartData,
                'macd_chart': macd_chart,
                'macd_signal_chart': macd_signal_chart,
                'indicator_profit': indicator_profit,
                'trade_list': trade_list,
                'total_profit': round(total_profit, 2),
                'total_trade_number': total_trade_number,
                'total_win': round(total_win, 2),
                'max_drawdown': round(max_drawdown, 2)
            }
            return JsonResponse(context)
        if bot_kind == "Indicator BB Bot":
            middle_data = []
            upper_data = []
            lower_data = []
            bb_temp = []
            ave = 0
            sd = 0
            bb_index = 0
            period = int(bot[29])
            upper = float(bot[30])
            lower = float(bot[31])
            exchange = str(bot[6])
            date_from = int(time.mktime(date_from.timetuple()) * 1000) - (period) * (interval1)
            date_to = int(time.mktime(date_to.timetuple()) * 1000)
            if exchange == "binance":
                c.execute(" select api_key, secret from exchange_info where user_id=%s and exchange=%s",
                          (user_id, 'binance'))
                key_data = c.fetchone()
                api = key_data[0]
                secret = key_data[1]
                exchange_obj = ccxt.binance({
                    'proxies': {
                        'http': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                        'https': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                    },
                    'apiKey': api,
                    'secret': secret,
                })
                get_data_continue = True

                # exchange_obj.proxy = 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280'
                while get_data_continue:
                    temp_data = exchange_obj.fetch_ohlcv(coin_pair, interval, int(date_from), 1000)
                    chart_data.extend(temp_data)
                    date_from = temp_data[len(temp_data) - 1][0] + 1000
                    if int(temp_data[len(temp_data) - 1][0]) >= (int(date_to) - int(interval1)):
                        get_data_continue = False

            elif exchange == "cryptopia":
                c.execute(" select api_key, secret from exchange_info where user_id=%s and exchange=%s",
                          (user_id, "cryptopia"))
                key_data = c.fetchone()
                api = key_data[0]
                secret = key_data[1]
                exchange_obj = ccxt.cryptopia({
                    'proxies': {
                        'http': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                        'https': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                    },
                    'apiKey': api,
                    'secret': secret,
                })
                # exchange_obj.proxy = 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280'
                exchange_obj.has['fetchOHLCV'] = 'emulated'
                chart_data = exchange_obj.fetch_ohlcv(coin_pair, interval)
            elif exchange == "cexio":
                c.execute(" select api_key, secret from exchange_info where user_id=%s and exchange=%s",
                          (user_id, "cexio"))
                key_data = c.fetchone()
                api = key_data[0]
                secret = key_data[1]
                exchange_obj = ccxt.cex({
                    'proxies': {
                        'http': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                        'https': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                    },
                    'apiKey': api,
                    'secret': secret,
                })
                # exchange_obj.proxy = 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280'
                exchange_obj.has['fetchOHLCV'] = 'emulated'
                chart_data = exchange_obj.fetch_ohlcv(coin_pair, interval)

            elif exchange == "bittrex":
                c.execute(" select api_key, secret from exchange_info where user_id=%s and exchange=%s",
                          (user_id, "bittrex"))
                key_data = c.fetchone()
                api = key_data[0]
                secret = key_data[1]
                exchange_obj = ccxt.bittrex({
                    'proxies': {
                        'http': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                        'https': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                    },
                    'apiKey': api,
                    'secret': secret,
                })
                get_data_continue = True
                while get_data_continue:
                    temp_data = exchange_obj.fetch_ohlcv(coin_pair, interval, int(date_from), 1000)
                    chart_data.extend(temp_data)
                    print(date_from)
                    print(temp_data)
                    print(len(temp_data))
                    print(temp_data[len(temp_data) - 1][0])
                    print(date_to)
                    print(interval1)
                    date_from = temp_data[len(temp_data) - 1][0] + 1000
                    if int(temp_data[len(temp_data) - 1][0]) >= (int(date_to) - int(interval1)):
                        get_data_continue = False
            elif exchange == "hitbtc":
                c.execute(" select api_key, secret from exchange_info where user_id=%s and exchange=%s",
                          (user_id, "hitbtc"))
                key_data = c.fetchone()
                api = key_data[0]
                secret = key_data[1]
                exchange_obj = ccxt.hitbtc2({
                    'proxies': {
                        'http': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                        'https': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                    },
                    'secret': secret,
                })
                get_data_continue = True
                while get_data_continue:
                    temp_data = exchange_obj.fetch_ohlcv(coin_pair, interval, int(date_from), 1000)
                    chart_data.extend(temp_data)
                    print(date_from)
                    print(temp_data)
                    print(len(temp_data))
                    print(temp_data[len(temp_data) - 1][0])
                    print(date_to)
                    print(temp_data[len(temp_data) - 1][0])
                    print(interval1)
                    date_from = temp_data[len(temp_data) - 1][0] + 1000
                    if int(temp_data[len(temp_data) - 1][0]) >= (int(date_to) - int(interval1)):
                        get_data_continue = False
            elif exchange == "okex":
                c.execute(" select api_key, secret from exchange_info where user_id=%s and exchange=%s",
                          (user_id, "okex"))
                key_data = c.fetchone()
                api = key_data[0]
                secret = key_data[1]
                exchange_obj = ccxt.okex({
                    'proxies': {
                        'http': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                        'https': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                    },
                    'apiKey': api,
                    'secret': secret,
                })
                # exchange_obj.has['fetchOHLCV'] = 'emulated'
                print(exchange_obj.last_http_response)
                get_data_continue = True
                while get_data_continue:
                    temp_data = exchange_obj.fetch_ohlcv(coin_pair, interval)
                    chart_data.extend(temp_data)
                    print(date_from)
                    print(temp_data)
                    print(len(temp_data))
                    print(temp_data[len(temp_data) - 1][0])
                    print(date_to)
                    print(interval1)
                    date_from = temp_data[len(temp_data) - 1][0] + 1000
                    if int(temp_data[len(temp_data) - 1][0]) >= (int(date_to) - int(interval1)):
                        get_data_continue = False
            data_len = len(chart_data)
            print(chart_data)
            print(data_len)
            for i in range(period - 1, data_len):
                data = chart_data[i-period+1]
                data.pop(5)
                t1 = data[0] / 1000
                for k in range(i-period+1, i+1):
                    bb_temp.append(chart_data[k][4])
                ave = np.mean(bb_temp)
                sd = np.std(bb_temp)
                middle_data.append([data[0], ave])
                upper_data.append([data[0], ave+sd*upper])
                lower_data.append([data[0], ave-sd*lower])
                chartData.append(data)
                bb_temp = []

                c.execute(
                    "select buy_price from trading_history where bot_id=%s and buy_price<>'0' order by absID desc",
                    (bot_id,))
                temp = c.fetchone()
                if c.rowcount:
                    last_buy_price = temp[0]
                else:
                    last_buy_price = 0
                conn.commit()
                c.execute(
                    "select sell_price from trading_history where bot_id=%s and sell_price<>'0' order by absID desc",
                    (bot_id,))
                temp = c.fetchone()
                if c.rowcount:
                    last_sell_price = temp[0]
                else:
                    last_sell_price = 0
                conn.commit()

                if data[4] <= (ave-sd*lower):
                    exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'buy', trading_volume, data[4],
                                                              'maker')
                    exchange_fee = float(data[4]) * float(exchange_fee['rate'])*trading_volume
                    test_result = bb_backtest(user_id, bot_id, 'lower', data[4], last_buy_price, last_sell_price, buy_higher,
                                    sell_cheaper, trading_volume, stay_profitable, double_fee, exchange_fee, t1)
                if data[4] >= (ave+sd*upper):
                    exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'sell', trading_volume, data[4],
                                                              'maker')
                    exchange_fee = float(data[4]) * float(exchange_fee['rate'])*trading_volume
                    test_result = bb_backtest(user_id, bot_id, 'upper', data[4], last_buy_price, last_sell_price, buy_higher,
                                              sell_cheaper, trading_volume, stay_profitable, double_fee, exchange_fee, t1)
                #if test_result.find("open long"):
                #    long_price = data[4]
                #    last_buy_price = data[4]
                #    test_result = ""
                #if test_result.find("close long"):
                #    long_price = 0
                #    last_sell_price = data[4]
                #    test_result = ""
                if profit > 0:
                    if long_price > 0:
                        if float(data[4] >= (float(long_price) + float(profit) * float(long_price) / 100)):
                            #print("close long profit")
                            #print(data[4])
                            # print((float(long_price) + float(profit)*float(long_price)/100))
                            # print((float(long_price) - float(stop_loss)*float(long_price)/100))
                            order_time = datetime.datetime.fromtimestamp(t1)
                            c.execute(
                                """update backtest set order_status='complete', order_type='sell', sell_price=%s, sell_time=%s where position='long' and order_type='buy' and order_status='create'""",
                                (data[4], order_time,))
                            conn.commit()
                            long_price = 0
                            last_buy_price = 0
                            last_sell_price = data[4]
                            test_result = "close long"
                if stop_loss > 0:
                    if long_price > 0:
                        if float(data[4]) <= (float(long_price) - float(stop_loss) * float(long_price) / 100):
                            #print("close long stoploss")
                            #print(data[4])
                            # print((float(long_price) + float(profit)*float(long_price)/100))
                            # print((float(long_price) - float(stop_loss)*float(long_price)/100))
                            order_time = datetime.datetime.fromtimestamp(t1)
                            c.execute(
                                """update backtest set order_status='complete', order_type='sell', sell_price=%s, sell_time=%s where position='long' and order_type='buy' and order_status='create'""",
                                (data[4], order_time,))
                            conn.commit()
                            long_price = 0
                            last_buy_price = 0
                            last_sell_price = data[4]
                            test_result = "close long"
            conn.commit()
            c.execute("""select backtest.*, bot.trading_volume, bot.bot_name from backtest INNER JOIN bot ON bot.absID=backtest.bot_id where backtest.user_id=%s order by buy_time""", (user_id,))
            list1 = c.fetchall()
            trade_index = 1
            for trade in list1:
                if trade[4] == "sell" and trade[5] == "complete":
                    print("list in")
                    trade_list.append([trade_index, trade[11], 'Open Long', trade[6], trade[8], trade[10], ''])
                    profit = float(trade[10]) * (float(trade[9]) - float(trade[8]))
                    trade_index += 1
                    trade_list.append([trade_index, trade[11], 'Close Long', trade[7], trade[9], trade[10], profit])
                    trade_index += 1
                    if indicator_profit == 0:
                        indicator_profit = 100 * (float(trade[9]) - float(trade[8])) / float(trade[9])
                    elif indicator_profit > 0:
                        if indicator_profit < 100 * (float(trade[9]) - float(trade[8])) / float(trade[9]):
                            indicator_profit = 100 * (float(trade[9]) - float(trade[8])) / float(trade[9])
            title = bot_name + "-" + bot_kind + "(Coin Pair=" + selected_coin + "/" + base_currency + ")"
            c.execute(
                "select backtest.buy_price, backtest.sell_price, backtest.order_status, bot.trading_volume from backtest inner join bot on bot.absID=backtest.bot_id ")
            r1 = c.fetchall()
            conn.commit()
            if len(r1) > 0:
                for i in r1:
                    if i[2] == "complete":
                        total_trade_number += 2
                        total_profit += (float(i[1]) - float(i[0])) * float(i[3])
                        if (float(i[1]) - float(i[0])) > 0:
                            profit_sum += (float(i[1]) - float(i[0])) * float(i[3])
                        if (float(i[1]) - float(i[0])) > profit_max:
                            profit_max = (float(i[1]) - float(i[0]))
                        if profit_min == 0:
                            profit_min = (float(i[1]) - float(i[0]))
                        else:
                            if (float(i[1]) - float(i[0])) < profit_min:
                                profit_min = (float(i[1]) - float(i[0]))
                    else:
                        total_trade_number += 1


                total_win = float(100*total_profit/profit_sum)
                max_drawdown = profit_max - profit_min
            print(total_trade_number)
            print(total_profit)
            print(total_win)
            print(max_drawdown)
            context = {
                'bot_kind': 'bb',
                'title': title,
                'period': period,
                'upper': upper,
                'lower': lower,
                'chart_data': chartData,
                'middle_data': middle_data,
                'upper_data': upper_data,
                'lower_data': lower_data,
                'trade_list': trade_list,
                'indicator_profit': indicator_trade_list,
                'total_profit': round(total_profit, 2),
                'total_trade_number': total_trade_number,
                'total_win': round(total_win, 2),
                'max_drawdown': round(max_drawdown, 2)
            }
            return JsonResponse(context)

    c.execute("select permission from user where absID=%s", (user_id,))
    r1 = c.fetchone()
    permission = r1[0]
    if bot_list:
        context = {
            'bot_list': bot_list,
            'permission': permission
        }
        #if indicator_show:
        #    context['indicator_chart_data'] = indicator_data
        #    context['indicator_trade_list'] = indicator_trade_list
        #    context['indicator_profit'] = indicator_profit

        return HttpResponse(template.render(context, request))

    context = {
        'permission': permission
    }
    return HttpResponse(template.render(context, request))
def user_setting(request):
    template = loader.get_template('pages/user/html/user_setting.html')
    context = {}
    return HttpResponse(template.render(context, request))
def exchange_info(request):
    template = loader.get_template('pages/user/html/exchange_info.html')
    conn = mysql.connector.Connect(host='localhost', user='cso', password='', database='trading_bot')
    c = conn.cursor(buffered=True)
    user_id = request.session['user_id']
    if request.method == "POST":
        binance_api = request.POST['binance_api']
        binance_secret = request.POST['binance_secret']
        cryptopia_api = request.POST['cryptopia_api']
        cryptopia_secret = request.POST['cryptopia_secret']
        cex_api = request.POST['cex_api']
        cex_secret = request.POST['cex_secret']
        bittrex_api = request.POST['bittrex_api']
        bittrex_secret = request.POST['bittrex_secret']
        hitbtc_api = request.POST['hitbtc_api']
        hitbtc_secret = request.POST['hitbtc_secret']
        okex_api = request.POST['okex_api']
        okex_secret = request.POST['okex_secret']
        quoinex_api = request.POST['quoinex_api']
        quoinex_secret = request.POST['quoinex_secret']
        kraken_api = request.POST['kraken_api']
        kraken_secret = request.POST['kraken_secret']
        c.execute("""select * from exchange_info where user_id=%s""", (user_id,))
        r1 = c.fetchall()
        conn.commit()
        if len(r1) > 0:
            c.execute("update exchange_info set api_key=%s, secret=%s where user_id=%s and exchange='binance'",
                      (binance_api, binance_secret, user_id))

            c.execute("update exchange_info set api_key=%s, secret=%s where user_id=%s and exchange='cryptopia'",
                      (cryptopia_api, cryptopia_secret, user_id))
            c.execute("update exchange_info set api_key=%s, secret=%s where user_id=%s and exchange='cexio'",
                      (cex_api, cex_secret, user_id))
            c.execute("update exchange_info set api_key=%s, secret=%s where user_id=%s and exchange='bittrex'",
                      (bittrex_api, bittrex_secret, user_id))
            c.execute("update exchange_info set api_key=%s, secret=%s where user_id=%s and exchange='hitbtc'",
                      (hitbtc_api, hitbtc_secret, user_id))
            c.execute("update exchange_info set api_key=%s, secret=%s where user_id=%s and exchange='okex'",
                      (okex_api, okex_secret, user_id))
            c.execute("update exchange_info set api_key=%s, secret=%s where user_id=%s and exchange='quoinex'",
                      (quoinex_api, quoinex_secret, user_id))
            c.execute("update exchange_info set api_key=%s, secret=%s where user_id=%s and exchange='kraken'",
                      (kraken_api, kraken_secret, user_id))
            conn.commit()
        else:
            c.execute("insert into `exchange_info` (`user_id`,`exchange`,`api_key`,`secret`) values (%s, %s, %s, %s )",
                      (user_id, 'binance', binance_api, binance_secret))
            c.execute("insert into `exchange_info` (`user_id`,`exchange`,`api_key`,`secret`) values (%s, %s, %s, %s )",
                      (user_id, 'cryptopia', cryptopia_api, cryptopia_secret))
            c.execute("insert into `exchange_info` (`user_id`,`exchange`,`api_key`,`secret`) values (%s, %s, %s, %s )",
                      (user_id, 'cexio', cex_api, cex_secret))
            c.execute("insert into `exchange_info` (`user_id`,`exchange`,`api_key`,`secret`) values (%s, %s, %s, %s )",
                      (user_id, 'bittrex', bittrex_api, bittrex_secret))
            c.execute("insert into `exchange_info` (`user_id`,`exchange`,`api_key`,`secret`) values (%s, %s, %s, %s )",
                      (user_id, 'hitbtc', hitbtc_api, hitbtc_secret))
            c.execute("insert into `exchange_info` (`user_id`,`exchange`,`api_key`,`secret`) values (%s, %s, %s, %s )",
                      (user_id, 'okex', okex_api, okex_secret))
            c.execute("insert into `exchange_info` (`user_id`,`exchange`,`api_key`,`secret`) values (%s, %s, %s, %s )",
                      (user_id, 'quoinex', quoinex_api, quoinex_secret))
            c.execute("insert into `exchange_info` (`user_id`,`exchange`,`api_key`,`secret`) values (%s, %s, %s, %s )",
                      (user_id, '', kraken_api, kraken_secret))
            conn.commit()

    c.execute("select api_key, secret from exchange_info where user_id=%s and exchange='binance'", (user_id,))
    binance_key = c.fetchall()
    c.execute("select api_key, secret from exchange_info where user_id=%s and exchange='cryptopia'", (user_id,))
    cryptopia_key = c.fetchall()
    c.execute("select api_key, secret from exchange_info where user_id=%s and exchange='cexio'", (user_id,))
    cex_key = c.fetchall()
    c.execute("select api_key, secret from exchange_info where user_id=%s and exchange='bittrex'", (user_id,))
    bittrex_key = c.fetchall()
    c.execute("select api_key, secret from exchange_info where user_id=%s and exchange='hitbtc'", (user_id,))
    hitbtc_key = c.fetchall()
    c.execute("select api_key, secret from exchange_info where user_id=%s and exchange='okex'", (user_id,))
    okex_key = c.fetchall()
    c.execute("select api_key, secret from exchange_info where user_id=%s and exchange='quoinex'", (user_id,))
    quoinex_key = c.fetchall()
    c.execute("select api_key, secret from exchange_info where user_id=%s and exchange='kraken'", (user_id,))
    kraken_key = c.fetchall()
    conn.commit()
    conn.close()
    context = {
        'binance_key': binance_key,
        'cryptopia_key': cryptopia_key,
        'cex_key': cex_key,
        'bittrex_key': bittrex_key,
        'hitbtc_key': hitbtc_key,
        'okex_key': okex_key,
        'quoinex_key': quoinex_key,
        'kraken_key': kraken_key
    }
    return HttpResponse(template.render(context, request))

### Admin UI
#@login_required
def doc_manage(request):
    template = loader.get_template('pages/user/html/document_manage.html')
    conn = mysql.connector.Connect(host='localhost', user='cso', password='', database='trading_bot')
    c = conn.cursor(buffered=True)
    result = ""
    if request.method == "POST":
        title_id = request.POST['title_id']
        c.execute("""select title, content from landingpage where title_id=%s""", (title_id,))
        conn.commit()
        sql_result = c.fetchall()
        if len(sql_result) <= 0:
            context = {}
        else:
            context = {
                'title': sql_result[0][0],
                'title_id': title_id,
                'content': sql_result[0][1]}
        print(context)
        return HttpResponse(json.dumps(context), content_type='application/json')
    c.execute("""select title, content from landingpage where title_id='summary' """)
    conn.commit()
    sql_result = c.fetchall()
    if len(sql_result) <= 0:
        context = {}
    else:
        context = {
            'title': sql_result[0][0],
            'title_id': 'summary',
            'content': sql_result[0][1]
        }

    conn.close()
    return HttpResponse(template.render(context, request))

def doc_save(request):
    template = loader.get_template('pages/user/html/document_manage.html')
    conn = mysql.connector.Connect(host='localhost', user='cso', password='', database='trading_bot')
    c = conn.cursor(buffered=True)
    context = {}
    if request.method == "POST":
        title_id = request.POST['title_id']
        title = request.POST['title']
        print(title)
        content = request.POST['doc_content']
        c.execute("""update landingpage set content=%s, title=%s where title_id=%s""", (content, title, title_id))
        conn.commit()
        context = {
            'title': title,
            'title_id': title_id,
            'content': content
        }
    conn.close()
    return HttpResponse(template.render(context, request))

def google_login(request):
    conn = mysql.connector.Connect(host='localhost', user='cso', password='', database='trading_bot')
    c = conn.cursor(buffered=True)
    time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    user_email = str(request.user.email)
    user_last_name = str(request.user.last_name)
    user_first_name = str(request.user.first_name)
    username = str(request.user.profile.user)
    #c.execute("""select permission from user where username=%s and first_name=%s and last_name=%s and email=%s and google_login='on' """, (username, user_first_name, user_last_name, user_email))
    c.execute("""select permission, absID from user where email=%s""", (user_email,))
    result = c.fetchall()
    conn.commit()
    if len(result) > 0:
        if result[0][0] == 1:
            template = loader.get_template('pages/user/html/admin_dashboard.html')
        else:
            template = loader.get_template('pages/user/html/dashboard.html')
        request.session['user_id'] = result[0][1]
        context = {}
        return HttpResponse(template.render(context, request))
    else:
        #data = {'username': username, 'email': user_email, 'password': ''}
        #form = SignupForm(data)
        #user = form.save(commit=True)
        #user.is_active = True
        #user.save
        c.execute("""insert into `user` (`username`,`first_name`,`last_name`,`email`,`google_login`,`permission`, `verify`, `create_date`, `login_date`) values (%s, %s, %s, %s, %s, %s, %s, %s, %s )""", (username, user_first_name, user_last_name, user_email, 'on', '4', 'confirm', time, time))
        conn.commit()
        c.execute("select absID from user where email=%s", (user_email,))
        user_info = c.fetchone()
        conn.commit()
        user_id = user_info[0]
        c.execute("""insert into `exchange_info` (`user_id`, `exchange`) values (%s, %s )""", (user_id, 'binance',))
        c.execute("""insert into `exchange_info` (`user_id`, `exchange`) values (%s, %s )""", (user_id, 'cryptopia',))
        c.execute("""insert into `exchange_info` (`user_id`, `exchange`) values (%s, %s )""", (user_id, 'cexio',))
        c.execute("""insert into `exchange_info` (`user_id`, `exchange`) values (%s, %s )""", (user_id, 'bittrex',))
        c.execute("""insert into `exchange_info` (`user_id`, `exchange`) values (%s, %s )""", (user_id, 'hitbtc',))
        c.execute("""insert into `exchange_info` (`user_id`, `exchange`) values (%s, %s )""", (user_id, 'okex',))
        c.execute("""insert into `exchange_info` (`user_id`, `exchange`) values (%s, %s )""", (user_id, 'quoinex',))
        c.execute("""insert into `exchange_info` (`user_id`, `exchange`) values (%s, %s )""", (user_id, 'kraken',))
        conn.commit()
        conn.close()
        request.session['user_id'] = user_id
        template = loader.get_template('pages/user/html/dashboard.html')
        context = {}
        return HttpResponse(template.render(context, request))
def email_activate(request, uidb64, token):
    print(uidb64)
    print(token)
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        print(uid)
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        username = user.username
        user_email = user.email
        #login(request, user)
        template = loader.get_template('pages/landingpage/login.html')
        conn = mysql.connector.Connect(host='localhost', user='cso', password='', database='trading_bot')
        c = conn.cursor(buffered=True)
        c.execute("update user set verify='confirm' where username=%s and email=%s", (username, user_email))
        conn.commit()
        c.execute("select absID from user where email=%s", (user_email,))
        user_info = c.fetchone()
        conn.commit()
        user_id = user_info[0]
        c.execute("""insert into `exchange_info` (`user_id`, `exchange`) values (%s, %s )""", (user_id, 'binance',))
        c.execute("""insert into `exchange_info` (`user_id`, `exchange`) values (%s, %s )""", (user_id, 'cryptopia',))
        c.execute("""insert into `exchange_info` (`user_id`, `exchange`) values (%s, %s )""", (user_id, 'cexio',))
        c.execute("""insert into `exchange_info` (`user_id`, `exchange`) values (%s, %s )""", (user_id, 'bittrex',))
        c.execute("""insert into `exchange_info` (`user_id`, `exchange`) values (%s, %s )""", (user_id, 'hitbtc',))
        c.execute("""insert into `exchange_info` (`user_id`, `exchange`) values (%s, %s )""", (user_id, 'okex',))
        c.execute("""insert into `exchange_info` (`user_id`, `exchange`) values (%s, %s )""", (user_id, 'quoinex',))
        c.execute("""insert into `exchange_info` (`user_id`, `exchange`) values (%s, %s )""", (user_id, 'kraken',))
        conn.commit()
        conn.close()
        context = {
            'login_error': "Successfuly activate your account! "
        }
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponse('Activation link is invalid!')
def rsi_bot_save(request):
    template = loader.get_template('pages/user/html/trading.html')
    conn = mysql.connector.Connect(host='localhost', user='cso', password='', database='trading_bot')
    c = conn.cursor(buffered=True)
    if request.method == "POST":
        user_id = str(request.session['user_id'])
        bot_name = request.POST['rsi_bot_name']
        #bot_type = request.POST['bot_type']
        exchange1 = request.POST['rsi_exchange']
        base_currency = request.POST['rsi_base_currency']
        selected_coin = request.POST['rsi_selected_coin']
        candle_interval = request.POST['rsi_candle_interval']
        trading_volume = request.POST['rsi_trading_volume']
        rsi_period = request.POST['rsi_period']
        rsi_top = request.POST['rsi_top']
        rsi_bottom = request.POST['rsi_bottom']
        #buy_higher = request.POST['buy_higher']
        #double_fee = request.POST['double_fee']
        #sell_cheaper = request.POST['sell_cheaper']
        #stay_profitable = request.POST['stay_profitable']
        take_profit = request.POST['rsi_take_profit']
        stop_loss = request.POST['rsi_stop_loss']
        trading_number = request.POST['rsi_trading_number']
        #auto_off = request.POST['auto_off']
        trading_from = request.POST['rsi_trading_from']
        trading_to = request.POST['rsi_trading_to']
        param_list = request.POST
        # if param_list.has_key("bot_type"):
        if "rsi_bot_type" in param_list:
            bot_type = "Live"
        else:
            bot_type = "Demo"
        if "rsi_buy_higher" in param_list:
            buy_higher = "On"
        else:
            buy_higher = "Off"
        if "rsi_sell_cheaper" in param_list:
            sell_cheaper = "On"
        else:
            sell_cheaper = "Off"
        if "rsi_double_fee" in param_list:
            double_fee = "On"
        else:
            double_fee = "Off"
        if "rsi_stay_profitable" in param_list:
            stay_profitable = "On"
        else:
            stay_profitable = "Off"
        if "rsi_auto_off" in param_list:
            auto_off = "On"
        else:
            auto_off = "Off"

        c.execute("""insert into `bot` (`user_id`,`bot_name`,`bot_type`, `bot_kind`, `exchange1`,`base_currency`,
                  `selected_coin`, `trading_volume`, `rsi_period`, `rsi_top`, `rsi_bottom`, `buy_higher`, 
                  `sell_cheaper`, `double_fee`, `stay_profitable`, `take_profit`, `stop_loss`, `trading_number`, 
                  `auto_off`, `trading_from`, `trading_to`, `candle_interval`) 
                  values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s )""",
                  (user_id, bot_name, bot_type, 'Indicator RSI Bot', exchange1, base_currency, selected_coin,
                   trading_volume, rsi_period, rsi_top, rsi_bottom, buy_higher, sell_cheaper, double_fee,
                   stay_profitable, take_profit, stop_loss, trading_number, auto_off, trading_from, trading_to, candle_interval))
        context = {}

        conn.close
        return HttpResponseRedirect(reverse('trading'))
        #return JsonResponse(context)
        #return HttpResponse(template.render(context, request))
    #return HttpResponse()
@csrf_protect
@require_POST
@never_cache
def macd_bot_save(request):
    template = loader.get_template('pages/user/html/trading.html')
    conn = mysql.connector.Connect(host='localhost', user='cso', password='', database='trading_bot')
    c = conn.cursor(buffered=True)
    user_id = str(request.session['user_id'])
    if request.method == "POST":
        bot_name = request.POST['macd_bot_name']
        #bot_type = request.POST['bot_type']
        exchange1 = request.POST['macd_exchange']
        base_currency = request.POST['macd_base_currency']
        selected_coin = request.POST['macd_selected_coin']
        candle_interval = request.POST['macd_candle_interval']
        trading_volume = request.POST['macd_trading_volume']
        macd_long = request.POST['macd_long']
        macd_short = request.POST['macd_short']
        macd_signal = request.POST['macd_signal']
        #buy_higher = request.POST['buy_higher']
        #double_fee = request.POST['double_fee']
        #sell_cheaper = request.POST['sell_cheaper']
        #stay_profitable = request.POST['stay_profitable']
        take_profit = request.POST['macd_take_profit']
        stop_loss = request.POST['macd_stop_loss']
        trading_number = request.POST['macd_trading_number']
        #auto_off = request.POST['auto_off']
        trading_from = request.POST['macd_trading_from']
        trading_to = request.POST['macd_trading_to']
        param_list = request.POST
        # if param_list.has_key("bot_type"):
        if "macd_bot_type" in param_list:
            bot_type = "Live"
        else:
            bot_type = "Demo"
        if "macd_buy_higher" in param_list:
            buy_higher = "On"
        else:
            buy_higher = "Off"
        if "macd_sell_cheaper" in param_list:
            sell_cheaper = "On"
        else:
            sell_cheaper = "Off"
        if "macd_double_fee" in param_list:
            double_fee = "On"
        else:
            double_fee = "Off"
        if "macd_stay_profitable" in param_list:
            stay_profitable = "On"
        else:
            stay_profitable = "Off"
        if "macd_auto_off" in param_list:
            auto_off = "On"
        else:
            auto_off = "Off"
        c.execute("""insert into `bot` (`user_id`,`bot_name`,`bot_type`, `bot_kind`, `exchange1`,`base_currency`,`selected_coin`, 
                    `trading_volume`, `macd_long`, `macd_short`, `macd_signal`, `buy_higher`, `sell_cheaper`, 
                    `double_fee`, `stay_profitable`, `take_profit`, `stop_loss`, `trading_number`, `auto_off`, 
                    `trading_from`, `trading_to`, `candle_interval`) 
                    values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s )""",
                  (user_id, bot_name, bot_type, 'Indicator MACD Bot', exchange1, base_currency, selected_coin,
                   trading_volume, macd_long, macd_short, macd_signal, buy_higher, sell_cheaper, double_fee,
                   stay_profitable, take_profit, stop_loss, trading_number, auto_off, trading_from, trading_to,
                   candle_interval))
        conn.commit()
    c.execute("select * from bot where user_id=%s order by bot_kind, bot_type, bot_status", (user_id,))
    bot_list = c.fetchall()
    context = {'bot_list': bot_list}
    conn.close()
    #return JsonResponse(context)
    return HttpResponseRedirect(reverse('trading'))
    #return HttpResponse(template.render(context, request))
def bb_bot_save(request):
    conn = mysql.connector.Connect(host='localhost', user='cso', password='', database='trading_bot')
    c = conn.cursor(buffered=True)
    user_id = str(request.session['user_id'])
    print("here")
    if request.method == "POST":
        bot_name = request.POST['bb_bot_name']
        # bot_type = request.POST['bot_type']
        exchange1 = request.POST['bb_exchange']
        base_currency = request.POST['bb_base_currency']
        selected_coin = request.POST['bb_selected_coin']
        candle_interval = request.POST['bb_candle_interval']
        trading_volume = request.POST['bb_trading_volume']
        bb_period = request.POST['bb_period']
        bb_upper = request.POST['bb_upper']
        bb_lower = request.POST['bb_lower']
        # buy_higher = request.POST['buy_higher']
        # double_fee = request.POST['double_fee']
        # sell_cheaper = request.POST['sell_cheaper']
        # stay_profitable = request.POST['stay_profitable']
        take_profit = request.POST['bb_take_profit']
        stop_loss = request.POST['bb_stop_loss']
        trading_number = request.POST['bb_trading_number']
        # auto_off = request.POST['auto_off']
        trading_from = request.POST['bb_trading_from']
        trading_to = request.POST['bb_trading_to']
        param_list = request.POST
        # if param_list.has_key("bot_type"):
        if "bb_bot_type" in param_list:
            bot_type = "Live"
        else:
            bot_type = "Demo"
        if "bb_buy_higher" in param_list:
            buy_higher = "On"
        else:
            buy_higher = "Off"
        if "bb_sell_cheaper" in param_list:
            sell_cheaper = "On"
        else:
            sell_cheaper = "Off"
        if "bb_double_fee" in param_list:
            double_fee = "On"
        else:
            double_fee = "Off"
        if "bb_stay_profitable" in param_list:
            stay_profitable = "On"
        else:
            stay_profitable = "Off"
        if "bb_auto_off" in param_list:
            auto_off = "On"
        else:
            auto_off = "Off"
        c.execute("""insert into `bot` (`user_id`,`bot_name`,`bot_type`, `bot_kind`, `exchange1`,`base_currency`,`selected_coin`, 
                        `trading_volume`, `bb_period`, `bb_upper`, `bb_lower`, `buy_higher`, `sell_cheaper`, 
                        `double_fee`, `stay_profitable`, `take_profit`, `stop_loss`, `trading_number`, `auto_off`, 
                        `trading_from`, `trading_to`, `candle_interval`) 
                        values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s )""",
                  (user_id, bot_name, bot_type, 'Indicator BB Bot', exchange1, base_currency, selected_coin,
                   trading_volume, bb_period, bb_upper, bb_lower, buy_higher, sell_cheaper, double_fee,
                   stay_profitable, take_profit, stop_loss, trading_number, auto_off, trading_from, trading_to, candle_interval))
        conn.commit()
    c.execute("select * from bot where user_id=%s order by bot_kind, bot_type, bot_status", (user_id,))
    bot_list = c.fetchall()
    context = {'bot_list': bot_list}
    conn.close()
    # return JsonResponse(context)
    return HttpResponseRedirect(reverse('trading'))
def arbitrage_bot_save(request):
    template = loader.get_template('pages/user/html/trading.html')
    conn = mysql.connector.Connect(host='localhost', user='cso', password='', database='trading_bot')
    c = conn.cursor(buffered=True)
    if request.method == "POST":
        username = request.session['username']
        email = request.session['email']
        user_id = str(request.session['user_id'])
        bot_name = request.POST['arbitrage_bot_name']
        #bot_type = request.POST['bot_type']
        exchange1 = request.POST['arbitrage_exchange1']
        exchange2 = request.POST['arbitrage_exchange2']
        #base_currency = request.POST['arbitrage_base_currency']
        selected_coin = request.POST['arbitrage_selected_coin']
        candle_interval = request.POST['arbitrage_candle_interval']
        trading_volume = request.POST['arbitrage_trading_volume']
        price_difference = request.POST['arbitrage_difference']
        #rsi_period = request.POST['rsi_period']
        #rsi_top = request.POST['rsi_top']
        #rsi_bottom = request.POST['rsi_bottom']
        #buy_higher = request.POST['buy_higher']
        #double_fee = request.POST['double_fee']
        #sell_cheaper = request.POST['sell_cheaper']
        #stay_profitable = request.POST['stay_profitable']
        take_profit = request.POST['arbitrage_take_profit']
        stop_loss = request.POST['arbitrage_stop_loss']
        trading_number = request.POST['arbitrage_trading_number']
        #auto_off = request.POST['auto_off']
        trading_from = request.POST['arbitrage_trading_from']
        trading_to = request.POST['arbitrage_trading_to']

        param_list = request.POST
        # if param_list.has_key("bot_type"):
        if "arbitrage_bot_type" in param_list:
            bot_type = "On"
        else:
            bot_type = "Off"
        if "arbitrage_buy_higher" in param_list:
            buy_higher = "On"
        else:
            buy_higher = "Off"
        if "arbitrage_sell_cheaper" in param_list:
            sell_cheaper = "On"
        else:
            sell_cheaper = "Off"
        if "arbitrage_double_fee" in param_list:
            double_fee = "On"
        else:
            double_fee = "Off"
        if "arbitrage_stay_profitable" in param_list:
            stay_profitable = "On"
        else:
            stay_profitable = "Off"
        if "arbitrage_auto_off" in param_list:
            auto_off = "On"
        else:
            auto_off = "Off"
        c.execute("""insert into `bot` (`user_id`,`bot_name`,`bot_type`, `bot_kind`, `exchange1`,`exchange2`,`selected_coin`, `trading_volume`, `price_difference`, `buy_higher`, `sell_cheaper`, `double_fee`, `stay_profitable`, `take_profit`, `stop_loss`, `trading_number`, `auto_off`, `trading_from`, `trading_to`, `candle_interval`) 
                  values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, )""",
                  (user_id, bot_name, bot_type, 'Arbitrage Bot', exchange1, exchange2, selected_coin, trading_volume, price_difference, buy_higher, sell_cheaper, double_fee, stay_profitable, take_profit, stop_loss, trading_number, auto_off, trading_from, trading_to, candle_interval))
        conn.close
        context = {}
        return HttpResponse(template.render(context, request))
    #return HttpResponse()
def market_bot_save(request):
    template = loader.get_template('pages/user/html/trading.html')
    conn = mysql.connector.Connect(host='localhost', user='cso', password='', database='trading_bot')
    c = conn.cursor(buffered=True)
    if request.method == "POST":
        username = request.session['username']
        email = request.session['email']
        user_id = str(request.session['user_id'])
        bot_name = request.POST['bot_name']
        #bot_type = request.POST['bot_type']
        exchange1 = request.POST['exchange']
        base_currency = request.POST['base_currency']
        selected_coin = request.POST['selected_coin']
        candle_interval = request.POST['candle_interval']
        trading_volume = request.POST['trading_volume']
        rsi_period = request.POST['rsi_period']
        rsi_top = request.POST['rsi_top']
        rsi_bottom = request.POST['rsi_bottom']
        #buy_higher = request.POST['buy_higher']
        #double_fee = request.POST['double_fee']
        #sell_cheaper = request.POST['sell_cheaper']
        #stay_profitable = request.POST['stay_profitable']
        take_profit = request.POST['take_profit']
        stop_loss = request.POST['stop_loss']
        trading_number = request.POST['trading_number']
        #auto_off = request.POST['auto_off']
        trading_from = request.POST['trading_from']
        trading_to = request.POST['trading_to']

        param_list = request.POST
        # if param_list.has_key("bot_type"):
        if "bot_type" in param_list:
            bot_type = "On"
        else:
            bot_type = "Off"
        if "buy_higher" in param_list:
            buy_higher = "On"
        else:
            buy_higher = "Off"
        if "sell_cheaper" in param_list:
            sell_cheaper = "On"
        else:
            sell_cheaper = "Off"
        if "double_fee" in param_list:
            double_fee = "On"
        else:
            double_fee = "Off"
        if "stay_profitable" in param_list:
            stay_profitable = "On"
        else:
            stay_profitable = "Off"
        if "auto_off" in param_list:
            auto_off = "On"
        else:
            auto_off = "Off"
        c.execute("""insert into `bot` (`user_id`,`bot_name`,`bot_type`, `bot_kind`, `exchange1`,`base_currency`,`selected_coin`, `trading_volume`, `rsi_period`, `rsi_top`, `rsi_bottom`, `buy_higher`, `sell_cheaper`, `double_fee`, `stay_profitable`, `take_profit`, `stop_loss`, `trading_number`, `auto_off`, `trading_from`, `trading_to`, `candle_interval`) 
                  values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s )""",
                  (user_id, bot_name, bot_type, 'RSI Bot', exchange1, base_currency, selected_coin, trading_volume, rsi_period, rsi_top, rsi_bottom, buy_higher, sell_cheaper, double_fee, stay_profitable, take_profit, stop_loss, trading_number, auto_off, trading_from, trading_to, candle_interval))
        conn.close
        context = {}
        return HttpResponse(template.render(context, request))
    #return HttpResponse()
def ml_bot_save(request):
    template = loader.get_template('pages/user/html/trading.html')
    conn = mysql.connector.Connect(host='localhost', user='cso', password='', database='trading_bot')
    c = conn.cursor(buffered=True)
    if request.method == "POST":
        username = request.session['username']
        email = request.session['email']
        user_id = str(request.session['user_id'])
        bot_name = request.POST['bot_name']
        #bot_type = request.POST['bot_type']
        exchange1 = request.POST['exchange']
        base_currency = request.POST['base_currency']
        selected_coin = request.POST['selected_coin']
        candle_interval = request.POST['candle_interval']
        trading_volume = request.POST['trading_volume']
        rsi_period = request.POST['rsi_period']
        rsi_top = request.POST['rsi_top']
        rsi_bottom = request.POST['rsi_bottom']
        #buy_higher = request.POST['buy_higher']
        #double_fee = request.POST['double_fee']
        #sell_cheaper = request.POST['sell_cheaper']
        #stay_profitable = request.POST['stay_profitable']
        take_profit = request.POST['take_profit']
        stop_loss = request.POST['stop_loss']
        trading_number = request.POST['trading_number']
        #auto_off = request.POST['auto_off']
        trading_from = request.POST['trading_from']
        trading_to = request.POST['trading_to']

        param_list = request.POST
        # if param_list.has_key("bot_type"):
        if "bot_type" in param_list:
            bot_type = "On"
        else:
            bot_type = "Off"
        if "buy_higher" in param_list:
            buy_higher = "On"
        else:
            buy_higher = "Off"
        if "sell_cheaper" in param_list:
            sell_cheaper = "On"
        else:
            sell_cheaper = "Off"
        if "double_fee" in param_list:
            double_fee = "On"
        else:
            double_fee = "Off"
        if "stay_profitable" in param_list:
            stay_profitable = "On"
        else:
            stay_profitable = "Off"
        if "auto_off" in param_list:
            auto_off = "On"
        else:
            auto_off = "Off"
        c.execute("""insert into `bot` (`user_id`,`bot_name`,`bot_type`, `bot_kind`, `exchange1`,`base_currency`,`selected_coin`, `trading_volume`, `rsi_period`, `rsi_top`, `rsi_bottom`, `buy_higher`, `sell_cheaper`, `double_fee`, `stay_profitable`, `take_profit`, `stop_loss`, `trading_number`, `auto_off`, `trading_from`, `trading_to`, `candle_interval`) 
                  values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s )""",
                  (user_id, bot_name, bot_type, 'RSI Bot', exchange1, base_currency, selected_coin, trading_volume, rsi_period, rsi_top, rsi_bottom, buy_higher, sell_cheaper, double_fee, stay_profitable, take_profit, stop_loss, trading_number, auto_off, trading_from, trading_to, candle_interval))
        conn.close
        context = {}
        return HttpResponse(template.render(context, request))
    #return HttpResponse()
def update_bot_status(request):
    template = loader.get_template('pages/user/html/trading.html')
    conn = mysql.connector.Connect(host='localhost', user='cso', password='', database='trading_bot')
    c = conn.cursor(buffered=True)
    bot_id = request.POST['bot_id']
    c.execute("select bot.bot_name, bot.bot_type, bot.bot_kind, bot.bot_status, user.permission, bot.run_time from bot inner join user on user.absID=bot.user_id where bot.absID=%s", (bot_id,))
    list1 = c.fetchall()
    bot_status = list1[0][3]
    user_permission = list1[0][4]
    run_time = list1[0][5]
    table_name = ""
    conn.commit()
    if user_permission == "2":
        table_name = "run_enthusiast_bot"
    if user_permission == "3":
        table_name = "run_adopter_bot"
    if user_permission == "4":
        table_name = "run_newbie_bot"
    if bot_status == "On":
        c.execute("select bot_id from "+table_name+" where run_time=%s", (run_time,))
        list2 = c.fetchall()
        conn.commit()
        bot_id_list = str(list2[0][0])
        print(bot_id_list)
        str1 = "," + bot_id + ","
        print(str1)
        bot_id_list = bot_id_list.replace(str1, ",")
        print(bot_id_list)
        c.execute("update "+table_name+" set bot_id=%s where run_time=%s", (bot_id_list, run_time))
        c.execute("update bot set bot_status='Off' where absID=%s", (bot_id,))
        conn.commit()
        bot_new_status = "Off"

    elif bot_status == "Off":
        c.execute(
            "select "+table_name+".bot_id, bot_run_time.run_time from bot_run_time inner join "+table_name+" on bot_run_time.run_time="+table_name+".run_time where bot_run_time.user_permission=%s",
            (user_permission,))
        b1 = c.fetchall()
        print("off")
        print(b1)
        bot_id_list = b1[0][0]
        run_time = b1[0][1]
        conn.commit()
        if user_permission == "2":
            new_run_time = divmod(int(run_time)+5, 150)
            new_run_time = new_run_time[1]
        if user_permission == "3":
            new_run_time = divmod(int(run_time)+5, 300)
            new_run_time = new_run_time[1]
        if user_permission == "4":
            new_run_time = divmod(int(run_time)+5, 450)
            print(new_run_time)
            new_run_time = new_run_time[1]
            print(new_run_time)
        if bot_id_list == "":
            new_bot_id_list = "," + bot_id + ","
        else:
            new_bot_id_list = bot_id_list + bot_id + ","
        c.execute("update bot_run_time set run_time=%s where user_permission=%s", (new_run_time, user_permission))
        c.execute("update "+table_name+" set bot_id=%s where run_time=%s", (new_bot_id_list, run_time))
        c.execute("update bot set bot_status='On', run_time=%s where absID=%s", (run_time, bot_id))
        conn.commit()
        bot_new_status = "On"


    context = {
        'bot_status': bot_status,
        'bot_new_status': bot_new_status,
        'bot_name': list1[0][0],
        'bot_type': list1[0][1],
        'bot_kind': list1[0][2]
    }
    conn.close()
    return JsonResponse(context)
    #return HttpResponse(json.dumps(context), content_type='application/json')
def rsi_backtest(user_id, bot_id, trend, coin_price, last_buy_price, last_sell_price, buy_higher, sell_cheaper,
                  trading_volume, stay_profitable, double_fee, exchange_fee, time):
    conn = mysql.connector.Connect(host='localhost', user='cso', password='', database='trading_bot')
    c = conn.cursor(buffered=True)
    order_time = datetime.datetime.fromtimestamp(time)
    #print(user_id)
    result_str = ""
    if trend == "bottom":
        print("comt to here")
        c.execute("select * from backtest where user_id=%s and position ='long' and order_type='buy' and order_status='create'", (user_id,))
        result = c.fetchall()
        conn.commit()
        if len(result) <= 0:
            # print("open long")
            # print(coin_price)
            if buy_higher == "On" and coin_price > last_sell_price:
                return ""
            c.execute(
                """insert into `backtest` (`user_id`, `bot_id`, `position`, `order_type`, `order_status`, `buy_time`, `buy_price`) values (%s, %s, %s, %s, %s, %s, %s)""",
                (user_id, bot_id, 'long', 'buy', 'create', order_time, coin_price,))
            conn.commit()
            result_str = "open long"

        return result_str
    if trend == "top":
        #print("go to there")
        c.execute(
            """select buy_price from backtest where user_id=%s and position='long' and order_type='buy' and order_status='create'""",
            (user_id,))
        result1 = c.fetchall()
        # print(result1)
        conn.commit()
        if len(result1) > 0:
            buy_price = float(result1[0][0])
            if sell_cheaper == "On" and coin_price < last_buy_price:
                return ""
            if double_fee == "On" and float(trading_volume) * (float(coin_price) - float(buy_price)) < 2 * exchange_fee:
                return ""
            if stay_profitable == "On" and coin_price < buy_price:
                return ""
            c.execute(
                "update backtest set order_status='complete', order_type='sell', sell_price=%s, sell_time=%s where user_id=%s and position='long' and order_type='buy' and order_status='create'",
                (coin_price, order_time, user_id))
            conn.commit()
            result_str = "close long"
        # conn.close()
        return result_str
def macd_backtest(user_id, bot_id, trend, coin_price, last_buy_price, last_sell_price, buy_higher, sell_cheaper,
                  trading_volume, stay_profitable, double_fee, exchange_fee, time):
    conn = mysql.connector.Connect(host='localhost', user='cso', password='', database='trading_bot')
    c = conn.cursor(buffered=True)
    order_time = datetime.datetime.fromtimestamp(time)
    print(user_id)
    result_str = ""
    if trend == "up_trend":
        c.execute("""select * from backtest where user_id=%s and position ='long' and order_type='buy' and order_status='create'""", (user_id,))
        result = c.fetchall()
        conn.commit()
        if len(result) <= 0:
            print("open long")
            print(coin_price)
            if buy_higher == "On" and coin_price > last_sell_price:
                return ""
            c.execute(
                """insert into `backtest` (`user_id`, `bot_id`, `position`, `order_type`, `order_status`, `buy_time`, `buy_price`) values (%s, %s, %s, %s, %s, %s, %s)""",
                (user_id, bot_id, 'long', 'buy', 'create', order_time, coin_price,))
            conn.commit()
            result_str = "open long"

        return result_str
    if trend == "down_trend":
        c.execute(
            """select buy_price from backtest where user_id=%s and position='long' and order_type='buy' and order_status='create'""", (user_id,))
        result1 = c.fetchall()
        print(result1)
        conn.commit()
        if len(result1) > 0:
            buy_price = float(result1[0][0])
            if sell_cheaper == "On" and coin_price < last_buy_price:
                return ""
            if double_fee == "On" and float(trading_volume)*(float(coin_price) - float(buy_price)) < 2 * exchange_fee:
                return ""
            if stay_profitable == "On" and coin_price < buy_price:
                return ""
            c.execute("update backtest set order_status='complete', order_type='sell', sell_price=%s, sell_time=%s where user_id=%s and position='long' and order_type='buy' and order_status='create'", (coin_price, order_time, user_id))
            conn.commit()
            result_str += "close long"
        #conn.close()
        return result_str
def bb_backtest(user_id, bot_id, trend, coin_price, last_buy_price, last_sell_price, buy_higher, sell_cheaper,
                  trading_volume, stay_profitable, double_fee, exchange_fee, time):
    conn = mysql.connector.Connect(host='localhost', user='cso', password='', database='trading_bot')
    c = conn.cursor(buffered=True)
    order_time = datetime.datetime.fromtimestamp(time)
    #print(user_id)
    result_str = ""
    if trend == "lower":
        c.execute("""select * from backtest where bot_id=%s and order_status='create'""", (bot_id,))
        result = c.fetchall()
        conn.commit()
        if len(result) <= 0:
            #print("open long")
            #print(coin_price)
            if buy_higher == "On" and coin_price > last_sell_price:
                return ""
            c.execute(
                """insert into `backtest` (`user_id`, `bot_id`, `position`, `order_type`, `order_status`, `buy_time`, `buy_price`) values (%s, %s, %s, %s, %s, %s, %s)""",
                (user_id, bot_id, 'long', 'buy', 'create', order_time, coin_price,))
            conn.commit()
            result_str = "open long"

        return result_str
    if trend == "upper":
        c.execute(
            """select buy_price from backtest where user_id=%s and position='long' and order_type='buy' and order_status='create'""", (user_id,))
        result1 = c.fetchall()
        #print(result1)
        conn.commit()
        if len(result1) > 0:
            buy_price = float(result1[0][0])
            if sell_cheaper == "On" and coin_price < last_buy_price:
                return ""
            if double_fee == "On" and float(trading_volume)*(float(coin_price) - float(buy_price)) < 2 * exchange_fee:
                return ""
            if stay_profitable == "On" and coin_price < buy_price:
                return ""
            c.execute("update backtest set order_status='complete', order_type='sell', sell_price=%s, sell_time=%s where user_id=%s and position='long' and order_type='buy' and order_status='create'", (coin_price, order_time, user_id))
            conn.commit()
            result_str += "close long"
        #conn.close()
        return result_str
def change_exchange(request):

    if request.method == "POST":
        exchange = request.POST['exchange']
        base_currency = str(request.POST['base_currency'])
        base_currency = base_currency.lower()
        #file_path = "/media/vilayhong/WORK/Andy_Task/cexminer.nz/templates/coin/" + exchange + "/" + base_currency + ".txt"
        #print(BASE_DIR)
        #print(os.path.join(BASE_DIR, 'templates/coin',))
        file_path = os.path.join(BASE_DIR, 'templates/coin/',)+exchange + "/" + base_currency + ".txt"
        #file_path = "/var/www/cexminer.nz/templates/coin/" + exchange + "/" + base_currency + ".txt"
        coin_list = []
        with open(file_path) as lines:
            coin_list = lines.read().splitlines()
        context = {
            'selected_coin': coin_list
        }
        return JsonResponse(context)

def save_exchange_info(request):
    template = loader.get_template('pages/user/html/trading.html')
    conn = mysql.connector.Connect(host='localhost', user='cso', password='', database='trading_bot')
    c = conn.cursor(buffered=True)
    if request.method == "POST":
        user_id = request.session['user_id']
        binance_api = request.POST['binance_api']
        binance_secret = request.POST['binance_secret']
        cryptopia_api = request.POST['cryptopia_api']
        cryptopia_secret = request.POST['cryptopia_secret']
        cex_api = request.POST['cex_api']
        cex_secret = request.POST['cex_secret']
        bittrex_api = request.POST['bittrex_api']
        bittrex_secret = request.POST['bittrex_secret']
        hitbtc_api = request.POST['hitbtc_api']
        hitbtc_secret = request.POST['hitbtc_secret']
        okex_api = request.POST['okex_api']
        okex_secret = request.POST['okex_secret']







