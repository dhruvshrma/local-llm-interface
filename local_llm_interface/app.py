from flask import Flask, jsonify, render_template, request, Response
import redis 
import ollama
import uuid
from datetime import datetime
import atexit
import sqlite3

app = Flask(__name__)

redis_conn = redis.Redis(host='localhost', port=6389, db=0, decode_responses=True)

DATABASE = 'conversations.db'

def save_conversations_to_db():
    db = None 
    try:
        db = sqlite3.connect(DATABASE)
        cursor = db.cursor()

        conversation_ids = [key for key in redis_conn.keys('conversation:*') if not key.endswith(':messages')]

        for conversation_id in conversation_ids:
            model, start_time = redis_conn.hmget(conversation_id, 'model', 'start_time')
            cursor.execute('INSERT INTO conversations (id, model, start_time) VALUES (?, ?, ?) ON CONFLICT(id) DO UPDATE SET model = ?, start_time = ?',
                           (conversation_id, model, str(start_time), model, str(start_time)))

            message_ids = redis_conn.lrange(f'{conversation_id}:messages', 0, -1)
            for message_id in message_ids:
                role, content, timestamp_utc = redis_conn.hmget(f'{message_id}', 'role', 'content', 'timestamp')

                cursor.execute('INSERT INTO messages (id, conversation_id, role, content, timestamp_utc) VALUES (?, ?, ?, ?, ?) ON CONFLICT(id) DO NOTHING',
                               (message_id, conversation_id, role, content, str(timestamp_utc)))

        db.commit()
    except Exception as e:
        
        print(f"Error saving conversations to DB: {e}")
        if db:
            db.rollback()
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()

atexit.register(save_conversations_to_db)

def start_conversation(conversation_id, model_name):
    redis_conn.hset(f"conversation:{conversation_id}", "model", model_name)
    redis_conn.hset(f"conversation:{conversation_id}", "start_time", datetime.now().isoformat())

def add_message_to_conversation(conversation_id, role, message):
    message_id = str(uuid.uuid4())
    redis_conn.hmset(f"message:{message_id}", {"content": message, "role": role, "timestamp": datetime.now().isoformat()})
    redis_conn.rpush(f"conversation:{conversation_id}:messages", f"message:{message_id}")

def get_conversation_messages(conversation_id):
    message_ids = redis_conn.lrange(f"conversation:{conversation_id}:messages", 0, -1)
    messages = []
    for message_id in message_ids:
        message = redis_conn.hgetall(message_id)
        messages.append(message)
    return messages


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/api/models')
def get_models():
    try:
        models_info = ollama.list()  
        model_names = [model['name'] for model in models_info['models']] 
        return jsonify({'models': model_names})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    model = data.get('model')
    user_query = data.get('query')
    
    if not model or not user_query:
        return jsonify({'error': 'Model and query are required.'}), 400
    
    conversation_id = data.get('conversation_id')
    print(conversation_id)
    if not conversation_id:
        conversation_id = str(uuid.uuid4())
        start_conversation(conversation_id=conversation_id, model_name=model)
        
    add_message_to_conversation(conversation_id, 'user', user_query)
    try:
        def generate():
            stream = ollama.chat(model=model, messages=get_conversation_messages(conversation_id), stream=True)
            response_content = ""
            for chunk in stream:
                part = chunk['message']['content']
                response_content += part
                yield part 
            add_message_to_conversation(conversation_id, 'assistant', response_content)
        
        response = Response(generate(), mimetype='text/plain')
        response.headers['X-Conversation-ID'] = conversation_id
        return response
    except Exception as e:
        print(f"Error during chat operation: {e}")
        return jsonify({'error': 'Failed to process the chat request.'}), 500


if __name__ == '__main__':
    app.run(debug=True)
