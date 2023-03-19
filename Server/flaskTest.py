from flask import Flask, render_template, request
# from markupsafe import escape
from os import getcwd

directory = getcwd()
app = Flask(__name__, template_folder='template', static_folder='static')


@app.route('/<username>')
def user_page(username):
    html_page = f' <h1> Hello {username} </h1>'
    return html_page


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        message = request.form.get('UserChat')
        if message:
            print(message)
        else:
            print('message is empty')
        return render_template('index.html')
    elif request.method == 'GET':
        return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)

