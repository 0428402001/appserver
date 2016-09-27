import tornado.httpclient
import tornado.web
import tornado.gen
import tornado.httpserver
import tornado.ioloop
import os
import sys

from ting import TestHandler, StartupImage, Config, Activity, Category, CategoryHot, CategorySubscription,CategorySubscriptionstate,UserProfile,UserClassify, MenuInfo,QueryHot, BlogHot, BlogIndex, Blog, BlogCategory, BlogFavorate, BlogPraise,BlogFavorateUID, BlogQuery, BlogTag, TagBlog, BlogID, CommentHot, Comment, CommentBlog,CommentPraise, CommentPraiseCommentID,CommentReply, CommentReplyComment_id, Message , MessageAllreadyRead,Setting ,  Blogview, AD, FlushAllCache, FlushSingleBlogContent, FlushHomePageBlog, FlushHomePageBlogIndex, UpdateToken,  PushBlogToAllUsers ,Test2,  Test1, PushBlogToAPPID, Rss, AdsTa,UserLogin,UserRegister,UpdateImage



application = tornado.web.Application(
    handlers=[
        (TestHandler.url_pattern(), TestHandler),
        (StartupImage.url_pattern(), StartupImage),
        (Config.url_pattern(), Config),
        (Activity.url_pattern(), Activity),
        (Category.url_pattern(), Category),
        (CategoryHot.url_pattern(), CategoryHot),
        (CategorySubscription.url_pattern(), CategorySubscription),
        (CategorySubscriptionstate.url_pattern(), CategorySubscriptionstate),
        (UserLogin.url_pattern(), UserLogin),
        (UpdateImage.url_pattern(), UpdateImage),
        (UserRegister.url_pattern(), UserRegister),
        (UserProfile.url_pattern(), UserProfile),
        (UserClassify.url_pattern(), UserClassify),
        (MenuInfo.url_pattern(), MenuInfo),
        (QueryHot.url_pattern(), QueryHot),
        (BlogHot.url_pattern(), BlogHot),
        (BlogIndex.url_pattern(), BlogIndex),
        (Blog.url_pattern(), Blog),
        (BlogCategory.url_pattern(), BlogCategory),
        (BlogFavorate.url_pattern(), BlogFavorate),
        (BlogPraise.url_pattern(), BlogPraise),
        (BlogFavorateUID.url_pattern(), BlogFavorateUID),
        (BlogQuery.url_pattern(), BlogQuery),
        (BlogTag.url_pattern(), BlogTag),
        (Blogview.url_pattern(), Blogview),
        (TagBlog.url_pattern(), TagBlog),
        (BlogID.url_pattern(), BlogID),
        (CommentHot.url_pattern(), CommentHot),
        (CommentPraise.url_pattern(), CommentPraise),
        (CommentPraiseCommentID.url_pattern(), CommentPraiseCommentID),
        (CommentReply.url_pattern(), CommentReply),
        (CommentReplyComment_id.url_pattern(), CommentReplyComment_id),
        (Comment.url_pattern(), Comment),
        (CommentBlog.url_pattern(), CommentBlog),
        (Message.url_pattern(), Message),
        (MessageAllreadyRead.url_pattern(), MessageAllreadyRead),
        (AD.url_pattern(), AD),
        (FlushAllCache.url_pattern(), FlushAllCache),
        (FlushSingleBlogContent.url_pattern(), FlushSingleBlogContent),
        (FlushHomePageBlog.url_pattern(), FlushHomePageBlog),
        (FlushHomePageBlogIndex.url_pattern(), FlushHomePageBlogIndex),
        (UpdateToken.url_pattern(), UpdateToken),
        (PushBlogToAllUsers.url_pattern(),PushBlogToAllUsers ),
        (PushBlogToAPPID.url_pattern(), PushBlogToAPPID),
        (AdsTa.url_pattern(), AdsTa),
        (Setting.url_pattern(), Setting),
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
