from flask import Flask, render_template, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import random
from datetime import datetime, timedelta
app = Flask(__name__)
app.secret_key = 'blue-uni-2026-v8-new-board'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///uni.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(100)); phone=db.Column(db.String(20),unique=True)
    password=db.Column(db.String(200)); otp=db.Column(db.String(10))
    otp_exp=db.Column(db.DateTime); bio=db.Column(db.String(200),default='طالب في Blue Uni')
class Post(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    user=db.Column(db.String(100),default='طالب'); text=db.Column(db.Text)
    image=db.Column(db.String(500)); cat=db.Column(db.String(50),default='عام')
    likes=db.Column(db.Integer,default=0); pinned=db.Column(db.Boolean,default=False)
    created=db.Column(db.DateTime,default=datetime.utcnow)
class Comment(db.Model):
    id=db.Column(db.Integer,primary_key=True); post_id=db.Column(db.Integer)
    user=db.Column(db.String(100),default='طالب'); text=db.Column(db.Text)
class Chat(db.Model):
    id=db.Column(db.Integer,primary_key=True); sender=db.Column(db.String(100),default='طالب')
    text=db.Column(db.Text); group=db.Column(db.String(100),default='العام')

with app.app_context():
    db.create_all()
    if not Post.query.first():
        db.session.add(Post(user='أحمد البشير جبريل',text='مرحباً بكم في Blue Uni 🎓 عالم التواصل الجديد لجامعتنا - سجل وابدأ 🔥',image='/static/logo_blue.png',likes=1240,pinned=True))
        db.session.add(Post(user='سارة',text='المختبر اليوم 🧪 تجربة DNA جديدة',image='/static/settings_bg.png',likes=856))
        db.session.commit()

@app.route('/')
def index(): return render_template('index.html')
@app.route('/api/posts')
def posts(): return jsonify([{'id':p.id,'user':p.user,'text':p.text,'image':p.image,'cat':p.cat,'likes':p.likes,'pinned':p.pinned} for p in Post.query.order_by(Post.pinned.desc(),Post.created.desc()).limit(50).all()])
@app.route('/api/post',methods=['POST'])
def add_post():
    d=request.json; db.session.add(Post(user=session.get('name','طالب'),text=d.get('text',''),image=d.get('image',''),cat=d.get('category','عام'))); db.session.commit(); return jsonify({'ok':True})
@app.route('/api/like/<int:id>')
def like(id):
    p=Post.query.get(id); p.likes+=1; db.session.commit(); return jsonify({'ok':True})
@app.route('/api/comments/<int:id>')
def get_c(id): return jsonify([{'user':x.user,'text':x.text} for x in Comment.query.filter_by(post_id=id).all()])
@app.route('/api/comment',methods=['POST'])
def add_c():
    d=request.json; db.session.add(Comment(post_id=d['post_id'],user=session.get('name','طالب'),text=d['text'])); db.session.commit(); return jsonify({'ok':True})
@app.route('/api/chat')
def get_chat():
    g=request.args.get('group','العام'); return jsonify([{'sender':x.sender,'text':x.text} for x in Chat.query.filter_by(group=g).order_by(Chat.id.desc()).limit(50).all()[::-1]])
@app.route('/api/chat',methods=['POST'])
def send_chat():
    d=request.json; db.session.add(Chat(sender=session.get('name','طالب'),text=d['text'],group=d.get('group','العام'))); db.session.commit(); return jsonify({'ok':True})
@app.route('/api/register',methods=['POST'])
def reg():
    d=request.json; code=str(random.randint(1000,9999))
    if User.query.filter_by(phone=d.get('phone')).first(): return jsonify({'msg':'الرقم مسجل قبل كده'})
    u=User(name=d.get('name'),phone=d.get('phone'),password=generate_password_hash(d.get('password','1234')),otp=code,otp_exp=datetime.utcnow()+timedelta(minutes=2)); db.session.add(u); db.session.commit(); session['temp_phone']=d.get('phone'); return jsonify({'msg':'تم التسجيل','code':code})
@app.route('/api/verify',methods=['POST'])
def verify():
    u=User.query.filter_by(phone=session.get('temp_phone')).first()
    if u and u.otp==request.json.get('code'): u.otp=''; db.session.commit(); session['name']=u.name; return jsonify({'ok':True})
    return jsonify({'ok':False})
@app.route('/api/login',methods=['POST'])
def login():
    d=request.json; u=User.query.filter_by(phone=d.get('phone')).first()
    if u and check_password_hash(u.password,d.get('password','')): session['name']=u.name; return jsonify({'ok':True,'name':u.name})
    return jsonify({'ok':False,'msg':'رقم او كلمة سر غلط'})

if __name__=='__main__':
    print('🎓 Blue Uni شغال على 8000')
    app.run(host='0.0.0.0',port=8000,threaded=True)
