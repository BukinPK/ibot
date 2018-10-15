import os
import numpy as np
from random import randrange
from time import sleep
from getpass import getpass
from .InstagramAPI import InstagramAPI

basedir = os.path.abspath(os.path.dirname(__file__))

from .follower import Follower
from .target import Target


__all__ = ['Bot', 'InstagramAPI', 'Follower', 'Target']


class Bot:
 
    my_name = ''
    passwd = ''
    unfollow_wait = 60

    def __init__(self):
        try: os.mkdir(os.path.join(basedir, 'bot_data'))
        except FileExistsError: pass

    def login(self):
        if not self.my_name: self.my_name = input('Enter your login: ')
        if not self.passwd: self.passwd = getpass('Enter your password: ')
        self.api = InstagramAPI(self.my_name, self.passwd)
        if self.api.login() is True:
            self.getUserId = self._getUserId
            self.makeTarget = self._makeTarget
            self.unfollowing = self._unfollowing
            self.makeFollower = self._makeFollower
            return True
        else:
            self.my_name = ''
            self.passwd = ''
            del self.api
            return False

    def _getUserId(self, username):
        if username:
            self.api.searchUsername(username)
            return self.api.LastJson['user']['pk']
        else:
            return None
    
    def _makeTarget(self, target_id=None):
        if not target_id: target_id = self.getUserId(
            input('Enter the name of the target group: '))
        self.target = Target(target_id, self.api)

    def _makeFollower(self, follower_id=None):
        if not follower_id: follower_id = self.getUserIyd(
            input('Enter the name of the user: '))
        self.follower = Follower(follower_id, self.api)
        return self.follower

    def _unfollowing(self):
        self.getData()
        for follower in self.following:
            if follower.unfollow():
                wait = randrange(30, self.unfollow_wait)
                print('wait:', wait)
                sleep(wait)
    
    def getData(self):
        with open(os.path.join(basedir, 'bot_data', 'user_fol'), 'r') as f:
            following = np.array(f.readlines(), dtype='int64')

        ext = []
        for file in ('user_unfol', 'user_unfol_exceptions'):
            if os.path.exists(os.path.join(basedir, 'bot_data', file)):
                with open(os.path.join(basedir, 'bot_data', file), 'r') as f:
                    ext.extend(f.readlines()) 
        if ext:
            ext = np.array(ext, dtype='int64')
            following = np.setdiff1d(following, ext, assume_unique=True)

        self.following = list(map(self.makeFollower,
                                  list(map(int, following))))
