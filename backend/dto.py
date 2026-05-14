from dao import sql 
from werkzeug.security import generate_password_hash, check_password_hash
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import uuid

def response_wrapper(status, message, data=None):
    """
    Función helper para estandarizar todas las respuestas del backend.
    Asegura que el frontend de Vue siempre reciba el mismo formato.

    Parámetros:
        status (str): Código de estado interno (ej: "000" para éxito, "100" para error).
        message (str): Mensaje descriptivo para mostrar al usuario.
        data (dict/list, opcional): Los datos a devolver (ej: lista de eventos).

    Retorna:
        dict: Diccionario formateado con 'status', 'success' y 'data' (si existe).
    """
    if data is not None:
        return {"status": {"code": status, "msg": message}, "data": data, "success": status == "000"}
    return {"status": {"code": status, "msg": message}, "success": status == "000"}


# ==========================================
# LÓGICA DE EVENTOS Y CATEGORÍAS
# ==========================================

def get_todos_los_eventos():
    """
    Obtiene todos los eventos registrados en la base de datos.

    Retorna:
        tuple: (Respuesta formateada, código HTTP).
    """
    query = "SELECT * FROM eventos"
    result = sql.find(query=query, multiple=True)
    
    if result.success:
        return response_wrapper("000", "Eventos cargados correctamente", result.data or []), 200
    else:
        return response_wrapper(result.status or "100", result.message or "Error interno"), result.code or 500

def add_evento_dto(id_organizador, id_categoria, titulo, descripcion, direccion_texto, latitud, longitud, fecha_inicio, fecha_fin, foto_url):
    """
    Inserta un nuevo evento (mercadillo) en la base de datos.

    Parámetros:
        id_organizador (int): ID del usuario que crea el evento.
        id_categoria (int): ID de la categoría del evento.
        titulo (str): Título del evento.
        descripcion (str): Descripción detallada.
        direccion_texto (str): Dirección en formato legible.
        latitud (float): Coordenada GPS.
        longitud (float): Coordenada GPS.
        fecha_inicio (str): Fecha de inicio del evento.
        fecha_fin (str): Fecha de finalización.
        foto_url (str): URL de la imagen de portada.

    Retorna:
        tuple: (Respuesta formateada con el ID generado, código HTTP 201/500).
    """
    query = """
        INSERT INTO eventos (id_organizador, id_categoria, titulo, descripcion, direccion_texto, latitud, longitud, fecha_inicio, fecha_fin, foto_url) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    parameters = (id_organizador, id_categoria, titulo, descripcion, direccion_texto, latitud, longitud, fecha_inicio, fecha_fin, foto_url)
    
    result = sql.insert(query=query, parameters=parameters)
    
    if result.success:
        return response_wrapper("000", "Mercadillo publicado con éxito", {"id_evento": result.data}), 201
    else:
        return response_wrapper("100", "Error al publicar mercadillo en BD"), 500
    
def eliminar_evento_dto(id_evento):
    """
    Elimina un evento de la base de datos por su ID.

    Parámetros:
        id_evento (int): El identificador del evento a borrar.

    Retorna:
        tuple: (Respuesta formateada, código HTTP 200/500).
    """
    query = "DELETE FROM eventos WHERE id_evento = %s"
    result = sql.modify(query=query, parameters=(id_evento,))
    
    if result.success:
        return response_wrapper("000", "Mercadillo eliminado con éxito", {}), 200
    else:
        return response_wrapper("100", "Error al eliminar el mercadillo"), 500
    
def get_todas_las_categorias():
    """
    Obtiene la lista maestra de categorías disponibles.

    Retorna:
        tuple: (Respuesta formateada, código HTTP).
    """
    query = "SELECT * FROM categorias"
    result = sql.find(query=query, multiple=True)
    
    if result.success:
        return response_wrapper("000", "Categorías cargadas correctamente", result.data or []), 200
    else:
        return response_wrapper(result.status or "100", result.message or "Error interno"), result.code or 500


# ==========================================
# LÓGICA DE FAVORITOS
# ==========================================

def add_favorito_dto(id_usuario, id_evento):
    """
    Vincula un evento como favorito para un usuario específico.
    Utiliza INSERT IGNORE para evitar duplicados si el usuario hace clic varias veces.

    Parámetros:
        id_usuario (int): ID del usuario.
        id_evento (int): ID del evento.

    Retorna:
        tuple: (Respuesta formateada, código HTTP).
    """
    if not id_usuario or not id_evento:
        return response_wrapper("111", "Faltan datos obligatorios"), 400

    query = "INSERT IGNORE INTO favoritos (id_usuario, id_evento) VALUES (%s, %s)"
    parameters = (id_usuario, id_evento)
    
    result = sql.insert(query=query, parameters=parameters)
    
    if result.success:
        return response_wrapper("000", "Añadido a favoritos correctamente"), 200
    else:
        return response_wrapper(result.status or "100", result.message or "Error al guardar favorito"), result.code or 500

def remove_favorito_dto(id_usuario, id_evento):
    """
    Elimina la vinculación de un evento como favorito para un usuario.

    Parámetros:
        id_usuario (int): ID del usuario.
        id_evento (int): ID del evento.

    Retorna:
        tuple: (Respuesta formateada, código HTTP).
    """
    if not id_usuario or not id_evento:
        return response_wrapper("111", "Faltan datos obligatorios"), 400

    query = "DELETE FROM favoritos WHERE id_usuario = %s AND id_evento = %s"
    parameters = (id_usuario, id_evento)
    
    result = sql.modify(query=query, parameters=parameters)
    
    if result.success:
        return response_wrapper("000", "Eliminado de favoritos correctamente"), 200
    else:
        return response_wrapper(result.status or "100", result.message or "Error al eliminar favorito"), result.code or 500

def get_favoritos_dto(id_usuario):
    """
    Recupera todos los IDs de los eventos que un usuario ha marcado como favoritos.

    Parámetros:
        id_usuario (int): ID del usuario.

    Retorna:
        tuple: (Respuesta formateada con la lista de IDs, código HTTP).
    """
    if not id_usuario:
        return response_wrapper("111", "Falta el ID del usuario"), 400

    query = "SELECT id_evento FROM favoritos WHERE id_usuario = %s"
    parameters = (id_usuario,)
    
    result = sql.find(query=query, multiple=True, parameters=parameters)
    
    if result.success:
        return response_wrapper("000", "Favoritos obtenidos", result.data or []), 200
    else:
        return response_wrapper(result.status or "100", result.message or "Error interno"), result.code or 500


# ==========================================
# LÓGICA DE USUARIOS Y AUTENTICACIÓN
# ==========================================

def enviar_correo_verificacion(email_destino, token):
    """
    Se conecta al servidor SMTP de Gmail de forma segura (SSL/Puerto 465)
    para enviar el correo con el token de verificación al nuevo usuario.

    Parámetros:
        email_destino (str): El correo proporcionado por el usuario.
        token (str): El UUID generado para verificar la cuenta.

    Retorna:
        bool: True si el correo se envió con éxito, False en caso de error (ej: firewall).
    """
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
        print(f"❌ Error CRÍTICO al enviar correo: {e}")
        return False

def register_user_dto(nombre_completo, email, password, tipo_usuario, telefono):
    """
    Registra un usuario en la base de datos, encripta su contraseña,
    genera un token único y dispara el envío del correo de verificación.

    Parámetros:
        nombre_completo (str): Nombre completo del usuario.
        email (str): Correo electrónico (debe ser único en la BD).
        password (str): Contraseña en texto plano.
        tipo_usuario (str): Rol del usuario ('visitante' u 'organizador').
        telefono (str): Teléfono opcional.

    Retorna:
        tuple: (Respuesta formateada, código HTTP).
    """
    if not email or not password or not nombre_completo:
        return response_wrapper("111", "Faltan datos obligatorios"), 400

    hashed_pw = generate_password_hash(password)
    token_verified = str(uuid.uuid4())

    query = """
        INSERT INTO usuarios (nombre_completo, email, password, tipo_usuario, telefono, token_verified, verified_email)
        VALUES (%s, %s, %s, %s, %s, %s, FALSE)
    """
    parameters = (nombre_completo, email, hashed_pw, tipo_usuario, telefono, token_verified)
    
    result = sql.insert(query=query, parameters=parameters)
    
    if result.success:
        enviar_correo_verificacion(email, token_verified)
        return response_wrapper("000", "Usuario registrado correctamente. Revisa tu correo.", {"id_usuario": result.data}), 201
    elif result.code == 409: 
        return response_wrapper("112", "Ese email ya está registrado"), 409
    else:
        return response_wrapper("100", "Error al registrar usuario"), 500

def login_user_dto(email, password):
    """
    Verifica las credenciales de un usuario y comprueba que su cuenta esté validada
    antes de permitir el acceso.

    Parámetros:
        email (str): Correo del usuario.
        password (str): Contraseña en texto plano a verificar.

    Retorna:
        tuple: (Respuesta formateada con los datos del usuario, código HTTP).
    """
    if not email or not password:
        return response_wrapper("111", "Faltan datos obligatorios"), 400

    query = "SELECT * FROM usuarios WHERE email = %s"
    result = sql.find(query=query, multiple=False, parameters=(email,))
    
    if not result.success or not result.data:
        return response_wrapper("104", "Usuario no encontrado o credenciales incorrectas"), 401

    user = result.data
    
    if not user.get('verified_email'):
        return response_wrapper("105", "Debes verificar tu correo para poder iniciar sesión."), 403
    
    if check_password_hash(user['password'], password):
        del user['password']
        return response_wrapper("000", "Login exitoso", user), 200
    else:
        return response_wrapper("104", "Usuario no encontrado o credenciales incorrectas"), 401
        
def verificar_usuario_dto(token):
    """
    Cambia el estado de un usuario a 'verificado' buscando su token único en la BD.
    Una vez verificado, elimina el token por seguridad.

    Parámetros:
        token (str): Token UUID generado en el registro.

    Retorna:
        tuple: (Respuesta formateada, código HTTP).
    """
    query = "UPDATE usuarios SET verified_email = TRUE, token_verified = NULL WHERE token_verified = %s"
    result = sql.modify(query=query, parameters=(token,))
    
    if result.success:
        return response_wrapper("000", "Cuenta verificada con éxito", {}), 200
    else:
        return response_wrapper("113", "Enlace inválido o cuenta ya verificada", {}), 400

# ==========================================
# GESTIÓN DE PERFIL Y CONFIGURACIÓN
# ==========================================

def update_user_foto_dto(id_usuario, url_foto):
    """
    Actualiza la URL de la foto de perfil de un usuario.

    Parámetros:
        id_usuario (int): ID del usuario a modificar.
        url_foto (str): Nueva URL pública de la imagen.

    Retorna:
        tuple: (Respuesta formateada, código HTTP).
    """
    query = "UPDATE usuarios SET foto_url = %s WHERE id_usuario = %s"
    parameters = (url_foto, id_usuario)
    
    result = sql.modify(query=query, parameters=parameters)
    
    if result.success:
        return response_wrapper("000", "Foto de perfil actualizada", {"foto_url": url_foto}), 200
    else:
        return response_wrapper(result.status or "100", result.message or "Error al actualizar la foto"), 500

def update_user_info_dto(id_usuario, nombre):
    """
    Actualiza el nombre completo de un usuario en la base de datos.

    Parámetros:
        id_usuario (int): ID del usuario.
        nombre (str): Nuevo nombre completo.

    Retorna:
        tuple: (Respuesta formateada, código HTTP).
    """
    query = "UPDATE usuarios SET nombre_completo = %s WHERE id_usuario = %s"
    parameters = (nombre, id_usuario)
    
    result = sql.modify(query=query, parameters=parameters)
    
    if result.success:
        return response_wrapper("000", "Información de perfil actualizada con éxito"), 200
    else:
        return response_wrapper(result.status or "100", result.message or "Error al actualizar el nombre"), 500

def change_password_dto(id_usuario, antigua, nueva):
    """
    Cambia la contraseña de un usuario tras verificar que la antigua es correcta.

    Parámetros:
        id_usuario (int): ID del usuario.
        antigua (str): Contraseña actual en texto plano.
        nueva (str): Nueva contraseña en texto plano.

    Retorna:
        tuple: (Respuesta formateada, código HTTP).
    """
    query_find = "SELECT password FROM usuarios WHERE id_usuario = %s"
    res_find = sql.find(query=query_find, multiple=False, parameters=(id_usuario,))
    
    if not res_find.success or not res_find.data:
        return response_wrapper("104", "Usuario no encontrado"), 404

    if not check_password_hash(res_find.data['password'], antigua):
        return response_wrapper("401", "La contraseña actual es incorrecta"), 401
    
    nueva_encriptada = generate_password_hash(nueva)
    query_update = "UPDATE usuarios SET password = %s WHERE id_usuario = %s"
    
    res_update = sql.modify(query=query_update, parameters=(nueva_encriptada, id_usuario))
    
    if res_update.success:
        return response_wrapper("000", "Contraseña cambiada con éxito"), 200
    else:
        return response_wrapper("100", "Error al actualizar la contraseña en la base de datos"), 500

def update_evento_imagen_dto(id_evento, url_imagen):
    query = "UPDATE eventos SET foto_url = %s WHERE id_evento = %s"
    result = sql.modify(query=query, parameters=(url_imagen, id_evento))
    
    if result.success:
        return response_wrapper("000", "Imagen del evento actualizada", {"imagen_url": url_imagen}), 200
    else:
        return response_wrapper("100", "Error al actualizar la imagen del evento"), 500