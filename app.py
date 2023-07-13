from flask import Flask, request, jsonify, render_template
from langchain.agents import load_tools
from langchain.agents import initialize_agent
from langchain.llms import OpenAI
from serpapi import GoogleSearch
import os
import openai

os.environ["OPENAI_API_KEY"] = "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"
os.environ["SERPAPI_API_KEY"] = "a5bf812b4ac1500d13b11dad7039b34ecfe2a8999698156aa167f1c50e4e4ea7"

app = Flask(__name__)
app.config["DEBUG"] = True

# Load the model
llm = OpenAI()

# Load in some tools to use
tools = load_tools(["serpapi", "llm-math"], llm=llm)

# Initialize the agent
agent = initialize_agent(tools, llm, agent="zero-shot-react-description", verbose=True)

@app.route('/api/chat', methods=['GET'])
def chat():
    """
    Endpoint que responde a las solicitudes GET en '/api/chat'.
    Recibe la pregunta como parámetro en la URL ('question').
    Utiliza el modelo ChatGPT de OpenAI para generar una respuesta a la pregunta.
    También realiza una búsqueda en Google utilizando la API de SerpApi y devuelve enlaces relevantes.

    Returns:
        JSON: Una respuesta JSON que contiene la respuesta generada y los enlaces relevantes.
    """
    question = request.args.get('question')

    # Buscar en Google utilizando SerpApi
    search_params = {
        "engine": "google",
        "q": question,
        "api_key": 'a5bf812b4ac1500d13b11dad7039b34ecfe2a8999698156aa167f1c50e4e4ea7'
    }
    search = GoogleSearch(search_params)
    results = search.get_dict()

    # Obtener los enlaces relevantes de los resultados de búsqueda
    relevant_links = [result['link'] for result in results['organic_results']]

    # Generar respuesta utilizando ChatGPT
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=question,
        max_tokens=1000,
        n=1,
        stop=None,
        temperature=0.7
    )

    # Obtener la respuesta generada
    answer = response.choices[0].text.strip()

    return jsonify({'answer': answer, 'relevant_links': relevant_links})

@app.route('/')
def index():
    """
    Página de inicio que muestra un template llamado 'index.html'.
    """
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=os.environ.get("PORT", 5000))