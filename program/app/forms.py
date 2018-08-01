from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField,TextAreaField,IntegerField,SelectField
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError
from app.models import User,Product
from app.extensions import photos


# 用户注册
class RegisterForm(FlaskForm):
    username = StringField('用户名', validators=[Length(1, 20, message='用户名必须在6~20个字符之间')])
    password = PasswordField('密码', validators=[Length(4, 12, message='密码长度必须在4~12个字符之间')])
    confirm = PasswordField('确认密码', validators=[EqualTo('password', message='两次密码不一致')])
    sex = SelectField('性别', choices=[('男', '男'), ('女', '女')], default='男')
    age = StringField('年龄',validators=[Length(2,message='年龄不能为空')])
    email = StringField('邮箱', validators=[Email(message='无效的邮箱格式')])
    idCard = StringField('身份证号', validators=[Length(16, message='身份证号必须为16位')])
    phonenumber = StringField('手机号', validators=[Length(11, message='手机号必须为11位')])
    submit = SubmitField('立即注册')

    # 自定义验证函数，验证username
    def validate_username(self, field):
        if User.query.filter(User.username == field.data).first():
            raise ValidationError('该用户已注册，请选用其他名称')
        # elif User.query.filter(Admin.username == field.data).first():
        #     raise ValidationError('管理员已经存在，不要搞事情')
        return True

    # 自定义验证函数，验证email
    def validate_email(self, field):
        if User.query.filter(User.email == field.data).first():
            raise ValidationError('该邮箱已注册，请选用其他邮箱')
        return True

    def validate_idCard(self, field):
        if User.query.filter(User.idCard == field.data).first():
            raise ValidationError('该身份证号已注册，您确定是新用户吗？')
        return True


    def validate_phonenumber(self, field):
        if User.query.filter(User.phonenumber == field.data).first():
            raise ValidationError('该手机号已注册，请选用其他手机号')

        return True





# 用户登录表单
class LoginForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(message='用户名不能为空')])
    password = PasswordField('密码', validators=[DataRequired(message='密码不能为空')])
    remember = BooleanField('记住我')
    submit = SubmitField('立即登录')

class LoginForm_a(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(message='用户名不能为空')])
    password = PasswordField('密码', validators=[DataRequired(message='密码不能为空')])
    remember = BooleanField('记住我')
    submit = SubmitField('立即登录')


# 上传头像表单
class UploadForm(FlaskForm):
    icon = FileField('请选择你的头像', validators=[FileRequired('请选择文件'), FileAllowed(photos, '只能上传图片')])
    submit = SubmitField('上传')

#修改密码表单
class UpdatePassword(FlaskForm):
    username = StringField('用户名',validators=[DataRequired(message='用户名不能为空')])
    old_password = PasswordField('旧密码',validators=[DataRequired(message='请输入旧密码')])
    new_password = PasswordField('新密码', validators=[DataRequired(message='请输入旧密码')])
    confirm = PasswordField('确认新密码', validators=[DataRequired(message='请输入旧密码')])
    submit = SubmitField('确认修改')


class UserInformation(FlaskForm):
    name = StringField('姓名',validators=[DataRequired(message='姓名不能为空')])
    sex = SelectField('性别', choices=[('男', '男'), ('女', '女')], default='男')
    age = IntegerField('年龄')
    idCard = StringField('身份证号',validators=[Length(18,message='身份证号不能为空')])
    phonenumber = StringField('手机号',validators=[Length(11,message='手机号不能为空')])

    submit = SubmitField('提交信息')
# class ContentForm(FlaskForm):
#
#     content = TextAreaField('',validators=[Length(3,140,message='你想说什么？')])
#     submit = SubmitField()

# class PostsForm(FlaskForm):
#     content = TextAreaField('',validators=[Length(3,140,message='爱我你就写点什么吧(3~140)')],render_kw={'placeholder':'谈谈你的想法'})
#     submit = SubmitField('发表')

#增加用户
class AddUserForm(FlaskForm):
    username = StringField('用户名', validators=[Length(1, 20, message='用户名必须在6~20个字符之间')])
    password = StringField('密码', validators=[Length(4, 12, message='密码长度必须在4~12个字符之间')])
    sex = SelectField('性别', choices=[('男', '男'), ('女', '女')], default='男')
    age = StringField('年龄',validators=[Length(2,message='年龄不能为空')])
    email = StringField('邮箱', validators=[Email(message='无效的邮箱格式')])
    idCard = StringField('身份证号', validators=[Length(16, message='身份证号必须为16位')])
    phonenumber = StringField('手机号', validators=[Length(11, message='手机号必须为11位')])
    section = SelectField('部门', choices=[('开发部', '开发部'), ('人事部', '人事部'), ('后勤部', '开发部')])
    part = SelectField('职位', choices=[('员工', '员工'), ('部长', '部长')], default='员工')
    submit = SubmitField('增加用户')

    # 自定义验证函数，验证username
    def validate_username(self, field):
        if User.query.filter(User.username == field.data).first():
            raise ValidationError('该用户已存在')
        # elif User.query.filter(Admin.username == field.data).first():
        #     raise ValidationError('管理员已经存在，不要搞事情')

        return True

    # 自定义验证函数，验证email
    def validate_email(self, field):
        if User.query.filter(User.email == field.data).first():
            raise ValidationError('该邮箱已注册')

        return True

    def validate_idCard(self, field):
        if User.query.filter(User.idCard == field.data).first():
            raise ValidationError('该身份证号已注册')

        return True


    def validate_phonenumber(self, field):
        if User.query.filter(User.phonenumber == field.data).first():
            raise ValidationError('该手机号已注册')

        return True

class AddProduct(FlaskForm):
    name = StringField('项目名称', validators=[Length(1, 20, message='项目名必须在1~20个字符之间')])
    section = SelectField('部门',choices=[('开发部','开发部'),('人事部','人事部'),('后勤部','后勤部')],default='开发部')
    progress = SelectField('项目进度',choices=[('未完成','未完成'),('已完成','已完成')],default='未完成')
    submit = SubmitField('增加项目')

    def validate_project(self, field):
        if Product.query.filter(Product.name == field.data).first():
            raise ValidationError('该项目已存在，请添加其他项目')
        return True