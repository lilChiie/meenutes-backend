from flask import Blueprint, request, jsonify
from sqlalchemy import text
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

from sqlalchemy.exc import SQLAlchemyError, DBAPIError
import re
from extensions import db
from models.user import MeetingUser
from models.employee import Employee  
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadTimeSignature

users_bp = Blueprint('users', __name__)

mail = Mail()
s = URLSafeTimedSerializer("super-secret-key")  # sama dengan JWT secret kamu

@users_bp.record_once
def setup_mail(state):
    app = state.app
    app.config.update(
        MAIL_SERVER="smtp.gmail.com",
        MAIL_PORT=587,
        MAIL_USE_TLS=True,
        MAIL_USERNAME="youremail@gmail.com",  # ubah jadi email kamu
        MAIL_PASSWORD="yourapppassword",      # gunakan App Password Gmail
    )
    mail.init_app(app)

@users_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    nik = data.get('nik')
    user_id = data.get('user_id')
    email = data.get('email')
    password = data.get('password')
    role = 2


    # Validasi input wajib
    if not all([nik, user_id, email, password]):
        return jsonify({"msg": "⚠️ NIK, User ID, Email, dan Password wajib diisi"}), 400

    # Validasi panjang input
    if len(nik) > 6:
        return jsonify({"msg": "⚠️ NIK maksimal 6 karakter"}), 400
    if len(user_id) > 20:
        return jsonify({"msg": "⚠️ User ID maksimal 20 karakter"}), 400
    if len(email) > 50:
        return jsonify({"msg": "⚠️ Email maksimal 50 karakter"}), 400
    if len(password) > 100:
        return jsonify({"msg": "⚠️ Password maksimal 100 karakter"}), 400

    try:
        # Eksekusi stored procedure
        sql = text("""
            EXEC document_registration_user 
                @nik = :nik,
                @user_id = :user_id,
                @email = :email,
                @password = :password
        """)
        
        result = db.session.execute(sql, {
            'nik': nik,
            'user_id': user_id,
            'email': email,
            'password': password,
            'role': role

        })
        
        db.session.commit()

        # Ambil hasil dari SP jika ada
        try:
            result_data = result.fetchone()
            if result_data:
                success_msg = result_data[0] if isinstance(result_data, tuple) else str(result_data)
                return jsonify({"msg": success_msg}), 201
        except:
            pass
        
        return jsonify({"msg": "✅ User berhasil didaftarkan"}), 201

    except Exception as e:
        db.session.rollback()
        
        # Ambil error message dari exception
        error_msg = str(e.orig) if hasattr(e, 'orig') and e.orig else str(e)
        
        # Log untuk debugging
        print(f"=== Registration Error ===")
        print(f"Full error: {error_msg}")
        print(f"========================")
        
        # Extract pesan error yang mengandung emoji dari SP
        # Cari pattern emoji di error message
        emoji_pattern = r'[❌⚠️💥✅].*?(?=\s*\(|$)'
        match = re.search(emoji_pattern, error_msg, re.DOTALL)
        
        if match:
            clean_msg = match.group(0).strip()
            # Bersihkan jika ada text tambahan setelah titik atau newline
            clean_msg = clean_msg.split('\n')[0].strip()
            clean_msg = re.sub(r'\s+', ' ', clean_msg)  # Replace multiple spaces
            
            # Tentukan status code berdasarkan isi pesan
            if "sudah terdaftar" in clean_msg.lower():
                return jsonify({"msg": clean_msg}), 409
            elif "tidak ditemukan" in clean_msg.lower() or "⚠️" in clean_msg:
                return jsonify({"msg": clean_msg}), 404
            elif "💥" in clean_msg:
                return jsonify({"msg": clean_msg}), 500
            else:
                return jsonify({"msg": clean_msg}), 400
        
        # Jika tidak ada emoji, cek kata kunci
        error_lower = error_msg.lower()
        
        if "sudah terdaftar" in error_lower:
            return jsonify({"msg": "❌ User dengan NIK atau User ID ini sudah terdaftar."}), 409
        elif "tidak ditemukan" in error_lower or "employee_code" in error_lower:
            return jsonify({"msg": f"⚠️ Tidak ditemukan data karyawan dengan NIK: {nik}. Pastikan NIK terdaftar di tabel employees."}), 404
        elif "unique" in error_lower or "duplicate" in error_lower:
            return jsonify({"msg": "❌ User dengan NIK atau User ID ini sudah terdaftar."}), 409
        else:
            # Fallback error message
            return jsonify({"msg": "💥 Terjadi kesalahan pada server. Silakan coba lagi."}), 500

    
# LOGIN
@users_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    userid = data.get('userid')
    password = data.get('password')

    if not userid or not password:
        return jsonify({"msg": "User ID and Password are required"}), 400

    user = MeetingUser.query.filter_by(userid=userid).first()
    if not user:
        return jsonify({"msg": "User not found"}), 404

    # Plain-text comparison (NOT SECURE)
    if user.password != password:
        return jsonify({"msg": "Incorrect password"}), 401

    access_token = create_access_token(identity=user.nik)
    return jsonify({
        "msg": "Login successful",
        "access_token": access_token,
        "user": {
            "nik": user.nik,
            "userid": user.userid,
            "username": user.username,
            "email": user.email,
            "role": user.role
        }
    }), 200

@users_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    email = data.get('email')

    if not email:
        return jsonify({"msg": "Email wajib diisi"}), 400

    user = MeetingUser.query.filter_by(email=email).first()
    if not user:
        return jsonify({"msg": "Email tidak terdaftar"}), 404

    # Generate token valid 1 jam
    token = s.dumps(email, salt='password-reset-salt')
    reset_link = f"http://localhost:5173/reset-password/{token}"

    msg = Message("Reset Password Request",
                  sender="youremail@gmail.com",
                  recipients=[email])
    msg.body = f"Klik link berikut untuk reset password kamu:\n{reset_link}\n\nLink ini hanya berlaku 1 jam."
    mail.send(msg)

    return jsonify({"msg": "Link reset password telah dikirim ke email kamu."}), 200

@users_bp.route('/reset-password/<token>', methods=['POST'])
def reset_password(token):
    data = request.get_json()
    new_password = data.get('new_password')

    if not new_password:
        return jsonify({"msg": "Password baru wajib diisi"}), 400

    try:
        email = s.loads(token, salt='password-reset-salt', max_age=3600)  # token berlaku 1 jam
    except SignatureExpired:
        return jsonify({"msg": "Token kadaluarsa"}), 400
    except BadTimeSignature:
        return jsonify({"msg": "Token tidak valid"}), 400

    user = MeetingUser.query.filter_by(email=email).first()
    if not user:
        return jsonify({"msg": "User tidak ditemukan"}), 404

    # Update password ke hashed
    user.password = generate_password_hash(new_password)
    db.session.commit()

    return jsonify({"msg": "Password berhasil diperbarui"}), 200



@users_bp.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    user_id = int(get_jwt_identity())
    user = MeetingUser.query.get(user_id)

    return jsonify({
        "user": {
            "nik": user.nik,
            "userid": user.userid,
            "username": user.username,
            "email": user.email,
            "role": user.role
        }
    })


# CRUD USER

@users_bp.route("/", methods=["GET"])
def get_users():
    users = MeetingUser.query.all()
    return jsonify([
        {
            "nik": u.nik,
            "userid": u.userid,
            "username": u.username,
            "email": u.email,
            "role": u.role
        }
        for u in users
    ]), 200


@users_bp.route("/", methods=["POST"])
def create_user():
    data = request.get_json()

    nik = data.get("nik")
    user_id = data.get("user_id")
    email = data.get("email")
    role = data.get("role")
    password = data.get("password")


    # Validasi input required
    if not all([nik, user_id, email, role]):
        return jsonify({"msg": "NIK, User ID, Email, and Role are required"}), 400

    try:
        # Generate default password (bisa disesuaikan dengan kebijakan perusahaan)
        # Contoh: password default adalah "Welcome123!" atau bisa generate random
        from werkzeug.security import generate_password_hash
        default_password = "Welcome123!"  # Password default untuk user baru
       
        
        sql = text("""
            EXEC admin_add_user 
                @nik = :nik,
                @user_id = :user_id,
                @email = :email,
                @password = :password,
                @role = :role
        """)
        
        result = db.session.execute(sql, {
            'nik': nik,
            'user_id': user_id,
            'email': email,
            'password': password,
            'role': role 
        })
        
        db.session.commit()

        return jsonify({
            "msg": "User created successfully",
            "default_password": default_password  # Opsional: kirim ke frontend untuk ditampilkan ke admin
        }), 201

    except Exception as e:
        db.session.rollback()
        error_msg = str(e)
        
        # Handle specific errors from stored procedure
        if "sudah terdaftar" in error_msg.lower() or "already registered" in error_msg.lower():
            return jsonify({"msg": "User dengan NIK atau User ID ini sudah terdaftar"}), 400
        
        if "tidak ditemukan data karyawan" in error_msg.lower():
            return jsonify({"msg": "NIK tidak ditemukan di tabel employees. Pastikan NIK valid"}), 400
            
        if "format email tidak valid" in error_msg.lower():
            return jsonify({"msg": "Format email tidak valid"}), 400
        
        return jsonify({"msg": f"Error: {error_msg}"}), 500


@users_bp.route("/<string:nik>", methods=["PUT"])
def update_user(nik):
    data = request.get_json()
    user = MeetingUser.query.filter_by(nik=nik).first()

    if not user:
        return jsonify({"error": "User not found"}), 404

    try:
        user.userid = data.get("userid", user.userid)
        user.username = data.get("username", user.username)
        user.email = data.get("email", user.email)
        user.role = data.get("role", user.role)

        db.session.commit()
        return jsonify({"message": "User updated successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


@users_bp.route("/<string:nik>", methods=["DELETE"])
def delete_user(nik):
    user = MeetingUser.query.get(nik)
    if not user:
        return jsonify({"error": "User not found"}), 404

    try:
        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": "User deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

@users_bp.route("/validate-nik/<nik>", methods=["GET"])
def validate_nik(nik):
    try:
        sql = text("""
            SELECT employee_code, 
                   CONCAT(first_name, ' ', last_name) as full_name
            FROM [meeting_management_db].[dbo].[employees]
            WHERE employee_code = :nik
        """)
        result = db.session.execute(sql, {'nik': nik}).fetchone()
        
        if result:
            return jsonify({
                "valid": True,
                "employee_code": result.employee_code,
                "full_name": result.full_name
            }), 200
        else:
            return jsonify({
                "valid": False,
                "msg": "NIK not found in employee database"
            }), 404
            
    except Exception as e:
        return jsonify({"msg": f"Error: {str(e)}"}), 500