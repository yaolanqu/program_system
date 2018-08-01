from flask import Blueprint, render_template, redirect, url_for, flash, current_app, session, request,make_response
from app.forms import RegisterForm,AddProduct, UploadForm,UpdatePassword,LoginForm_a,UserInformation,AddUserForm

from app.models import User,Admin,Product
from app.extensions import db, photos
from app.mail import send_mail
from flask_login import login_user, logout_user, login_required, current_user
from PIL import Image
import os

admin = Blueprint('admin', __name__)


# 管理员登陆路由
@admin.route('/login_a/', methods=['GET', 'POST'])
def login_a():
    form = LoginForm_a()
    if form.validate_on_submit():
        if not Admin.query.filter(Admin.username == 'admin'):
            flash('用户名错误')
            return render_template('user/login_a.html', form=form)
        elif Admin.query.filter(Admin.password == '123456'):
            flash('登陆成功')
            return render_template('main/index_a.html', form=form)
    return render_template('user/login_a.html',form=form)


# 退出登录
@admin.route('/logout/')
def logout():
    logout_user()
    flash('您已退出登录')
    return redirect(url_for('main.index'))

@admin.route('/comfile_a/')
def comfile_a():
    return render_template('main/comfile_a.html')

#开发部
@admin.route('/project_a/',methods = ['GET','POST'])
def project_a():

    form = AddProduct()
    if form.validate_on_submit():
        p = Product(
            name=form.name.data,
            sections=form.section.data,
            progress=form.progress.data
        )
        db.session.add(p)
        db.session.commit()
    u = User.query.filter(User.section == '开发部').all()
    # pros = Product.query.filter(Product.sections == '开发部')
    pro = Product.query.all()
    return render_template('bumen/project_a.html',u =u,pro = pro,form=form,endpoint='admin.del_product',endpoint1= 'admin.update_progress')
#删除项目
@login_required
@admin.route('/del_product/')
def del_product():
    id = request.args.get('id')
    Product.query.filter(Product.id == id).delete()
    return redirect(url_for('admin.project_a'))

@login_required
@admin.route('/update_progress/')
def update_progress():
    id = request.args.get('id')
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy import create_engine

    ENGINE = create_engine("mysql://root:Root9248*@118.25.43.122:3306/bishe?charset=utf8",
                           convert_unicode=True)
    Session2 = sessionmaker(bind=ENGINE, autocommit=False, autoflush=False)

    session2 = Session2()

    product = session2.query(Product).filter_by(id=id).first()
    if product.progress == '未完成':
        product.progress = "已完成"
        session2.commit()
    else:
        product.progress ='未完成'
        session2.commit()
    return redirect(url_for('admin.project_a'))

@admin.route('/renshibu_a/',methods =['GET','POST'])
def renshi_a():

    form = AddUserForm()
    if form.validate_on_submit():
        # 根据表单数据创建User对象
        u = User( username=form.username.data,
                  password=form.password.data,
                  sex = form.sex.data,
                  age = form.age.data,
                  confirmed = 1,
                  email=form.email.data,
                  idCard=form.idCard.data,
                  phonenumber=form.phonenumber.data,
                  section=form.section.data,
                  part=form.part.data,
                  )
        # 然后保存到数据库中
        db.session.add(u)
        # 此时还没有提交，所以新用户没有id值，需要手动提交
        db.session.commit()



    page = request.args.get('page',1,type=int)
    pagination = User.query.order_by(User.age).paginate(page=page,per_page=3,error_out=False)
    # us = User.query.filter(User.username == '用户测试').first()

    users = pagination.items
    resps =request.cookies.get('name')
    us = User.query.filter(User.username == resps)
    return render_template('bumen/renshi_a.html', us = us,users = users,pagination=pagination,
                           endpoint1 = 'admin.deluser',form =form,endpoint2='admin.select_part',
                           endpoint4='admin.del_absent',
                            endpoint5='admin.add_absent',endpoint6='admin.select_sections')


#删除员工：
@login_required
@admin.route('/deluser/')
def deluser():
    id = request.args.get('id')
    User.query.filter(User.id == id).delete()
    return redirect(url_for('admin.renshi_a'))


@login_required
@admin.route('select_part')
def select_part():
    id= request.args.get('id')
    u = User.query.filter(User.id == id).first()
    if u.part == '员工':
        u.part = '部长'
        db.session.add(u)
        db.session.commit()
    else:
        u.part = '员工'
        db.session.add(u)
        db.session.commit()
    return redirect(url_for('admin.renshi_a'))



@login_required
@admin.route('del_absent')
def del_absent():
    id =request.args.get('id')
    u = User.query.filter(User.id == id).first()
    if u.absent != 0:
        u.absent -= 1
    else:
        u.absent = 0
    db.session.add(u)
    db.session.commit()
    return redirect(url_for('admin.renshi_a'))

@login_required
@admin.route('add_absent')
def add_absent():
    id =request.args.get('id')
    u = User.query.filter(User.id == id).first()
    if u.absent>30:
        u.absent = 0
    else:
        u.absent += 1
    db.session.add(u)
    db.session.commit()
    return redirect(url_for('admin.renshi_a'))

@login_required
@admin.route('add_select_sections')
def select_sections():
    id =request.args.get('id')
    u = User.query.filter(User.id == id).first()
    if u.section==None:
        u.section='开发部'
    elif u.section == '开发部':
        u.section='后勤部'
    elif u.section == '后勤部':
        u.section='开发部'
    db.session.add(u)
    db.session.commit()

    return redirect(url_for('admin.renshi_a'))