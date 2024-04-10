from flask import Flask, jsonify, render_template, request, Response
import ollama

app = Flask(__name__)

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

    def generate():
        stream = ollama.chat(model=model, messages=[{'role': 'user', 'content': user_query}], stream=True)
        for chunk in stream:
            yield chunk['message']['content'] 

    return Response(generate(), mimetype='text/plain')


if __name__ == '__main__':
    app.run(debug=True)
