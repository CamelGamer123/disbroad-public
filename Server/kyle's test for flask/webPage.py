import flask
from login_handler import LoginHandler
from bs4 import BeautifulSoup

app = flask.Flask(__name__)
login_handler = LoginHandler()
login_handler.load()


@app.route('/')
def main_page():
    html_page = ''
    with open('index.html', 'r') as html:
        for line in html.readlines():
            html_page += line
    return html_page


@app.route('/login_success_test')
def login_success_test():
    return flask.make_response(BeautifulSoup(open('login_success.html', 'r').read(), 'html.parser').prettify())


@app.route('/login')
def login_page(success=True):
    soup = BeautifulSoup(open('login_page.html', 'r').read(), 'html.parser')

    if success:
        response = flask.make_response(soup.prettify())
        return response
    else:
        fail_message = soup.new_tag('p')
        fail_message.string = 'Invalid Credentials. Please try again.'
        soup.body.append(fail_message)
        response = flask.make_response(soup.prettify())
        return response


@app.route('/login_fail')
def login_fail():
    return login_page(False)


@app.route('/login/creds', methods=['GET', 'POST'])
def login_attempt():
    cookie = flask.request.cookies.get('uid')
    if cookie is not None:
        return flask.redirect(flask.url_for('login_success_test'))
    username = flask.request.form['username']
    password = flask.request.form['password']
    error = None
    if flask.request.method == 'POST':
        if login_handler.login(username, password):
            response = flask.make_response(flask.redirect(flask.url_for('login_success_test')))
            response.set_cookie('uid', login_handler.get_uid(username))
            return response
        else:
            return flask.redirect(flask.url_for('login_fail'))


@app.route('/logout')
def logout():
    response = flask.make_response(flask.redirect(flask.url_for('main_page')))
    response.delete_cookie('uid')
    return response


@app.route('/signup')
def register_page(error=None):
    if error is not None:
        soup = BeautifulSoup(open('signup_page.html', 'r').read(), 'html.parser')
        fail_message = soup.new_tag('p')
        fail_message.string = error
        soup.body.append(fail_message)
        response = flask.make_response(soup.prettify())
        return response
    soup = BeautifulSoup(open('signup_page.html', 'r').read(), 'html.parser')
    response = flask.make_response(soup.prettify())
    return response


@app.route('/signup/creds', methods=['GET', 'POST'])
def register_attempt():
    username = flask.request.form['username']
    password = flask.request.form['password']
    confirm_password = flask.request.form['confirm_password']
    email = flask.request.form['email']

    error = None
    if flask.request.method == 'POST':
        if password != confirm_password:
            print(password, confirm_password)
            return register_page('Passwords do not match. Please try again.')
        elif login_handler.get_uid(username) is not None:

            if login_handler.login(username, password):
                response = flask.make_response(flask.redirect(flask.url_for('login_success_test')))
                response.set_cookie('uid', login_handler.get_uid(username))
                return response
            else:
                return register_page('Username already taken. Please try again.')
        else:
            login_handler.add_user(username, password)
            response = flask.make_response(flask.redirect(flask.url_for('login_page')))
            return response


app.run()
