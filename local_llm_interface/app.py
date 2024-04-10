from flask import Flask, jsonify, render_template, request, Response, session
from flask_session import Session

import ollama

app = Flask(__name__)
app.config['SECRET_KEY'] = 'my_key'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False

Session(app)

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
    
    if 'messages' not in session:
        session['messages'] = []
    
    session['messages'].append({'role': 'user', 'content': user_query})
        
    session.modified = True

    def generate(messages):
        stream = ollama.chat(model=model, messages=messages, stream=True)
        response_content = ""
        for chunk in stream:
            part = chunk['message']['content']
            response_content += part
            yield part 
        
        messages.append({'role': 'assistant', 'content': response_content})
    session.modified = True
    print(session['messages'])

    return Response(generate(session['messages']), mimetype='text/plain')


if __name__ == '__main__':
    app.run(debug=True)
