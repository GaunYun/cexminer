from django.conf.urls import url, include
from . import views
from django.contrib import admin
#from django.contrib.auth import views as auth_views
#from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from TradingBot import settings


urlpatterns = [
# landingpage
    url(r'^$', views.index, name='index'),
    url(r'^login/$', views.login, name='login'),
    url(r'^signup/$', views.signup, name='signup'),
    url(r'^about/$', views.about, name='about'),
    url(r'^services/$', views.services, name='services'),
    url(r'^pricing/$', views.pricing, name='pricing'),
    url(r'^blog/$', views.blog, name='blog'),
    url(r'^article/$', views.article, name='article'),
    url(r'^faq/$', views.faq, name='faq'),
    url(r'^index2/$', views.index2, name='index2'),
    url(r'^index/$', views.index, name='index'),
    url(r'^forgot_password/$', views.forgot_password, name='forgot_password'),
    #url(r'^change_password/$', views.change_password, name='change_password'),
#### login page
    url(r'^login_account/$', views.login_account, name='login_account'),
    url(r'^user_register/$', views.user_register, name='user_register'),
    #url(r'^login_account/$', auth_views.login, name='login_account'),
    url(r'^auth/', include('social_django.urls', namespace='social')),
    url(r'^two_step/$', views.two_step, name='two_step'),
    url(r'^google_login/$', views.google_login, name='google_login'),
    url(r'^email_activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', views.email_activate, name='email_activate'),
    url(r'^forgot_password_activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', views.forgot_password_activate, name='forgot_password_activate'),
###  User Admin page
    url(r'^dashboard/$', views.dashboard, name='dashboard'),
    url(r'^history/$', views.history, name='history'),
    url(r'^trading/$', views.trading, name='trading'),
    url(r'^profit_loss/$', views.profit_loss, name='profit_loss'),
    url(r'^user_setting/$', views.user_setting, name='user_setting'),
    url(r'^exchange_info/$', views.exchange_info, name='exchange_info'),
    url(r'^rsi_bot_save/$', views.rsi_bot_save, name='rsi_bot_save'),
    url(r'^macd_bot_save/$', views.macd_bot_save, name='macd_bot_save'),
    url(r'^bb_bot_save/$', views.bb_bot_save, name='bb_bot_save'),
    url(r'^arbitrage_bot_save/$', views.arbitrage_bot_save, name='arbitrage_bot_save'),
    url(r'^rsi_bot_save/$', views.market_bot_save, name='market_bot_save'),
    url(r'^ml_bot_save/$', views.ml_bot_save, name='ml_bot_save'),
    url(r'^update_bot_status/$', views.update_bot_status, name='update_bot_status'),
    url(r'^change_exchange/$', views.change_exchange, name='change_exchange'),
    url(r'^bot_type_change/$', views.bot_type_change, name='bot_type_change'),
    url(r'^bot_name_change/$', views.bot_name_change, name='bot_name_change'),
    url(r'^view_history_graph/$', views.view_history_graph, name='view_history_graph'),
    #url(r'^/$', views, name=''),
### Admin UI
    url(r'^doc_manage/$', views.doc_manage, name='doc_manage'),
    url(r'^doc_save/$', views.doc_save, name='doc_save'),
]
# serving of uploaded media + static files while debug mode is on
if settings.DEBUG:
    #urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  # uploaded media
    urlpatterns += staticfiles_urlpatterns()
