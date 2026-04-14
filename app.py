import os
import hashlib
import uuid
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
from werkzeug.utils import secure_filename
from database import init_db, get_db, row_to_dict

app = Flask(__name__)
app.secret_key = 'pichome-secret-key-' + str(uuid.uuid4())

# 配置
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp'}
MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# 确保上传目录存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def get_user_by_id(user_id):
    db = get_db()
    return row_to_dict(db.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone())


def get_user_by_username(username):
    db = get_db()
    return row_to_dict(db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone())


def get_user_by_email(email):
    db = get_db()
    return row_to_dict(db.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone())


@app.route('/')
def index():
    # 检查是否已登录，未登录则重定向到登录页
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    
    user = get_user_by_id(user_id)
    
    page = request.args.get('page', 1, type=int)
    per_page = 20
    offset = (page - 1) * per_page
    
    db = get_db()
    query = '''
        SELECT i.*, u.username 
        FROM images i 
        JOIN users u ON i.user_id = u.id 
        ORDER BY i.created_at DESC 
        LIMIT ? OFFSET ?
    '''
    image_rows = db.execute(query, (per_page, offset)).fetchall()
    images = [row_to_dict(row) for row in image_rows]
    
    total = db.execute('SELECT COUNT(*) FROM images').fetchone()[0]
    total_pages = (total + per_page - 1) // per_page
    
    return render_template('index.html', images=images, page=page, total_pages=total_pages, user=user)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm', '')
        
        if not username or not email or not password:
            flash('请填写所有字段', 'error')
            return redirect(url_for('register'))
        
        if password != confirm:
            flash('两次密码不一致', 'error')
            return redirect(url_for('register'))
        
        if len(password) < 6:
            flash('密码长度至少6位', 'error')
            return redirect(url_for('register'))
        
        if get_user_by_username(username):
            flash('用户名已存在', 'error')
            return redirect(url_for('register'))
        
        if get_user_by_email(email):
            flash('邮箱已被注册', 'error')
            return redirect(url_for('register'))
        
        db = get_db()
        db.execute('INSERT INTO users (username, email, password_hash, created_at) VALUES (?, ?, ?, ?)',
                   (username, email, hash_password(password), datetime.now()))
        db.commit()
        
        flash('注册成功，请登录', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        user = get_user_by_username(username)
        if not user or user['password_hash'] != hash_password(password):
            flash('用户名或密码错误', 'error')
            return redirect(url_for('login'))
        
        session['user_id'] = user['id']
        session['username'] = user['username']
        flash('登录成功', 'success')
        return redirect(url_for('upload'))
    
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('已退出登录', 'success')
    return redirect(url_for('index'))


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('请选择文件', 'error')
            return redirect(url_for('upload'))
        
        file = request.files['file']
        if file.filename == '':
            flash('请选择文件', 'error')
            return redirect(url_for('upload'))
        
        if file and allowed_file(file.filename):
            # 生成唯一文件名
            ext = file.filename.rsplit('.', 1)[1].lower()
            year = datetime.now().strftime('%Y')
            month = datetime.now().strftime('%m')
            
            save_dir = os.path.join(app.config['UPLOAD_FOLDER'], year, month)
            os.makedirs(save_dir, exist_ok=True)
            
            unique_name = f'{uuid.uuid4().hex}.{ext}'
            file_path = os.path.join(save_dir, unique_name)
            file.save(file_path)
            
            # 获取图片尺寸
            try:
                from PIL import Image
                with Image.open(file_path) as img:
                    width, height = img.size
            except:
                width, height = 0, 0
            
            # 获取文件大小
            file_size = os.path.getsize(file_path)
            
            # 标签
            tags = request.form.get('tags', '').strip()
            
            db = get_db()
            db.execute('''
                INSERT INTO images (user_id, filename, original_name, file_path, file_size, width, height, tags, views, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, ?)
            ''', (session['user_id'], unique_name, secure_filename(file.filename), 
                  f'{year}/{month}/{unique_name}', file_size, width, height, tags, datetime.now()))
            db.commit()
            
            flash('上传成功', 'success')
            return redirect(url_for('profile'))
        
        flash('不支持的文件类型', 'error')
        return redirect(url_for('upload'))
    
    return render_template('upload.html', user=get_user_by_id(session['user_id']))


@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = get_user_by_id(session['user_id'])
    db = get_db()
    
    image_rows = db.execute('''
        SELECT * FROM images WHERE user_id = ? ORDER BY created_at DESC
    ''', (session['user_id'],)).fetchall()
    
    images = [row_to_dict(row) for row in image_rows]
    total_size = sum(img['file_size'] for img in images)
    
    return render_template('profile.html', user=user, images=images, total_size=total_size)


@app.route('/image/<int:image_id>')
def image_detail(image_id):
    db = get_db()
    image_row = db.execute('''
        SELECT i.*, u.username 
        FROM images i 
        JOIN users u ON i.user_id = u.id 
        WHERE i.id = ?
    ''', (image_id,)).fetchone()
    
    image = row_to_dict(image_row)
    
    if not image:
        flash('图片不存在', 'error')
        return redirect(url_for('index'))
    
    # 增加浏览量
    db.execute('UPDATE images SET views = views + 1 WHERE id = ?', (image_id,))
    db.commit()
    
    user_id = session.get('user_id')
    user = get_user_by_id(user_id) if user_id else None
    
    return render_template('image.html', image=image, user=user)


@app.route('/delete/<int:image_id>', methods=['POST'])
def delete_image(image_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    db = get_db()
    image_row = db.execute('SELECT * FROM images WHERE id = ?', (image_id,)).fetchone()
    image = row_to_dict(image_row)
    
    if not image:
        flash('图片不存在', 'error')
        return redirect(url_for('index'))
    
    if image['user_id'] != session['user_id']:
        flash('无权删除', 'error')
        return redirect(url_for('index'))
    
    # 删除文件
    full_path = os.path.join(app.config['UPLOAD_FOLDER'], image['file_path'])
    if os.path.exists(full_path):
        os.remove(full_path)
    
    # 删除数据库记录
    db.execute('DELETE FROM images WHERE id = ?', (image_id,))
    db.commit()
    
    flash('删除成功', 'success')
    return redirect(url_for('profile'))


@app.route('/uploads/<path:filename>')
def serve_image(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


# 初始化数据库
init_db()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)