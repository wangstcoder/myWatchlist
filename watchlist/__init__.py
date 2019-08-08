import sys,os
from flask import  Flask
from flask_sqlalchemy import SQLAlchemy  # 导入扩展类
from flask_login import LoginManager



WIN = sys.platform.startswith('win')
if WIN:  # 如果是 Windows 系统，使用三个斜线
    prefix = 'sqlite:///'
else:  # 否则使用四个斜线
    prefix = 'sqlite:////'

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev'  # 等同于 app.secret_key = 'dev'
# 注意更新这里的路径，把 app.root_path 添加到 os.path.dirname() 中
# 以便把文件定位到项目根目录
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(os.path.dirname(app.root_path), os.getenv('DATABASE_FILE', 'data.db'))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 关闭对模型修改的监控

# 在扩展类实例化前加载配置
db = SQLAlchemy(app)

#初始化 Flask-Login 除了实例化扩展类之外，还要实现一个“用户加载回调函数”
login_manager = LoginManager(app) # 实例化扩展类
@login_manager.user_loader
def load_user(user_id):  # 创建用户加载回调函数，接受用户 ID 作为参数
    from watchlist.models import User
    user = User.query.get(int(user_id)) # 用 ID 作为 User 模型的主键查询对应的用户
    return user #返回用户对象

"""
添加了@login_required(登录保护)这个装饰器后，
如果未登录的用户访问对应的 URL，Flask-Login 会把用户重定向到登录页面，
并显示一个错误提示。为了让这个重定向操作正确执行，我们还需要把 login_manager.login_view 的值
设为我们程序的登录视图端点（函数名）
"""
login_manager.login_view = 'login'

"""
对于多个模板内都需要使用的变量，我们可以使用 app.context_processor 装饰器注册一个模板上下文处理函数
这个函数返回的变量（以字典键值对的形式）将会统一注入到每一个模板的上下文环境中，因此可以直接在模板中使用
"""
@app.context_processor
def inject_user():  # 函数名可以随意修改
    from watchlist.models import User
    user = User.query.first()
    return dict(user=user)  # 需要返回字典，等同于return {'user': user}


#为了避免循环依赖（A 导入 B，B 导入 A），把这一行导入语句放到构造文件的结尾
from watchlist import views, errors, commands