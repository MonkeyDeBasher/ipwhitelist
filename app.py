from flask import Flask, request, abort
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ips.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Модель для хранения разрешённых IP-адресов
class AllowedIP(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(45), unique=True, nullable=False)  # IPv6 совместимость

# Создание базы данных
@app.before_first_request
def create_tables():
    db.create_all()

# Проверка IP-адреса перед каждым запросом
@app.before_request
def check_ip():
    client_ip = request.remote_addr  # Получаем IP-адрес клиента
    allowed_ip = AllowedIP.query.filter_by(ip_address=client_ip).first()
    if not allowed_ip:
        abort(403)  # Если IP-адрес не найден в базе данных, возвращаем ошибку 403

@app.route('/')
def home():
    return "Добро пожаловать! Ваш IP-адрес разрешён."

@app.route('/add_ip/<ip>')
def add_ip(ip):
    """Маршрут для добавления IP в базу (только для администраторов)."""
    if request.remote_addr != '127.0.0.1':  # Этот маршрут доступен только с localhost
        abort(403)

    if not AllowedIP.query.filter_by(ip_address=ip).first():
        new_ip = AllowedIP(ip_address=ip)
        db.session.add(new_ip)
        db.session.commit()
        return f"IP {ip} добавлен в список разрешённых."
    return f"IP {ip} уже в списке разрешённых."

@app.errorhandler(403)
def forbidden(e):
    return "Доступ запрещён: ваш IP-адрес не разрешён.", 403

if __name__ == '__main__':
    app.run(debug=True)
