import os
import uuid

import config
from flask import (
    render_template,
    request,
    redirect,
    session,
    url_for,
    Blueprint,
    abort,
    send_from_directory,
    current_app)
from werkzeug.datastructures import FileStorage

from models.message import send_mail
from models.reply import Reply
from models.topic import Topic
from models.user import User
# from routes import current_user, cache
from routes import current_user

import json

from utils import log

main = Blueprint('index', __name__)

"""
用户在这里可以
    访问首页
    注册
    登录

用户登录后, 会写入 session, 并且定向到 /profile
"""

import gevent
import time

ut = {}


@main.route("/")
def index():
    # t = threading.Thread()
    # t.start()
    gevent.spawn()
    time.sleep(0.5)
    print('time type', time.sleep, gevent.sleep)
    u = current_user()
    return render_template("login-page.html", user=u)


@main.route('/setting')
def setting():
    # form = request.form.to_dict()
    u = current_user()
    return render_template("setting.html", user=u)


@main.route('/setting_password', methods=['POST'])
def setting_password():
    form = request.form.to_dict()
    log('formmmm', form)
    # 用类函数来判断
    u = current_user()
    form['password'] = User.salted_password(form['newpassword'])
    u.update(u.id, password=form['password'])
    log('passzzz', u.password)
    return redirect(url_for('.index'))


@main.route('/setting_sgin', methods=['POST'])
def setting_sgin():
    form = request.form.to_dict()
    # 用类函数来判断
    u = current_user()
    log('username', u.username, u.sign)
    u.update(u.id, username=form['username'], sign=form['sign'])
    return redirect(url_for('.setting'))


@main.route("/register", methods=['POST'])
def register():
    form = request.form.to_dict()
    # 用类函数来判断
    u = User.register(form)
    return redirect(url_for('.index'))


@main.route("/register_view")
def register_view():
    return render_template("register_view.html")


@main.route("/reset/send", methods=['POST'])
def reset_send():
    form = request.form.to_dict()
    username = form['username']
    u = User.one(username=username)
    token = str(uuid.uuid4())
    ut[u.id] = token
    subject = '点击链接'
    author = config.admin_mail
    to = u.email
    content = 'http://localhost:3000/reset/view?token={}'.format(token)
    send_mail(subject, author, to, content)
    return render_template('index.html')


@main.route("/reset/view", methods=["GET", "POST"])
def reset_view():
    if 'token' not in request.args:
        return redirect(url_for('.index'))
    else:
        return render_template('reset_view.html', token=request.args['token'])


@main.route('/reset/update', methods=["POST"])
def reset_update():
    form = request.form.to_dict()
    log('ffff', form)
    for key in ut:
        if ut[key] == form['token']:
            u = User.one(id=int(key))
            form['password'] = u.salted_password(form['newpassword'])
            log('ppppp', form['password'], form['newpassword'])
            u.update(u.id, password=form['password'])
    return redirect(url_for('.index'))


@main.route("/login", methods=['POST'])
def login():
    form = request.form
    u = User.validate_login(form)
    log('passaaaaa', form, u)
    if u is None:
        return redirect(url_for('.index'))
    else:
        # session 中写入 user_id
        # session_id = str(uuid.uuid4())
        # key = 'session_id_{}'.format(session_id)
        # log('index login key <{}> user_id <{}>'.format(key, u.id))
        # cache.set(key, u.id)

        # redirect_to_index = redirect(url_for('topic.index'))
        # response = current_app.make_response(redirect_to_index)
        # response.set_cookie('session_id', value=session_id)
        # 转到 topic.index 页面
        # return response
        session['user_id'] = u.id
        return redirect(url_for('topic.index'))


def created_topic(user_id):
    # O(n)
    ts = Topic.all(user_id=user_id)
    return ts
    #
    # k = 'created_topic_{}'.format(user_id)
    # if cache.exists(k):
    #     v = cache.get(k)
    #     ts = json.loads(v)
    #     return ts
    # else:
    #     ts = Topic.all(user_id=user_id)
    #     v = json.dumps([t.json() for t in ts])
    #     cache.set(k, v)
    #     return ts


def replied_topic(user_id):
    # O(k)+O(m*n)
    rs = Reply.all(user_id=user_id)
    ts = []
    for r in rs:
        t = Topic.one(id=r.topic_id)
        ts.append(t)
    return ts
    #
    #     sql = """
    # select * from topic
    # join reply on reply.topic_id=topic.id
    # where reply.user_id=1
    # """
    # k = 'replied_topic_{}'.format(user_id)
    # if cache.exists(k):
    #     v = cache.get(k)
    #     ts = json.loads(v)
    #     return ts
    # else:
    #     # ts = Topic.select()
    #     #   .join(Reply, 'id', 'topic_id')
    #     #   .where(user_id=user_id)
    #     #   .all()
    #     rs = Reply.all(user_id=user_id)
    #     ts = []
    #     for r in rs:
    #         t = Topic.one(id=r.topic_id)
    #         ts.append(t)
    #
    #     v = json.dumps([t.json() for t in ts])
    #     cache.set(k, v)
    #
    #     return ts


@main.route('/profile')
def profile():
    print('running profile route')
    u = current_user()
    if u is None:
        return redirect(url_for('.index'))
    else:
        created = created_topic(u.id)
        replied = replied_topic(u.id)
        return render_template(
            'profile.html',
            user=u,
            created=created,
            replied=replied
        )


@main.route('/user/<int:id>')
def user_detail(id):
    u = User.one(id=id)
    if u is None:
        abort(404)
    else:
        return render_template('profile.html', user=u)


@main.route('/image/add', methods=['POST'])
def avatar_add():
    file: FileStorage = request.files['avatar']
    # file = request.files['avatar']
    # filename = file.filename
    # ../../root/.ssh/authorized_keys
    # images/../../root/.ssh/authorized_keys
    # filename = secure_filename(file.filename)
    suffix = file.filename.split('.')[-1]
    if suffix not in ['gif', 'jpg', 'jpeg']:
        abort(400)
        log('不接受的后缀, {}'.format(suffix))
    else:
        filename = '{}.{}'.format(str(uuid.uuid4()), suffix)
        path = os.path.join('images', filename)
        file.save(path)

        u = current_user()
        User.update(u.id, image='/images/{}'.format(filename))

        return redirect(url_for('.setting'))


@main.route('/images/<filename>')
def image(filename):
    # 不要直接拼接路由，不安全，比如
    # http://localhost:3000/images/..%5Capp.py
    # path = os.path.join('images', filename)
    # print('images path', path)
    # return open(path, 'rb').read()
    # if filename in os.listdir('images'):
    #     return
    return send_from_directory('images', filename)
