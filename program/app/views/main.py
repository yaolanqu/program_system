from flask import Blueprint, render_template,flash,redirect,url_for
# from app.forms import PostsForm
from flask_login import current_user
from app.models import Admin
from app.extensions import db
main = Blueprint('main', __name__)

#
# @main.route('/',methods =['POST','GET'])
# def index():
#     form = PostsForm()
#
#     if form.validate_on_submit():
#         if current_user.is_authenticated:
#             #创建post对象，导入表单库
#             u = current_user._get_current_object()
#             p =Posts(content=form.content.data,user =u)
#             db.session.add(p)
#             flash('发表成功')
#             return redirect(url_for('main.index'))
#         else:
#             flash('登录后才能发表')
#             return redirect(url_for('user.login'))
#     return render_template('main/index.html',form = form)
@main.route('/')
def index():
    return render_template('main/index.html')

@main.route('/admin/')
def index_a():

    return render_template('main/index_a.html')

@main.route('/head/')
def index_h():
    return render_template('main/index.html')