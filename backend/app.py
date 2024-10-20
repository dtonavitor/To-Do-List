import os
import logging
import traceback
import json
from datetime import timedelta
from flask import Flask, request
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt
from bcrypt import hashpw, gensalt, checkpw
from flask_cors import CORS
from flask_redis import FlaskRedis
from Errors import EmptyFieldError, InvalidFieldError, ResponseError, InvalidTokenError, UnauthorizedError, DuplicateFieldError, MissingFieldError, UserNotFoundError
from Users import Users
from Tasks import Tasks

app = Flask(__name__)

# using redis to store the blocklist of tokens and the tasks cache
app.config['REDIS_URL'] = "redis://localhost:6379/0"
redis_client = FlaskRedis(app)

# JWT configuration for user authentication
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=15)
jwt = JWTManager(app)

CORS(app)

logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

users_class = Users()
tasks_class = Tasks()

@jwt.token_in_blocklist_loader
def check_if_token_in_blocklist(jwt_header, jwt_payload):
    jti = jwt_payload['jti']
    entry = redis_client.get(f"blocklist:{jti}")
    return entry is not None
  
def is_rate_limited(ip_address):
    attempts = redis_client.get(f"login_attempts:{ip_address}")
    if attempts and int(attempts) >= 5:
        return True
    return False

@app.route('/logout', methods=['GET'])
@jwt_required()
def logout():
    try:
        jti = get_jwt()['jti']  # JWT ID
        redis_client.set(f"blocklist:{jti}", "", ex=3600)  # Bloqueia o token por 1 hora
        return {'message': 'Logout realizado com sucesso'}, 200
    except Exception as e:
        logger.error(e)
        return {'error': 'Erro ao realizar logout'}, 500
  
@app.route('/login', methods=['POST'])
def login_user():
    try:
        ip_address = request.remote_addr  # IP do cliente

        if is_rate_limited(ip_address):
            return {'error': 'Muitas tentativas de login. Tente mais tarde.'}, 429
        
        data = request.json
        if 'email' not in data or 'password' not in data:
            raise MissingFieldError('Campo não encontrado')
          
        email = data['email']
        password = data['password']
        
        if not issubclass(type(email), str) or not issubclass(type(password), str):
            raise InvalidFieldError('Campo inválido')
          
        if len(email) == 0 or len(password) == 0:
          raise EmptyFieldError('Campo vazio')
        
        user_password = users_class.get_user_password(email)
        
        if user_password is None:
            raise UserNotFoundError('Usuário não encontrado')
          
        if not verify_password(user_password, password):
            raise UnauthorizedError('Email ou senha incorretos')
        
        user_id = users_class.login_user(email, user_password)
        
        if user_id is None:
            raise UserNotFoundError('Email ou senha incorretos')
          
        access_token = create_access_token(identity=user_id)
        
        redis_client.delete(f"login_attempts:{ip_address}")
        return {'access_token': access_token, 'user_id': user_id}, 200
      
    except UnauthorizedError as e:
        redis_client.incr(f"login_attempts:{ip_address}")
        redis_client.expire(f"login_attempts:{ip_address}", 300)
        logger.error(e)
        logger.error(traceback.format_exc())
        return {'error': e.message}, 403
    except (EmptyFieldError, InvalidFieldError, MissingFieldError, UserNotFoundError) as e:
        redis_client.incr(f"login_attempts:{ip_address}")
        redis_client.expire(f"login_attempts:{ip_address}", 300)
        logger.error(e)
        logger.error(traceback.format_exc())
        return {'error': e.message}, 400
    except (ResponseError, Exception) as e:
        redis_client.incr(f"login_attempts:{ip_address}")
        redis_client.expire(f"login_attempts:{ip_address}", 300)
        logger.error(e)
        logger.error(traceback.format_exc())
        return {'error': 'Erro ao logar usuário'}, 500
    

def hash_password(password):
    return hashpw(password.encode('utf-8'), gensalt())

def verify_password(stored_password, provided_password):
    return checkpw(provided_password.encode('utf-8'), stored_password)
  
@app.route('/register', methods=['POST'])
def register_user():
    try:
      data = request.json
      if 'email' not in data or 'password' not in data or 'username' not in data:
          raise MissingFieldError('Campo não encontrado')
        
      email = data['email']
      password = data['password']
      username = data['username']
      
      if not issubclass(type(email), str) or not issubclass(type(password), str) or not issubclass(type(username), str):
          raise InvalidFieldError('Campo inválido')
        
      if email == "" or password == "" or username == "":
        raise EmptyFieldError('Campo vazio')
      
      hashed_password = hash_password(password)  
      user_id = users_class.create_user(username, email, hashed_password)
      if user_id == 500:
          raise ResponseError('Erro ao criar usuário')
      elif user_id == 400:
          raise DuplicateFieldError('Email já cadastrado')        
      
      return {}, 201
        
    except (EmptyFieldError, InvalidFieldError, MissingFieldError, DuplicateFieldError) as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        return {'error': e.message}, 400
    except (ResponseError, Exception) as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        return {'error': 'Erro ao criar usuário'}, 500
      


@app.route('/tasks/<string:user_id>', methods=['GET'])
@jwt_required()
def get_tasks(user_id):
    try:
        current_user = get_jwt_identity()
        
        if current_user is None:
            raise UnauthorizedError('Usuário não autorizado')
        
        if current_user != user_id:
            raise InvalidTokenError('Token inválido')
          
        cache_key = f"tasks:{user_id}"
        cached_tasks = redis_client.get(cache_key)
        
        if cached_tasks:
            tasks = json.loads(cached_tasks)
        else:
            tasks = tasks_class.get_tasks(user_id)
            if tasks:
                redis_client.set(cache_key, json.dumps(tasks), ex=3600)
        
        return {'tasks': tasks}, 200
      
    except (InvalidTokenError, UnauthorizedError) as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        return {'error': e.message}, 403
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        return {'error': 'Erro ao buscar tarefas'}, 500 
  
@app.route('/task', methods=['POST'])
@jwt_required()
def create_task():
    try:
        current_user = get_jwt_identity()
        
        if current_user is None:
            raise UnauthorizedError('Usuário não autorizado')
        
        data = request.json
        
        if 'user_id' not in data or 'name' not in data or 'description' not in data:
            raise MissingFieldError('Campo não encontrado')
          
        user_id = data['user_id']
        name = data['name']
        description = data['description']
        
        if current_user != user_id:
            raise InvalidTokenError('Token inválido')
        
        if not issubclass(type(user_id), str) or not issubclass(type(name), str) or not issubclass(type(description), str):
            raise InvalidFieldError('Campo inválido')
          
        if user_id == "" or name == "" or description == "":
          raise EmptyFieldError('Campo vazio')
        
        task_id = tasks_class.create_task(user_id, name, description)
        
        if task_id == 400:
            raise DuplicateFieldError('Tarefa já cadastrada')
        elif task_id == 500:
            raise ResponseError('Erro ao criar tarefa')
          
        redis_client.delete(f"tasks:{user_id}")
        
        return {'task_id': task_id}, 201
    except (InvalidTokenError, UnauthorizedError) as e:
      logger.error(e)
      logger.error(traceback.format_exc())
      return {'error': e.message}, 403
    except (EmptyFieldError, InvalidFieldError, MissingFieldError, DuplicateFieldError) as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        return {'error': e.message}, 400
    except (ResponseError, Exception) as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        return {'error': 'Erro ao criar tarefa'}, 500
  
@app.route('/task/<string:task_id>', methods=['PUT'])
@jwt_required()
def update_task(task_id):
    try:
        current_user = get_jwt_identity()
        
        if current_user is None:
            raise UnauthorizedError('Usuário não autorizado')
        
        data = request.json
        
        name = ""
        description = ""
        
        if 'name' not in data and 'description' not in data:
            raise MissingFieldError('Campo não encontrado')
        
        if 'name' in data:
          name = data['name']
        if 'description' in data:
          description = data['description'] 
          
        if name == "" and description == "":
            raise EmptyFieldError('Campos vazios')
        
        if not issubclass(type(name), str) or not issubclass(type(description), str):
            raise InvalidFieldError('Campo inválido')
        
        updated, status = tasks_class.update_task(task_id, name, description)
        
        if not updated:
            if status == 400:
                raise DuplicateFieldError('Tarefa já cadastrada')
            else:
              raise ResponseError('Erro ao atualizar tarefa')
        
        redis_client.delete(f"tasks:{current_user}")
        
        return {}, 200
    except UnauthorizedError as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        return {'error': e.message}, 403
    except (InvalidFieldError, MissingFieldError, EmptyFieldError, DuplicateFieldError) as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        return {'error': e.message}, 400
    except (ResponseError, Exception) as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        return {'error': 'Erro ao atualizar tarefa'}, 500
    
  
@app.route('/task/<string:task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    try:
        current_user = get_jwt_identity()
        
        if current_user is None:
            raise UnauthorizedError('Usuário não autorizado')
        
        deleted = tasks_class.delete_task(task_id)
        
        if not deleted:
            raise ResponseError('Erro ao deletar tarefa')
        
        redis_client.delete(f"tasks:{current_user}")
        
        return {}, 200
    except UnauthorizedError as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        return {'error': e.message}, 403
    except ResponseError as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        return {'error': e.message}, 500
  
@app.route('/task/status/<string:task_id>', methods=['PUT'])
@jwt_required()
def update_task_status(task_id):
    try:
        current_user = get_jwt_identity()
        
        if current_user is None:
            raise UnauthorizedError('Usuário não autorizado')
        
        data = request.json
        
        if 'status' not in data:
            raise MissingFieldError('Campo não encontrado')
        
        status = data['status']
        
        if not issubclass(type(status), str):
            raise InvalidFieldError('Campo inválido')
        
        if status == "":
            raise EmptyFieldError('Campo vazio')
        
        updated = tasks_class.change_task_status(task_id, status)
        
        if not updated:
            raise ResponseError('Erro ao atualizar status da tarefa')
        
        redis_client.delete(f"tasks:{current_user}")
        
        return {}, 200
    except UnauthorizedError as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        return {'error': e.message}, 403
    except (InvalidFieldError, MissingFieldError, EmptyFieldError) as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        return {'error': e.message}, 400
    except (ResponseError, Exception) as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        return {'error': 'Erro ao atualizar status da tarefa'}, 500
  
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)