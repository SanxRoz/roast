from flask import Flask, render_template, request, jsonify, Response
import requests
import openai
from bs4 import BeautifulSoup

app = Flask(__name__, template_folder='templates')


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        input = request.form['input']
        return input
    return render_template('./index.html')


@app.route('/submit')
def submit():
    response = Response()
    api_data = request.args.get('input')
    open_ai_cookie = request.cookies.get("not-api-cookie")

    url = api_data
    response = requests.get(url)
    html = response.content

    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text()

    text = text.replace('\n', '')
    
    openai.api_key = f"{open_ai_cookie}"
    completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "system", "content": 'Generate a humorous and entertaining roas of the text of a website that I provide, a roast that will make me laugh out loud!. No more than 400 characters. Give me 1 recommendation to improve the website'},
                                                                               {"role": "user", "content": f"{text}"}],stream=True)
    def generate():
        for chunk in completion:
            if 'content' in chunk['choices'][0]['delta']:
                data= chunk['choices'][0]['delta']['content']
                yield 'data: ' + data + '\n\n'
                # Check for condition to close the connection
            if '' in chunk['choices'][0]['delta']:
                yield 'event: end\ndata: Connection closed\n\n'
                break
        
    return Response(generate(), mimetype='text/event-stream', headers={'Cache-Control': 'no-cache'})
        
if __name__ == '__main__':
    app.run(debug=True)