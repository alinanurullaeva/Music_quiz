import os
import datetime
from data import db_session
from flask import Flask, render_template, redirect

from data.users import User
from data.quizzes import Quiz
from data.composers import Composer
from data.compositions import Composition
from data.results import Result

from forms.user import RegisterForm
from forms.change import ChangeForm, ChangePasswordForm
from forms.quiz import QuizForm, FindCompositionForm
from forms.select_quiz import SelectForm, FindForm, MyQuiz, ResultForm
from forms.test import StartForm, TestForm

from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from data.login_form import LoginForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)


@app.route("/")
def index():
    if current_user.is_authenticated:
        if current_user.id:
            return redirect('/main')
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
    if not current_user.is_authenticated:
        return redirect('/')
    return render_template('lk.html', title='Личный кабинет', user=current_user)


@app.route('/lk/change', methods=['GET', 'POST'])
def change():
    if not current_user.is_authenticated:
        return redirect('/')
    form = ChangeForm()
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == current_user.id).first()
    if form.validate_on_submit():
        user.name = form.name.data
        user.surname = form.surname.data
        db_sess.commit()
        return redirect('/lk')
    return render_template('change.html', title='Изменить данные', form=form, user=user)


@app.route('/lk/change_password', methods=['GET', 'POST'])
def change_password():
    if not current_user.is_authenticated:
        return redirect('/')
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
        return render_template('change_password.html', title='Изменить пароль',
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
    if not current_user.is_authenticated:
        return redirect('/')
    flag = (current_user.position == 'учитель')
    return render_template('main.html', title='Главная страница', flag=flag)


@app.route('/create_quiz', methods=['GET', 'POST'])
def create_quiz():
    if not current_user.is_authenticated:
        return redirect('/')
    if current_user.position == 'ученик':
        return redirect('/main')
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
    if not current_user.is_authenticated:
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
    if not current_user.is_authenticated:
        return redirect('/')
    form = SelectForm()
    db_sess = db_session.create_session()
    compositions2_list = db_sess.query(Composition)
    arr = []
    for i in compositions2_list:
        composer = db_sess.query(Composer).filter(Composer.id == i.composer_id).first()
        arr.append(', '.join([composer.name, i.title]))
    if form.validate_on_submit():
        link = '/quiz/' + str(form.number.data)
        return redirect(link)
    return render_template('select_quiz.html', title='Выбрать викторину', form=form)


@app.route('/select_quiz/quiz_list', methods=['GET', 'POST'])
def quiz_list():
    if not current_user.is_authenticated:
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
        return render_template('quiz_list.html', title='Список викторин', form=form, arr=arr)
    quizzes_list = db_sess.query(Quiz).filter(Quiz.is_private == 0)
    arr = []
    for i in quizzes_list:
        user = db_sess.query(User).filter(User.id == i.user_id).first()
        arr.append(', '.join([str(i.id), i.title, user.name + ' ' + user.surname]))
    return render_template('quiz_list.html', title='Список викторин', form=form, arr=arr)


@app.route('/my_quizzes', methods=['GET', 'POST'])
def my_quizzes():
    if not current_user.is_authenticated:
        return redirect('/')
    if current_user.position == 'ученик':
        return redirect('/main')
    form = SelectForm()
    db_sess = db_session.create_session()
    compositions2_list = db_sess.query(Composition)
    arr = []
    for i in compositions2_list:
        composer = db_sess.query(Composer).filter(Composer.id == i.composer_id).first()
        arr.append(', '.join([composer.name, i.title]))
    if form.validate_on_submit():
        link = '/quiz/' + str(form.number.data)
        return redirect(link)
    return render_template('my_quizzes.html', title='Мои викторины', form=form)


@app.route('/my_quizzes/my_quiz_list', methods=['GET', 'POST'])
def my_quiz_list():
    if not current_user.is_authenticated:
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
    if not current_user.is_authenticated:
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
    link = '/test/' + str(quiz_id)
    link2 = '/results/' + str(quiz_id)
    return render_template('quiz.html', title='Викторина', user=user, quiz=quiz1, private=private, flag=flag,
                           link=link, link2=link2)


@app.route('/quiz/list_compositions', methods=['GET', 'POST'])
def list_compositions():
    if not current_user.is_authenticated:
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
        return render_template('compositions_list2.html', title='Список произведений', form=form, arr=arr)
    composition_list = db_sess.query(Composition)
    arr = []
    for i in composition_list:
        composer = db_sess.query(Composer).filter(Composer.id == i.composer_id).first()
        arr.append(', '.join([str(i.id), composer.name, i.title]))
    return render_template('compositions_list2.html', title="Список произведений", form=form, arr=arr)


@app.route('/test/music/<int:result_id>/<int:composition_id>', methods=["POST", "GET"])
def music(result_id, composition_id):
    if not current_user.is_authenticated:
        return redirect('/')
    form = TestForm()
    db_sess = db_session.create_session()
    result = db_sess.query(Result).filter(Result.id == result_id).first()
    delta_time = datetime.timedelta(
        minutes=db_sess.query(Quiz).filter(Quiz.id == result.quiz_id).first().time_limit)
    time = result.taking_date + delta_time
    quiz = db_sess.query(Quiz).filter(Quiz.id == result.quiz_id).first().content.split(';')
    question_number = quiz.index(str(composition_id))
    next_number = (question_number + 1) % len(quiz)
    next_link = quiz[next_number]
    previous_number = (question_number + len(quiz) - 1) % len(quiz)
    previous_link = quiz[previous_number]
    song = 'music/' + str(composition_id) + '.mp3'
    arr = result.student_answers.split(';')
    link = '/finish/' + str(result.id)
    if datetime.datetime.now() > time:
        result.is_finished = True
        db_sess.commit()
        return render_template('music.html', song=song, next=next_link, previous=previous_link, form=form,
                               composer_answer=arr[question_number].split(', ')[0],
                               composition_answer=arr[question_number].split(', ')[1], link=link,
                               message2='Время вышло. Ответы больше не принимаются. '
                                        'Завершите тест, чтобы подсчитать результаты',
                               title='Тест')
    if form.validate_on_submit() and not result.is_finished:
        arr[question_number] = ', '.join([form.composer.data, form.composition.data])
        result.student_answers = ';'.join(arr)
        db_sess.commit()
        return render_template('music.html', song=song, next=next_link, previous=previous_link, form=form,
                               composer_answer=arr[question_number].split(', ')[0],
                               composition_answer=arr[question_number].split(', ')[1], link=link,
                               message2=f'Тест завершиться в {time}', title='Тест')
    return render_template('music.html', song=song, next=next_link, previous=previous_link, form=form,
                           composer_answer=arr[question_number].split(', ')[0],
                           composition_answer=arr[question_number].split(', ')[1], link=link,
                           message2=f'Тест завершиться в {time}', title='Тест')


@app.route('/finish/<int:result_id>', methods=["POST", "GET"])
def finish(result_id):
    if not current_user.is_authenticated:
        return redirect('/')
    form = StartForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        result = db_sess.query(Result).filter(Result.id == result_id).first()
        student_answers = result.student_answers.split(';')
        right_answers = result.right_answers.split(';')
        scores = result.scores.split(';')
        for i in range(len(student_answers)):
            scores[i] = '0'
            composer = student_answers[i].split(', ')[0]
            composition = student_answers[i].split(', ')[1]
            right_composer = right_answers[i].split(', ')[0]
            right_composition = right_answers[i].split(', ')[1]
            if composer.capitalize() == right_composer.capitalize():
                scores[i] = str(int(scores[i]) + 1)
            if composition.capitalize() == right_composition.capitalize():
                scores[i] = str(int(scores[i]) + 1)
        total_score = 0
        for i in scores:
            total_score += int(i)
        result.scores = ';'.join(scores)
        result.total_score = total_score
        result.is_finished = True
        db_sess.commit()
        link = '/result/' + str(result_id)
        return redirect(link)
    return render_template('finish.html', title='Тест', form=form)


@app.route('/result/<result_id>')
def result(result_id):
    if not current_user.is_authenticated:
        return redirect('/')
    db_sess = db_session.create_session()
    final_result = db_sess.query(Result).filter(Result.id == result_id).first()
    total_score = final_result.total_score
    student_answers = final_result.student_answers.split(';')
    right_answers = final_result.right_answers.split(';')
    scores = final_result.scores.split(';')
    quiz_id = final_result.quiz_id
    user = db_sess.query(User).filter(User.id == final_result.user_id).first()
    name = user.name + ' ' + user.surname
    quiz = db_sess.query(Quiz).filter(Quiz.id == final_result.quiz_id).first()
    arr = []
    for i in range(len(student_answers)):
        arr.append(f'{student_answers[i]} - {right_answers[i]}, {scores[i]}')
    if current_user.id not in [user.id, quiz.user_id]:
        return redirect('/main')
    return render_template('result.html', arr=arr, total_score=total_score, title='Результат',
                           quiz_id=quiz_id, name=name)


@app.route('/results/<quiz_id>', methods=['GET', 'POST'])
def results(quiz_id):
    if not current_user.is_authenticated:
        return redirect('/')
    if current_user.position == 'ученик':
        return redirect('/main')
    form = ResultForm()
    db_sess = db_session.create_session()
    quiz2 = db_sess.query(Quiz).filter(Quiz.id == quiz_id).first()
    if current_user.id != quiz2.user_id:
        return redirect('/main')
    results2 = db_sess.query(Result).filter(Result.quiz_id == quiz_id)
    arr = []
    for i in results2:
        user = db_sess.query(User).filter(User.id == i.user_id).first()
        arr.append(f'{i.id}, {user.name} {user.surname}, {i.total_score}')
    if form.validate_on_submit():
        link = '/result/' + str(form.find_result.data)
        return redirect(link)
    return render_template('results.html', title='Результаты', arr=arr, form=form)


@app.route('/test/<quiz_id>', methods=['GET', 'POST'])
def test(quiz_id):
    if not current_user.is_authenticated:
        return redirect('/')
    form = StartForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        quiz = db_sess.query(Quiz).filter(Quiz.id == quiz_id).first().content.split(';')
        result = Result()
        result.user_id = current_user.id
        result.quiz_id = quiz_id
        arr = []
        for i in quiz:
            composition = db_sess.query(Composition).filter(Composition.id == i).first()
            title = composition.title
            composer = db_sess.query(Composer).filter(Composer.id == composition.composer_id).first().name
            arr.append(composer + ', ' + title)
        result.right_answers = ';'.join(arr)
        result.scores = ';'.join(['0' for i in range(len(quiz))])
        result.student_answers = ';'.join(['без ответа, без ответа' for i in range(len(quiz))])
        result.total_score = 0
        result.taking_date = datetime.datetime.now()
        db_sess.add(result)
        db_sess.commit()
        link = 'music/' + str(result.id) + '/' + quiz[0]
        return redirect(link)
    return render_template('test.html', title='Тест', form=form)


if __name__ == '__main__':
    db_session.global_init("db/music_db.sqlite")
    session = db_session.create_session()

    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
