from dao import sql 
from werkzeug.security import generate_password_hash, check_password_hash
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import uuid

def response_wrapper(status, message, data=None):
    """
    Función helper para estandarizar todas las respuestas del backend.
    """
    if data is not None:
        return {"status": {"code": status, "msg": message}, "data": data, "success": status == "000"}
    return {"status": {"code": status, "msg": message}, "success": status == "000"}


# ==========================================
# LÓGICA DE EVENTOS Y CATEGORÍAS
# ==========================================

def get_events():
    """
    Obtiene todos los eventos registrados en la base de datos.
    (TRADUCIDO PARA EL FRONTEND)
    """
    query = "SELECT * FROM events"
    result = sql.find(query=query, multiple=True)
    
    if result.success and result.data:
        # TRADUCTOR TEMPORAL: BD en inglés -> Vue en español
        eventos_formateados = []
        for e in result.data:
            eventos_formateados.append({
                'id_evento': e.get('event_id'),
                'id_organizador': e.get('organizer_id'),
                'id_categoria': e.get('category_id'),
                'titulo': e.get('title'),
                'descripcion': e.get('description'),
                'direccion_texto': e.get('address'),
                'latitud': e.get('latitude'),
                'longitud': e.get('longitude'),
                'fecha_inicio': e.get('start_date'),
                'fecha_fin': e.get('end_date'),
                'foto_url': e.get('photo_url')
            })
        return response_wrapper("000", "Eventos cargados correctamente", eventos_formateados), 200
    elif result.success:
        return response_wrapper("000", "Eventos cargados correctamente", []), 200
    else:
        return response_wrapper(result.status or "100", result.message or "Error interno"), result.code or 500

def add_event(id_organizador, id_categoria, titulo, descripcion, direccion_texto, latitud, longitud, fecha_inicio, fecha_fin, foto_url):
    """
    Inserta un nuevo evento (mercadillo) en la base de datos.
    """
    query = """
        INSERT INTO events (organizer_id, category_id, title, description, address, latitude, longitude, start_date, end_date, photo_url) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    parameters = (id_organizador, id_categoria, titulo, descripcion, direccion_texto, latitud, longitud, fecha_inicio, fecha_fin, foto_url)
    
    result = sql.insert(query=query, parameters=parameters)
    
    if result.success:
        return response_wrapper("000", "Mercadillo publicado con éxito", {"id_evento": result.data}), 201
    else:
        return response_wrapper("100", "Error al publicar mercadillo en BD"), 500
    
def delete_event(id_evento):
    """
    Elimina un evento de la base de datos por su ID.
    """
    query = "DELETE FROM events WHERE event_id = %s"
    result = sql.modify(query=query, parameters=(id_evento,))
    
    if result.success:
        return response_wrapper("000", "Mercadillo eliminado con éxito", {}), 200
    else:
        return response_wrapper("100", "Error al eliminar el mercadillo"), 500
    
def get_categories():
    """
    Obtiene la lista maestra de categorías disponibles.
    (TRADUCIDO PARA EL FRONTEND)
    """
    query = "SELECT * FROM categories"
    result = sql.find(query=query, multiple=True)
    
    if result.success and result.data:
        # TRADUCTOR TEMPORAL
        categorias_formateadas = []
        for c in result.data:
            categorias_formateadas.append({
                'id_categoria': c.get('category_id'),
                'nombre': c.get('name'),
                'color_hex': c.get('hex_color')
            })
        return response_wrapper("000", "Categorías cargadas correctamente", categorias_formateadas), 200
    elif result.success:
        return response_wrapper("000", "Categorías cargadas correctamente", []), 200
    else:
        return response_wrapper(result.status or "100", result.message or "Error interno"), result.code or 500


# ==========================================
# LÓGICA DE FAVORITOS
# ==========================================

def add_favorite(id_usuario, id_evento):
    """
    Vincula un evento como favorito para un usuario específico.
    """
    if not id_usuario or not id_evento:
        return response_wrapper("111", "Faltan datos obligatorios"), 400

    query = "INSERT IGNORE INTO favorites (user_id, event_id) VALUES (%s, %s)"
    parameters = (id_usuario, id_evento)
    
    result = sql.insert(query=query, parameters=parameters)
    
    if result.success:
        return response_wrapper("000", "Añadido a favoritos correctamente"), 200
    else:
        return response_wrapper(result.status or "100", result.message or "Error al guardar favorito"), result.code or 500

def remove_favorite(id_usuario, id_evento):
    """
    Elimina la vinculación de un evento como favorito para un usuario.
    """
    if not id_usuario or not id_evento:
        return response_wrapper("111", "Faltan datos obligatorios"), 400

    query = "DELETE FROM favorites WHERE user_id = %s AND event_id = %s"
    parameters = (id_usuario, id_evento)
    
    result = sql.modify(query=query, parameters=parameters)
    
    if result.success:
        return response_wrapper("000", "Eliminado de favoritos correctamente"), 200
    else:
        return response_wrapper(result.status or "100", result.message or "Error al eliminar favorito"), result.code or 500

def get_favorite(id_usuario):
    """
    Recupera todos los IDs de los eventos que un usuario ha marcado como favoritos.
    (TRADUCIDO PARA EL FRONTEND)
    """
    if not id_usuario:
        return response_wrapper("111", "Falta el ID del usuario"), 400

    query = "SELECT event_id FROM favorites WHERE user_id = %s"
    parameters = (id_usuario,)
    
    result = sql.find(query=query, multiple=True, parameters=parameters)
    
    if result.success and result.data:
         # TRADUCTOR TEMPORAL
         favoritos_formateados = []
         for f in result.data:
             favoritos_formateados.append({'id_evento': f.get('event_id')})
         return response_wrapper("000", "Favoritos obtenidos", favoritos_formateados), 200
    elif result.success:
         return response_wrapper("000", "Favoritos obtenidos", []), 200
    else:
        return response_wrapper(result.status or "100", result.message or "Error interno"), result.code or 500


# ==========================================
# LÓGICA DE USUARIOS Y AUTENTICACIÓN
# ==========================================

def send_verification_email(email_destino, token):
    # ... (Sin cambios, es Python puro) ...
    mi_email = "info.mercadillosencasa@gmail.com" 
    mi_password = "aqoxxrkjkfascxlp" 
    
    enlace = f"http://localhost:5173/#/verificar/{token}"
    
    msg = MIMEMultipart()
    msg['From'] = mi_email
    msg['To'] = email_destino
    msg['Subject'] = "Verifica tu cuenta en Mercadillos en Casa 🏠"
    
    cuerpo = f"""
    Hola,
    
    ¡Gracias por unirte a Mercadillos en Casa!
    Para poder iniciar sesión y publicar mercadillos, por favor verifica tu correo haciendo clic en el siguiente enlace:
    
    {enlace}
    
    Si tú no has creado esta cuenta, ignora este mensaje.
    """
    msg.attach(MIMEText(cuerpo, 'plain'))
    
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=10) 
        server.login(mi_email, mi_password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        return False

def register_user(nombre_completo, email, password, tipo_usuario, telefono):
    """
    Registra un usuario en la base de datos.
    """
    if not email or not password or not nombre_completo:
        return response_wrapper("111", "Faltan datos obligatorios"), 400

    hashed_pw = generate_password_hash(password)
    token_verified = str(uuid.uuid4())

    query = """
        INSERT INTO users (users_name, email, password, user_type, phone, token_verified, verified_email)
        VALUES (%s, %s, %s, %s, %s, %s, FALSE)
    """
    parameters = (nombre_completo, email, hashed_pw, tipo_usuario, telefono, token_verified)
    
    result = sql.insert(query=query, parameters=parameters)
    
    if result.success:
        send_verification_email(email, token_verified)
        return response_wrapper("000", "Usuario registrado correctamente. Revisa tu correo.", {"id_usuario": result.data}), 201
    elif result.code == 409: 
        return response_wrapper("112", "Ese email ya está registrado"), 409
    else:
        return response_wrapper("100", "Error al registrar usuario"), 500

def login_user(email, password):
    """
    Verifica las credenciales de un usuario.
    (TRADUCIDO PARA EL FRONTEND)
    """
    if not email or not password:
        return response_wrapper("111", "Faltan datos obligatorios"), 400

    query = "SELECT * FROM users WHERE email = %s"
    result = sql.find(query=query, multiple=False, parameters=(email,))
    
    if not result.success or not result.data:
        return response_wrapper("104", "Usuario no encontrado o credenciales incorrectas"), 401

    user = result.data
    
    if not user.get('verified_email'):
        return response_wrapper("105", "Debes verificar tu correo para poder iniciar sesión."), 403
    
    if check_password_hash(user['password'], password):
        del user['password']
        
        # TRADUCTOR TEMPORAL
        user_formateado = {
            'id_usuario': user.get('user_id'),
            'nombre_completo': user.get('users_name'),
            'email': user.get('email'),
            'tipo_usuario': user.get('user_type'),
            'telefono': user.get('phone'),
            'foto_url': user.get('photo_url')
        }
        
        return response_wrapper("000", "Login exitoso", user_formateado), 200
    else:
        return response_wrapper("104", "Usuario no encontrado o credenciales incorrectas"), 401
        
def verify_user(token):
    """
    Cambia el estado de un usuario a 'verificado'.
    """
    query = "UPDATE users SET verified_email = TRUE, token_verified = NULL WHERE token_verified = %s"
    result = sql.modify(query=query, parameters=(token,))
    
    if result.success:
        return response_wrapper("000", "Cuenta verificada con éxito", {}), 200
    else:
        return response_wrapper("113", "Enlace inválido o cuenta ya verificada", {}), 400

# ==========================================
# GESTIÓN DE PERFIL Y CONFIGURACIÓN
# ==========================================

def update_user_foto(id_usuario, url_foto):
    """
    Actualiza la URL de la foto de perfil de un usuario.
    """
    query = "UPDATE users SET photo_url = %s WHERE user_id = %s"
    parameters = (url_foto, id_usuario)
    
    result = sql.modify(query=query, parameters=parameters)
    
    if result.success:
        return response_wrapper("000", "Foto de perfil actualizada", {"foto_url": url_foto}), 200
    else:
        return response_wrapper(result.status or "100", result.message or "Error al actualizar la foto"), 500

def update_user_info(id_usuario, nombre):
    """
    Actualiza el nombre completo de un usuario en la base de datos.
    """
    query = "UPDATE users SET users_name = %s WHERE user_id = %s"
    parameters = (nombre, id_usuario)
    
    result = sql.modify(query=query, parameters=parameters)
    
    if result.success:
        return response_wrapper("000", "Información de perfil actualizada con éxito"), 200
    else:
        return response_wrapper(result.status or "100", result.message or "Error al actualizar el nombre"), 500

def change_password(id_usuario, antigua, nueva):
    """
    Cambia la contraseña de un usuario.
    """
    query_find = "SELECT password FROM users WHERE user_id = %s"
    res_find = sql.find(query=query_find, multiple=False, parameters=(id_usuario,))
    
    if not res_find.success or not res_find.data:
        return response_wrapper("104", "Usuario no encontrado"), 404

    if not check_password_hash(res_find.data['password'], antigua):
        return response_wrapper("401", "La contraseña actual es incorrecta"), 401
    
    nueva_encriptada = generate_password_hash(nueva)
    query_update = "UPDATE users SET password = %s WHERE user_id = %s"
    
    res_update = sql.modify(query=query_update, parameters=(nueva_encriptada, id_usuario))
    
    if res_update.success:
        return response_wrapper("000", "Contraseña cambiada con éxito"), 200
    else:
        return response_wrapper("100", "Error al actualizar la contraseña en la base de datos"), 500

def update_event_image(id_evento, url_imagen):
    """
    Actualiza la imagen de un evento
    """
    query = "UPDATE events SET photo_url = %s WHERE event_id = %s"
    result = sql.modify(query=query, parameters=(url_imagen, id_evento))
    
    if result.success:
        return response_wrapper("000", "Imagen del evento actualizada", {"imagen_url": url_imagen}), 200
    else:
        return response_wrapper("100", "Error al actualizar la imagen del evento"), 500