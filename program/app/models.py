from flask import current_app
from app.extensions import db, login_manager
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime








#管理员
class Admin(UserMixin,db.Model):
    id = db.Column(db.Integer,primary_key=True)
    username =db.Column(db.String(32))
    password_hash =db.Column(db.String(128))




    @property
    def password(self):
        raise AttributeError('不能访问密码属性')

    @password.setter
    def password(self, password):
        # 密码需要加密后存储
        self.password_hash = generate_password_hash(password)

    # 校验密码
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    # 生成账户激活的token
    def generate_activate_token(self, expires_in=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expires_in)
        return s.dumps({'id': self.id})

    # 校验账户激活的token
    @staticmethod
    def check_activate_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False

        a = Admin.query.get(data['id'])

        if not a:
            return False
        if not a.confirmed:
            a.confirmed = True
            db.session.add(a)
            return True


class User(UserMixin, db.Model):
    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(32), unique=True)
    password_hash = db.Column(db.String(128))
    email         = db.Column(db.String(64), unique=True)
    confirmed     = db.Column(db.Boolean, default=False)
    # 头像
    icon          = db.Column(db.String(64), default='default.jpeg')
    age           = db.Column(db.Integer)
    sex           = db.Column(db.String(64))
    phonenumber   = db.Column(db.String(11),unique=True)
    idCard        = db.Column(db.String(255),unique=True)
    part          = db.Column(db.String(5), default='员工')#职位
    section       = db.Column(db.String(5))#部门
    leave         = db.Column(db.Integer,default=0)#请假
    absent        = db.Column(db.Integer,default=0)#旷工
    assignment    = db.Column(db.Integer,default=0)#外派

    u_project     = db.relationship('Product', secondary='project', backref=db.backref('user', lazy='dynamic'),
                               lazy='dynamic')



    #添加反向引用
    # posts = db.relationship('Posts',backref='user',lazy = 'dynamic')

    # favovites = db.relationship('Posts',secondary='collection',backref = db.backref('user',))
    @property
    def password(self):
        raise AttributeError('不能访问密码属性')

    @password.setter
    def password(self, password):
        # 密码需要加密后存储
        self.password_hash = generate_password_hash(password)

    # 校验密码
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    # 生成账户激活的token
    def generate_activate_token(self, expires_in=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expires_in)
        return s.dumps({'id': self.id})

    # 校验账户激活的token
    @staticmethod
    def check_activate_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        u = User.query.get(data['id'])

        if not u:
            return False
        if not u.confirmed:
            u.confirmed = True
            db.session.add(u)
            return True
    #判断是否添加该项目
    def is_addproduct(self,pid):
        u_projects = self.u_project.all()
        u_p =list(filter(lambda p:p.id ==pid,u_projects))
        if len(u_p):
            return True
        return False
    #添加项目
    def add_product(self,pid):
        p =Product.query.get(pid)
        self.u_project.append(p)
    #取消该项目
    def del_product(self,pid):
        p = Product.query.get(pid)
        self.u_project.remove(p)

projects = db.Table('project',
    db.Column('User_id',db.Integer,db.ForeignKey('user.id')),
    db.Column('Product_id',db.Integer,db.ForeignKey('product.id')))




#产品信息
class Product(db.Model):
    id                  = db.Column(db.Integer,primary_key=True)
    name                = db.Column(db.String(32),unique=True)
    sections            = db.Column(db.String(5))
    progress            = db.Column(db.String(5))
    # project_u      = db.relationship('User', secondary='project', backref=db.backref('product', lazy='dynamic'),
    #                            lazy='dynamic')
    # rid = db.Column(db.Integer, index=True,default=0)
    # content = db.Column(db.Text)
    # timestamp = db.Column(db.DateTime,default=datetime.utcnow)



    #人和产品的多对多关系模型






# 该装饰器其实就是一个回调函数
@login_manager.user_loader
def loader_user(uid):
    return User.query.get(uid)

#
# if __name__ == '__main__':
#     db.create_all()


