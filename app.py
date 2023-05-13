from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
agent_chain = None

def set_agent_chain(chain):
    global agent_chain
    agent_chain = chain

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.form['input']
    response = agent_chain.run(user_input)
    return jsonify(response)
