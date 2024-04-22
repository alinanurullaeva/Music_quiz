import os
from data import db_session
from flask import Flask, render_template, request, redirect

from data.users import User
from data.quizzes import Quiz

from forms.user import RegisterForm
from forms.quiz import QuizForm

from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from data.login_form import LoginForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)


@app.route("/")
def index():
    # if current_user:
    #    return redirect('/main')
    return render_template('index.html', title='Music Quiz')


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            surname=form.surname.data,
            email=form.email.data,
            position=form.position.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect('/main')
        return render_template('login.html',
                               message="Неправильная почта или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/lk')
def lk():
    user = current_user
    if not user:
        return redirect('/')
    return render_template('lk.html', title='Личный кабинет', user=user)


@app.route('/lk/change', methods=['GET', 'POST'])
def change():
    user = current_user
    if not user:
        return redirect('/')
    return render_template('change', title='Изменить данные', user=user)


@login_manager.user_loader
def load_user(id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/main')
def main():
    if not current_user:
        return redirect("/")
    return render_template('main.html')


@app.route('/create_quiz', methods=['GET', 'POST'])
def create_quiz():
    if not current_user:
        return redirect('/')
    form = QuizForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        for quizzes in db_sess.query(Quiz).filter(Quiz.user_id == current_user.id):
            if quizzes.title == form.title.data:
                return render_template('create_quiz.html', title='Создание викторины',
                                       form=form,
                                       message="Такая викторина уже есть")
        quiz = Quiz(
            title=form.title.data,
            content=form.content.data,
            is_private=(form.is_private.data == 'Приватная'),
            time_limit=form.time_limit.data,
            user_id=current_user.id
        )
        db_sess.add(quiz)
        db_sess.commit()
        return redirect('/main')
    return render_template('create_quiz.html', title='Создание викторины', form=form)


'''@app.route('/form_sample', methods=['POST', 'GET'])
def form_sample():
    if request.method == 'GET':
        return render_template('')
    elif request.method == 'POST':
        print(request.form['email'])
        print(request.form['password'])
        print(request.form['class'])
        print(request.form['sex'])
        return "Форма отправлена"'''

if __name__ == '__main__':
    db_session.global_init("db/music_db.sqlite")
    session = db_session.create_session()

    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
