import tornado.httpclient
import tornado.web
import tornado.gen
import tornado.httpserver
import tornado.ioloop
import os
import sys

from ting import TestHandler, StartupImage, Config, Activity, Category, CategoryHot, CategorySubscription,CategorySubscriptionstate,UserProfile,UserClassify, MenuInfo,QueryHot, BlogHot, BlogIndex, Blog, BlogCategory, BlogFavorate, BlogPraise,BlogFavorateUID, BlogQuery, BlogTag, TagBlog, BlogID, CommentHot, Comment, CommentBlog,CommentPraise, CommentPraiseCommentID,CommentReply, CommentReplyComment_id, Message , MessageAllreadyRead,Setting ,  Blogview, AD, FlushAllCache, FlushSingleBlogContent, FlushHomePageBlog, FlushHomePageBlogIndex, UpdateToken,  PushBlogToAllUsers ,Test2,  Test1, PushBlogToAPPID, Rss



application = tornado.web.Application(
    handlers=[
        (FlushAllCache.url_pattern(), FlushAllCache),
        (FlushSingleBlogContent.url_pattern(), FlushSingleBlogContent),
        (FlushHomePageBlog.url_pattern(), FlushHomePageBlog),
        (FlushHomePageBlogIndex.url_pattern(), FlushHomePageBlogIndex),
        (PushBlogToAllUsers.url_pattern(),PushBlogToAllUsers ),
        (PushBlogToAPPID.url_pattern(), PushBlogToAPPID),
        (Test1.url_pattern(), Test1),
        (Test2.url_pattern(), Test2),
        (Rss.url_pattern(), Rss),
    ],
    template_path=os.path.join(os.path.dirname(__file__), "templates"),
    static_path = os.path.join(os.path.dirname(__file__), "static"),
    xsrf_cookies=False,
    login_url='/login',
    debug = True,
    #debug=False,
)

def main(port):
    srv = tornado.httpserver.HTTPServer(application, xheaders=True)
    srv.bind(port)
    srv.start()
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    port  = sys.argv[1]
    print port, type(port)
    main(port)
