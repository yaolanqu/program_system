from flask import Blueprint, render_template, redirect, url_for, flash, current_app, session, request,make_response
from app.forms import RegisterForm, LoginForm, UploadForm,UpdatePassword,LoginForm_a,UserInformation

from app.models import User,Admin,Product
from app.extensions import db, photos
from app.mail import send_mail
from flask_login import login_user, logout_user, login_required, current_user
from PIL import Image
import os


user = Blueprint('user', __name__)


@user.route('/test/')
@login_required
def test():
    return 'xxxxx'


# 退出登录
@user.route('/logout/')
def logout():

    logout_user()
    flash('您已退出登录')
    return redirect(url_for('main.index'))

#普通用户登陆路由
@user.route('/login/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        u = User.query.filter(User.username == form.username.data).first()
        if not u:
            flash('无效的用户名')
            # return redirect(url_for("user.login"))
        elif not u.confirmed:
            flash('账户尚未激活，请激活后再登录')
            # return redirect(url_for("user.login"))
        elif u.verify_password(form.password.data):

            # 用户登录，顺便可以完成记住我的功能，还可以指定有效时间
            login_user(u, remember=form.remember.data)
            flash('登录成功')


            return redirect(request.args.get('next') or url_for('main.index'))


        else:
            flash('无效的密码')

    return render_template('user/login.html', form=form)


#普通用户注册路由
@user.route('/register/', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        # 根据表单数据创建User对象
        u = User( username=form.username.data,
                  password=form.password.data,
                  sex = form.sex.data,
                  age = form.age.data,
                  email=form.email.data,
                  idCard=form.idCard.data,
                  phonenumber=form.phonenumber.data,

                  )

        # 然后保存到数据库中
        db.session.add(u)
        # 此时还没有提交，所以新用户没有id值，需要手动提交
        db.session.commit()
        # 准备token
        # 发送激活邮件
        token = u.generate_activate_token()
        url = url_for('user.activate', token=token, _external=True)
        send_mail(form.email.data, '账户激活', 'activate', username=form.username.data, url=url)
        flash('激活邮件已发送至您的邮箱，请点击连接以完成激活')
        return redirect(url_for('main.index'))
    return render_template('user/register.html', form=form)




# @user.route('/login_a/')
# def login_a():
# ##管理员登陆
#             if u.part == 0:
#                 flash('登陆成功')
#                 return render_template('user/login_a.html',form = form)

#激活路由
@user.route('/activate/<token>')
def activate(token):
    if User.check_activate_token(token):
        flash('激活成功，请等待公司对您进行部门分配')
        return redirect(url_for('user.login'))
    else:
        flash('激活失败')
        return redirect(url_for('main.index'))




# 用户详情

@user.route('/profiles/',methods = ['GET','POST'])
@login_required
def profiles():
    form = UserInformation()
    if form.validate_on_submit():
        u = User.query.filter(User.username == form.name.data).first()
        if current_user.username != form.name.data:
            flash('用户名不能修改')
            return redirect(url_for('user.profiles'))
        u.sex = form.sex.data
        u.age = form.age.data
        # try:
        u.idCard= form.idCard.data
        # except:u.idCard.
        u.phonenumber=form.phonenumber.data
        u.section =form.section.data
        db.session.add(u)
        db.session.commit()
        #设置cookie值记录
        resp = redirect(url_for('user.profile'))
        resp.set_cookie('name',u.username)
        return resp
    print("dsadasda")
    return render_template('user/profiles.html',form=form)





@user.route('/profile/')
@login_required
def profile():
    s = current_user.username
    u = User.query.filter(User.username == s).first()
    try:
        idcard = u.idCard
        phonenumber = u.phonenumber
        sex = u.sex
        age = u.age

    except:
        idcard = None
        phonenumber = None
        sex = None
        age = None
    img_url = photos.url(current_user.icon)
    return render_template('user/profile.html', img_url=img_url,name = s,sex = sex,age = age,idcard = idcard,phonenumber = phonenumber)





# 上传头像
@user.route('/change_icon/', methods=['GET','POST'])
def change_icon():
    form = UploadForm()
    if form.validate_on_submit():
        # 获取后缀
        suffix = os.path.splitext(form.icon.data.filename)[1]
        # 随机文件名
        filename = random_string() + suffix
        photos.save(form.icon.data, name=filename)
        # 生成缩略图
        pathname = os.path.join(current_app.config['UPLOADED_PHOTOS_DEST'], filename)
        img = Image.open(pathname)
        img.thumbnail((128, 128))
        img.save(pathname)
        # 删除原来的头像(不是默认头像时才需要删除)
        if current_user.icon != 'default.jpeg':
            os.remove(os.path.join(current_app.config['UPLOADED_PHOTOS_DEST'], current_user.icon))
        # 保存到数据库
        current_user.icon = filename
        db.session.add(current_user)
        return redirect(url_for('user.change_icon'))
    img_url = photos.url(current_user.icon)
    return render_template('user/change_icon.html', form=form, img_url=img_url)






def random_string(length=32):
    import random
    base_str = 'abcdefghijklmnopqrstuvwxyz1234567890'
    return ''.join(random.choice(base_str) for i in range(length))

#公司简介
@user.route('/com_file/')
def com_file():
    return render_template('main/com_file.html')




#开发部
@user.route('/kaifabu/', methods = ['GET','POST'])
def kaifa():
    if current_user.is_authenticated:
        if current_user.section != '开发部':
            flash('您不属于开发部')
            return redirect(url_for('main.index'))
        if current_user.part  == '部长':
            u = User.query.filter(User.section == '开发部')
            #增加新项目
            if request.method == "POST":
                add_b = request.form.get('add')
                add_product = Product(
                    name = add_b,
                    progress='未完成',
                    sections='开发部',
                )
                if Product.query.filter(Product.name==add_b).first():
                    flash('此项目已经存在，请增加新项目')
                    return render_template('bumen/kaifa_b.html')
                db.session.add(add_product)
                db.session.commit()
            p = Product.query.filter(Product.user == None)
            pro = Product.query.all()
            return render_template('bumen/kaifa_b.html',u= u,p_b =pro,p=p)

        #普通员工操作：
        u = User.query.filter(User.username == current_user.username).first()
        # pro_u = u.u_project.all()
        p = u.u_project.all()
        print('**************************')
        print(type(u))
        #获取未完成项目
        pro = Product.query.filter(Product.progress == '未完成')
        pro_unend = []
        for i in pro:
            a = i.user.all()
            b = []
            if a!= []:
                for j in a:
                    b.append(j.username)
                    if current_user.username not in b:
                       pro_unend.append(i)
            else:
                if i not in pro_unend:
                    pro_unend.append(i)
        # 获取个人未完成项目
        pro_end = []
        for i in p:
            if i.progress == '未完成':
                pro_end.append(i)
        # return pro_end
        #查询个人所有项目

        #获取数据
        if request.method == 'POST':
            #增加项目
            add_pro_id = request.form.get('add_pro')
            print(add_pro_id)
            u = User.query.get(current_user.id)

            add_pro = Product.query.get(int(add_pro_id))


            u.u_project.append(add_pro)

            db.session.add(u)

        return render_template('bumen/kaifa.html', p=p, pro_end = pro_end , pro_unend=pro_unend,endpoint='user.updatepro')

    flash('您还没有登陆，请登陆后进入')
    return redirect(url_for('user.login'))

@login_required
@user.route('/updatepro/')
def updatepro():

    finish_pros = request.args.get('id')
    # print('!!!!!!!!!!!!!!!!!!!!!!!!!')
    print(finish_pros)
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy import create_engine

    ENGINE = create_engine("mysql://root:Root9248*@118.25.43.122:3306/bishe?charset=utf8",
                           convert_unicode=True)
    Session2 = sessionmaker(bind=ENGINE, autocommit=False, autoflush=False)

    session2 = Session2()

    product = session2.query(Product).filter_by(id=int(finish_pros)).first()
    product.progress = "已完成"
    session2.commit()

    return redirect(url_for('user.kaifa'))


#人事部
@user.route('/renshibu/',methods = ['GET','POST'])
def renshi():

    if current_user.is_authenticated:
        if current_user.section != '人事部':
            flash('您不属于人事部')
            return redirect(url_for('main.index'))
        if current_user.part == '部长':
            # user = User.query.filter(User.section != None)
            page = request.args.get('page', 1, type=int)
            pagination = User.query.filter(User.section != None).order_by(User.age).paginate(page=page, per_page=3, error_out=False)


            user = pagination.items
            pagination2 =User.query.filter(User.section == None).order_by(User.age).paginate(page=page, per_page=3, error_out=False)
            nosec_user = pagination2.items
            return render_template('bumen/renshi_b.html',pagination=pagination,pagination2=pagination2,
                                   user= user,nosec_user = nosec_user,endpoint2='user.del_absent',
                                   endpoint3='user.add_absent',endpoint4='user.select_section')
        #未分配部门员工分配部门


        page = request.args.get('page', 1, type=int)
        pagination3 = User.query.filter(User.section != None).order_by(User.age).paginate(page=page, per_page=3,
                                                                                         error_out=False)

        users = pagination3.items


        pagination4 = User.query.filter(User.section == None).order_by(User.age).paginate(page=page, per_page=3,
                                                                                         error_out=False)

        nosec_users= pagination4.items
        return render_template('bumen/renshi.html',users =users,nosec_users = nosec_users,
                               endpoint1 = 'user.add_section',pagination3=pagination3,
                               pagination4=pagination4,endpoint2='user.select_section')
        #分配新用户部门


    flash('您还没有登陆，请登陆后进入')
    return redirect(url_for('user.login'))
@login_required
@user.route('/add_section/')
def add_section():
    id = request.args.get('id')
    u = User.query.filter(User.id == id).first()

    db.session.add(u)
    db.session.commit()
    return redirect(url_for('user.renshi'))

@login_required
@user.route('del_absent')
def del_absent():
    id =request.args.get('id')
    u = User.query.filter(User.id == id).first()
    if u.leave != 0:
        u.leave -= 1
    else:
        u.leave = 0
    db.session.add(u)
    db.session.commit()
    return redirect(url_for('user.renshi'))

@login_required
@user.route('/add_absent/')
def add_absent():
    id =request.args.get('id')
    u = User.query.filter(User.id == id).first()
    if u.leave>=30:
        u.leave = 30
    else:
        u.leave += 1
    db.session.add(u)
    db.session.commit()
    return redirect(url_for('user.renshi'))


@login_required
@user.route('add_select_section')
def select_section():
    id =request.args.get('id')
    u = User.query.filter(User.id == id).first()
    if u.section==None:
        u.section='开发部'
    db.session.add(u)
    db.session.commit()
    return redirect(url_for('user.renshi'))


#后勤部
@user.route('/houqinbu/',methods=['GET','POST'])
def houqin():
    if current_user.is_authenticated:
        if current_user.section != '后勤部':
            flash('您不属于后勤部')
            return redirect(url_for('main.index'))
        elif current_user.part  == '部长':
            u = User.query.filter(User.section == '开发部')
            # 增加新项目
            if request.method == "POST":
                add_b = request.form.get('add')
                add_product = Product(
                    name=add_b,
                    progress='未完成',
                    sections='开发部',
                )
                if Product.query.filter(Product.name == add_b).first():
                    flash('此项目已经存在，请增加新项目')
                    return render_template('bumen/kaifa_b.html')
                db.session.add(add_product)
                db.session.commit()
            p = Product.query.filter(Product.user == None)
            u_pro = []
            for i in u:
                p_b = i.u_project.all()
            return render_template('bumen/kaifa_b.html', u=u, p_b=p_b, p=p)
        u = User.query.filter(User.username == current_user.username).first()
        # pro_u = u.u_project.all()
        p = u.u_project.all()
        print('**************************')
        print(type(u))
        # 获取未完成项目
        pro = Product.query.filter(Product.progress == '未完成')
        pro_unend = []
        for i in pro:
            a = i.user.all()
            b = []
            if a != []:
                for j in a:
                    b.append(j.username)
                    if current_user.username not in b:
                        pro_unend.append(i)
            pro_unend.append(i)
        # 获取个人未完成项目
        pro_end = []
        for i in p:
            if i.progress == '未完成':
                pro_end.append(i)
        # return pro_end
        # 查询个人所有项目

        # 获取数据
        if request.method == 'POST':
            # 增加项目
            add_pro_id = request.form.get('add_pro')
            u = User.query.get(current_user.id)
            add_pro = Product.query.get(int(add_pro_id))
            u.u_project.append(add_pro)
            db.session.add(u)



        return render_template('bumen/houqin.html', p=p, pro_end=pro_end, pro_unend=pro_unend,endpoint='user.updatepros')
    flash('您还没有登陆，请登陆后进入')
    return redirect(url_for('user.login'))


@login_required
@user.route('/updatepros/')
def updatepros():

    finish_pros = request.args.get('id')
    # print('!!!!!!!!!!!!!!!!!!!!!!!!!')
    print(finish_pros)
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy import create_engine

    ENGINE = create_engine("mysql://root:Root9248*@118.25.43.122:3306/bishe?charset=utf8",
                           convert_unicode=True)
    Session2 = sessionmaker(bind=ENGINE, autocommit=False, autoflush=False)

    session2 = Session2()

    product = session2.query(Product).filter_by(id=int(finish_pros)).first()
    product.progress = "已完成"
    session2.commit()

    return redirect(url_for('user.houqin'))

#修改密码
@user.route('/updatepassword/',methods=['GET','POST'])
@login_required
def update_password():
    form = UpdatePassword()
    if form.validate_on_submit():
        u = User.query.filter(User.username == form.username.data).first()
        if not u:
            flash('无效的用户名,请重新输入')
        elif u.verify_password(form.old_password.data):
        # 用户登录，顺便可以完成记住我的功能，还可以指定有效时间
            u.password=form.new_password.data
            db.session.add(u)
        # db.session.
            flash('密码修改成功，请重新登陆')
        logout_user()
        return redirect(url_for('user.login'))
    return render_template('user/updatepassword.html',form = form)



# if request.method == 'POST':
        #     add_pro = request.form.add_sec.data
        #     add_pros = Product.query.filter(Product.name == add_pro)
        #     pros = Product.query.filter(Product.name==add_pros).first()
            # print(type(pross))

            # u=User.query.filter(User.section=='开发部')
            # # print(type(pros))
            # u.u_project.append(pros)
            # db.session.add(u)
            #提交项目
        # pro_end = Product.query.filter(User.id == current_user.id)