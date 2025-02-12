from flask import Flask, request, jsonify, render_template
from langchain.agents import load_tools
from langchain.agents import initialize_agent
from langchain.llms import OpenAI
from serpapi import GoogleSearch
import os
import openai
import pymysql
from dotenv import load_dotenv
import datetime

# Obtener la fecha actual
fecha_actual = datetime.date.today()

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Obtener las claves de API desde las variables de entorno
openai_api_key = os.getenv("OPENAI_API_KEY")
serpapi_api_key = os.getenv("SERPAPI_API_KEY")

app = Flask(__name__)
app.config["DEBUG"] = True

# Load the model
llm = OpenAI(openai_api_key=openai_api_key)

# Load in some tools to use
tools = load_tools(["serpapi", "llm-math"], llm=llm)

# Initialize the agent
agent = initialize_agent(tools, llm, agent="zero-shot-react-description", verbose=True)

username = "admin"
password = "12345678"
host = 'datagpt.cgtlbgxgrxsx.us-east-2.rds.amazonaws.com'
port = 3306

# Conectar a la base de datos
db = pymysql.connect(
    host=host,
    user=username,
    password=password,
    database="datagpt",
    cursorclass=pymysql.cursors.DictCursor
)

# Crear un cursor para ejecutar consultas
cursor = db.cursor()

# Obtener la versión de MySQL
cursor.execute('SELECT VERSION()')
version = cursor.fetchone()
print(f'MySQL version: {version}')

# Crear la tabla si no existe
create_table = '''
CREATE TABLE IF NOT EXISTS datagpt (
    id INT NOT NULL AUTO_INCREMENT,
    date DATE,
    question TEXT,
    answer TEXT,
    links TEXT,
    PRIMARY KEY (id)
)
'''
cursor.execute(create_table)

# Seleccionar la base de datos
use_db = ''' USE datagpt'''
cursor.execute(use_db)

# Inicializar el modelo de lenguaje
llm = OpenAI()

# Cargar las herramientas necesarias
tools = load_tools(["serpapi", "llm-math"], llm=llm)

# Inicializar el agente
agent = initialize_agent(
    tools, llm, agent="zero-shot-react-description", verbose=True)

@app.route('/')
def home():
    """Ruta principal que muestra la página de inicio."""
    return render_template('index.html')

@app.route('/chat')
def arnold():
    """Ruta que muestra la página de chat."""
    return render_template('chat.html')

@app.route('/api/chat', methods=['GET'])
def chat():
    """Ruta para manejar las solicitudes de chat API."""
    question = request.args.get('question')
    fecha_actual = datetime.datetime.today()

    search_params = {
        "engine": "google",
        "q": question,
        "api_key": serpapi_api_key
    }
    search = GoogleSearch(search_params)
    results = search.get_dict()

    relevant_links = [result['link'] for result in results['organic_results']]

    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=question,
        max_tokens=1000,
        n=1,
        stop=None,
        temperature=0.7
    )

    answer = response.choices[0].text.strip()
    links_str = ",".join(relevant_links)

    insert_data = '''
    INSERT INTO datagpt (date, question, answer, links) VALUES (%s, %s, %s, %s)
    '''
    cursor.execute(insert_data, (fecha_actual, question, answer, links_str))
    db.commit()

    return jsonify({'answer': answer, 'relevant_links': relevant_links})

@app.route('/info')
def info():
    """Ruta que muestra la página de información."""
    return render_template('info.html')

@app.route('/skynet')
def skynet():
    """Ruta que muestra la página de Skynet."""
    return render_template('skynet.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=os.environ.get("PORT", 5000))
