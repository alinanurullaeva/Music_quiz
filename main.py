import os
import datetime
from data import db_session
from flask import Flask, render_template, request, redirect, url_for

from data.users import User
from data.quizzes import Quiz
from data.composers import Composer
from data.compositions import Composition
from data.results import Result

from forms.user import RegisterForm
from forms.change import ChangeForm, ChangePasswordForm
from forms.quiz import QuizForm, FindCompositionForm
from forms.select_quiz import SelectForm, FindForm, MyQuiz
from forms.test import StartForm

from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from data.login_form import LoginForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)



@app.route("/")
def index():
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
        print(user)
        if user and user.check_password(form.password.data):
            print(1)
            login_user(user, remember=form.remember_me.data)
            print(2)
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
    form = ChangeForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == current_user.id).first()
        user.name = form.name.data
        user.surname = form.surname.data
        db_sess.commit()
        return redirect('/lk')
    return render_template('change.html', title='Изменить данные', form=form, user=user)


@app.route('/lk/change_password', methods=['GET', 'POST'])
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == current_user.id).first()
        if user.check_password(form.old_password.data):
            if form.new_password.data != form.password_again.data:
                return render_template('change_password.html', title='Изменить пароль',
                                       form=form,
                                       message="Пароли не совпадают")
            user.set_password(form.new_password.data)
            db_sess.commit()
            return redirect('/lk')
        return render_template('change_password.html',
                               message="Неправильный старый пароль",
                               form=form)
    return render_template('change_password.html', title='Изменить пароль', form=form)


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
    return render_template('main.html', title='Главная страница')


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
            is_private=form.is_private.data,
            time_limit=form.time_limit.data,
            user_id=current_user.id
        )
        db_sess.add(quiz)
        db_sess.commit()
        return redirect('/main')
    return render_template('create_quiz.html', title='Создание викторины', form=form)


@app.route('/create_quiz/compositions_list', methods=['GET', 'POST'])
def compositions_list():
    if not current_user:
        return redirect('/')
    form = FindCompositionForm()
    db_sess = db_session.create_session()
    if form.validate_on_submit():
        arr = []
        composition_list = db_sess.query(Composition)
        if form.find_composition.data:
            composition_list = composition_list.filter(Composition.title.in_([form.find_composition.data]))
        arr2 = []
        for i in composition_list:
            arr2.append(i.composer_id)
        if form.find_composer.data:
            composers = db_sess.query(Composer).filter(User.id.in_(arr2))
            composers = composers.filter(Composer.name.in_([form.find_composer.data]))
            arr3 = []
            for i in composers:
                arr3.append(i.id)
            composition_list = composition_list.filter(Composition.composer_id.in_(arr3))
        for i in composition_list:
            composer = db_sess.query(Composer).filter(Composer.id == i.composer_id).first()
            arr.append(', '.join([str(i.id), composer.name, i.title]))
        return render_template('compositions_list.html', title='Список произведений', form=form, arr=arr)
    composition_list = db_sess.query(Composition)
    arr = []
    for i in composition_list:
        composer = db_sess.query(Composer).filter(Composer.id == i.composer_id).first()
        arr.append(', '.join([str(i.id), composer.name, i.title]))
    return render_template('compositions_list.html', title='Список произведений', form=form, arr=arr)


@app.route('/select_quiz', methods=['GET', 'POST'])
def select_quiz():
    if not current_user:
        return redirect('/')
    form = SelectForm()
    db_sess = db_session.create_session()
    compositions2_list = db_sess.query(Composition)
    arr = []
    for i in compositions2_list:
        composer = db_sess.query(Composer).filter(Composer.id == i.composer_id).first()
        arr.append(', '.join([composer.name, i.title]))
    if form.validate_on_submit():
        print(1)
        return render_template('select_quiz.html', form=form)
    return render_template('select_quiz.html', form=form)


@app.route('/select_quiz/quiz_list', methods=['GET', 'POST'])
def quiz_list():
    if not current_user:
        return redirect('/')
    form = FindForm()
    db_sess = db_session.create_session()
    if form.validate_on_submit():
        arr = []
        quizzes_list = db_sess.query(Quiz).filter(Quiz.is_private == 0)
        if form.find_quiz.data:
            quizzes_list = quizzes_list.filter(Quiz.title.in_([form.find_quiz.data]))
        arr2 = []
        for i in quizzes_list:
            arr2.append(i.user_id)
        if form.find_user_name.data:
            users = db_sess.query(User).filter(User.id.in_(arr2))
            users = users.filter(User.name.in_([form.find_user_name.data]))
            arr3 = []
            for i in users:
                arr3.append(i.id)
            quizzes_list = quizzes_list.filter(Quiz.user_id.in_(arr3))
        if form.find_user_surname.data:
            users = db_sess.query(User).filter(User.id.in_(arr2))
            users = users.filter(User.surname.in_([form.find_user_surname.data]))
            arr3 = []
            for i in users:
                arr3.append(i.id)
            quizzes_list = quizzes_list.filter(Quiz.user_id.in_(arr3))
        for i in quizzes_list:
            user = db_sess.query(User).filter(User.id == i.user_id).first()
            arr.append(', '.join([str(i.id), i.title, user.name + ' ' + user.surname]))
        return render_template('quiz_list.html', form=form, arr=arr)
    quizzes_list = db_sess.query(Quiz).filter(Quiz.is_private == 0)
    arr = []
    for i in quizzes_list:
        user = db_sess.query(User).filter(User.id == i.user_id).first()
        arr.append(', '.join([str(i.id), i.title, user.name + ' ' + user.surname]))
    return render_template('quiz_list.html', title='Список викторин', form=form, arr=arr)


@app.route('/my_quizzes', methods=['GET', 'POST'])
def my_quizzes():
    if not current_user:
        return redirect('/')
    form = SelectForm()
    db_sess = db_session.create_session()
    compositions2_list = db_sess.query(Composition)
    arr = []
    for i in compositions2_list:
        composer = db_sess.query(Composer).filter(Composer.id == i.composer_id).first()
        arr.append(', '.join([composer.name, i.title]))
    if form.validate_on_submit():
        print(1)
        return render_template('my_quizzes.html', title='Мои викторины', form=form)
    return render_template('my_quizzes.html', title='Мои викторины', form=form)


@app.route('/my_quizzes/my_quiz_list', methods=['GET', 'POST'])
def my_quiz_list():
    if not current_user:
        return redirect('/')
    form = MyQuiz()
    db_sess = db_session.create_session()
    if form.validate_on_submit():
        arr = []
        quizzes_list = db_sess.query(Quiz).filter(Quiz.user_id == current_user.id)
        if form.find_quiz.data:
            quizzes_list = quizzes_list.filter(Quiz.title.in_([form.find_quiz.data]))
        for i in quizzes_list:
            user = db_sess.query(User).filter(User.id == i.user_id).first()
            arr.append(', '.join([str(i.id), i.title, user.name + ' ' + user.surname]))
        return render_template('my_quiz_list.html', title='Мои викторины', form=form, arr=arr)
    quizzes_list = db_sess.query(Quiz).filter(Quiz.user_id == current_user.id)
    arr = []
    for i in quizzes_list:
        user = db_sess.query(User).filter(User.id == i.user_id).first()
        arr.append(', '.join([str(i.id), i.title, user.name + ' ' + user.surname]))
    return render_template('my_quiz_list.html', title='Мои викторины', form=form, arr=arr)


@app.route('/quiz/<quiz_id>')
def quiz(quiz_id):
    if not current_user:
        return redirect('/')
    db_sess = db_session.create_session()
    quiz1 = db_sess.query(Quiz).filter(Quiz.id == quiz_id).first()
    user = db_sess.query(User).filter(User.id == quiz1.user_id).first()
    if quiz1.is_private:
        private = 'Да'
    else:
        private = 'Нет'
    if user.id == current_user.id:
        flag = True
    else:
        flag = False
    return render_template('quiz.html', title='Викторина', user=user, quiz=quiz1, private=private, flag=flag)


@app.route('/quiz/list_compositions', methods=['GET', 'POST'])
def list_compositions():
    if not current_user:
        return redirect('/')
    form = FindCompositionForm()
    db_sess = db_session.create_session()
    if form.validate_on_submit():
        arr = []
        composition_list = db_sess.query(Composition)
        if form.find_composition.data:
            composition_list = composition_list.filter(Composition.title.in_([form.find_composition.data]))
        arr2 = []
        for i in composition_list:
            arr2.append(i.composer_id)
        if form.find_composer.data:
            composers = db_sess.query(Composer).filter(User.id.in_(arr2))
            composers = composers.filter(Composer.name.in_([form.find_composer.data]))
            arr3 = []
            for i in composers:
                arr3.append(i.id)
            composition_list = composition_list.filter(Composition.composer_id.in_(arr3))
        for i in composition_list:
            composer = db_sess.query(Composer).filter(Composer.id == i.composer_id).first()
            arr.append(', '.join([str(i.id), composer.name, i.title]))
        return render_template('compositions_list2.html', form=form, arr=arr)
    composition_list = db_sess.query(Composition)
    arr = []
    for i in composition_list:
        composer = db_sess.query(Composer).filter(Composer.id == i.composer_id).first()
        arr.append(', '.join([str(i.id), composer.name, i.title]))
    return render_template('compositions_list2.html', title="Список произведений", form=form, arr=arr)


@app.route('/test/music/<int:result_id>/<int:composition_id>', methods=["POST", "GET"])
def music(result_id, composition_id):
    song = 'music/' + str(composition_id) + '.mp3'
    return render_template('music.html', song=song)


@app.route('/test/<quiz_id>', methods=['GET', 'POST'])
def test(quiz_id):
    if not current_user:
        redirect('/')
    form = StartForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        quiz = db_sess.query(Quiz).filter(Quiz.id == quiz_id).first().content.split(';')
        print(quiz)
        result = Result()
        result.user_id = current_user.id
        result.quiz_id = quiz_id
        result.student_answers = ';'.join(['0' for i in range(len(quiz))])
        arr = []
        for i in quiz:
            composition = db_sess.query(Composition).filter(Composition.id == i).first()
            title = composition.title
            composer = db_sess.query(Composer).filter(Composer.id == composition.composer_id).first().name
            arr.append(composer + ', ' + title)
        result.right_answers = ';'.join(arr)
        result.scores = result.student_answers = ';'.join(['0' for i in range(len(quiz))])
        result.total_score = 0
        result.taking_date = datetime.datetime.now()
        db_sess.add(result)
        db_sess.commit()
        link = '/test/music/' + str(result.id) + '/1'
        return render_template(link)
    return render_template('test.html', title='Тест', form=form)


if __name__ == '__main__':
    db_session.global_init("db/music_db.sqlite")
    session = db_session.create_session()

    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
