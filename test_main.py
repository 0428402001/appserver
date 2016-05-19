import tornado.httpclient
import tornado.web
import tornado.gen
import tornado.httpserver
import tornado.ioloop
import os
from frontend.config import project_static_path, frontend_port
from frontend.index import IndexPage, MainPage
from frontend.login import LoginPage, LogoutPage, RegisterPage
from frontend.upload import UploadPage
from frontend.user_activity_club import ClubCreateActivity, ActivityShow, ClubListActivity, PicCaptcha, VerifySMS, Club
from frontend.wechat import VerifyWechat, LeadToOAuth, OAuthGrantAccess
from wanka.common.handler.ping import PingHandler


application = tornado.web.Application(
    handlers=[
        (PingHandler.url_pattern(), PingHandler),
        (IndexPage.url_pattern(), IndexPage),
        (UploadPage.url_pattern(), UploadPage),
        (LoginPage.url_pattern(), LoginPage),
        (LogoutPage.url_pattern(), LogoutPage),
        (MainPage.url_pattern(), MainPage),
        (ClubCreateActivity.url_pattern(), ClubCreateActivity),
        (ActivityShow.url_pattern(), ActivityShow),
        (ClubListActivity.url_pattern(), ClubListActivity),
        (PicCaptcha.url_pattern(), PicCaptcha),
        (VerifySMS.url_pattern(), VerifySMS),
        (RegisterPage.url_pattern(), RegisterPage),
        (VerifyWechat.url_pattern(), VerifyWechat),
        (LeadToOAuth.url_pattern(), LeadToOAuth),
        (OAuthGrantAccess.url_pattern(), OAuthGrantAccess),
        (Club.url_pattern(), Club),
    ],
    template_path=project_static_path(),
    static_path=project_static_path(),
    cookie_secret="bZJc2sWbQLKos6GkHn/VB9oXwQt8S0R0kRv",
    xsrf_cookies=False,
    login_url='/login',
    debug=False,
)


def main():
    srv = tornado.httpserver.HTTPServer(application, xheaders=True)
    print frontend_port()
    srv.bind(frontend_port())
    srv.start()
    tornado.ioloop.IOLoop.instance().start()
