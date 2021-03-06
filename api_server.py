#!/usr/bin/env python
import web
import logging

import api.views.base
import api.views.notifications
import api.views.signup
import api.views.images
import api.views.profile
import api.views.social


class redirect:
    """
        Find and redirect to existed controller with '/' or without it
    """
    def GET(self, path):
        web.seeother('/' + path)

urls = (
    "/(.*)/", 'redirect', # Handle urls with slash and without it
    "/query/notification", api.views.notifications.Notification, # API handler for notifications

    # API to user signup: authenticate user
    "/auth", api.views.signup.Auth,

    # API to user signup: register user
    "/signup/register", api.views.signup.Register,

    # API to user signup: confirmation user email
    "/signup/confirmuser", api.views.signup.Confirmuser,

    # API to upload images
    "/image/upload", api.views.images.ImageUpload,

    # API to user profile: manage user products
    "/profile/mgl", api.views.profile.ManageGetList,
    "/profile/userinfo/update", api.views.profile.UserInfoUpdate,
    "/profile/userinfo/get", api.views.profile.GetProfileInfo,
    "/profile/userinfo/set_privacy", api.views.profile.SetPrivacy,

    # API to user profile: change user password
    "/profile/pwd", api.views.profile.ChangePassword,
    # API for social networks: posting on user page
    "/social/poup", api.views.social.PostingOnUserPage,
    "/social/query/(.*)/(follower|follow)", api.views.social.QueryFollowers
)
web.config.debug = True
api_app = web.application(urls, globals(), autoreload=True)

if __name__ == "__main__":
    api_app.run()
