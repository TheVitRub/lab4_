from flask import Flask, render_template, request, redirect, flash, send_from_directory, url_for
import os
from werkzeug.utils import secure_filename
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from astronaut_selection_form import *
import jsonlines


app = Flask(__name__, template_folder='templates')
app.config['UPLOAD_FOLDER'] = 'static/uploads'


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/list_prof/<list>')
def list_prof(list):
    professions = [
        "инженер-исследователь", "пилот", "строитель", "экзобиолог", "врач",
        "инженер по терраформированию", "климатолог", "специалист по радиационной защите",
        "астрогеолог", "гляциолог"
    ]
    if list == 'ol':
        return render_template('list_prof.html', professions=professions, list_type='ol')
    elif list == 'ul':
        return render_template('list_prof.html', professions=professions, list_type='ul')
    else:
        return "Передан неверный параметр. Пожалуйста, используйте 'ol' или 'ul'."


@app.route('/distribution')
def distribution():
    crew = []
    with jsonlines.open('static/members/members.jsonl') as reader:
        for member in reader:
            crew.append(member)
    return render_template('distribution.html', crew=crew)


@app.route('/member/<int:number>')
def member(number):
    crew = []
    with jsonlines.open('static/members/members.jsonl') as reader:
        for member in reader:
            crew.append(member)

    if 1 <= number <= len(crew):
        member = crew[number - 1]
        return render_template('member.html', member=member)
    else:
        return "Invalid member number."


@app.route('/member/random')
def random_member():
    import random
    crew = []
    with jsonlines.open('static/members/members.jsonl') as reader:
        for member in reader:
            crew.append(member)

    member = random.choice(crew)
    return render_template('member.html', member=member)


@app.route('/room/<sex>/<int:age>')
def room(sex, age):
    if sex == 'male':
        color = 'blue'
        emblem = 'emblem_male_child.png' if age < 21 else 'emblem_male_adult.png'
    elif sex == 'female':
        color = 'pink'
        emblem = 'emblem_female_child.png' if age < 21 else 'emblem_female_adult.png'
    else:
        return "Неверный параметр пола. Пожалуйста, используйте 'male' или 'female'."
    return render_template('room.html', color=color, emblem=emblem)


@app.route('/astronaut_selection', methods=['GET', 'POST'])
def astronaut_selection():
    form = AstronautSelectionForm()
    message = None

    if form.validate_on_submit():
        last_name = form.last_name.data
        first_name = form.first_name.data
        email = form.email.data
        education = form.education.data
        profession = form.profession.data
        gender = form.gender.data
        motivation = form.motivation.data
        stay_on_mars = form.stay_on_mars.data

        body = f"Фамилия: {last_name}\n"
        body += f"Имя: {first_name}\n"
        body += f"Email: {email}\n"
        body += f"Образование: {education}\n"
        body += f"Выбор основной профессии: {profession}\n"
        body += f"Пол: {gender}\n"
        body += f"Мотивация: {motivation}\n"
        body += f"Готовы ли остаться на Марсе?: {stay_on_mars}\n"

        msg = MIMEMultipart()
        msg['From'] = 'почта отправителя'
        msg['To'] = email
        msg['Subject'] = 'Резюме астронавта'

        msg.attach(MIMEText(body, 'plain'))

        filename = secure_filename(form.photo.data.filename)
        attachment = open(os.path.join(app.config['UPLOAD_FOLDER'], filename), "rb")
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', "attachment; filename= %s" % filename)
        msg.attach(part)

        try:
            server = smtplib.SMTP('smtp.mail.ru', 587)
            server.starttls()
            server.login('почта отправителя', 'пароль приложения')
            text = msg.as_string()
            server.sendmail('почта отправителя', email, text)
            server.quit()
            message = 'Резюме успешно отправлено'
            form = AstronautSelectionForm()
        except Exception as e:
            message = f'Не удалось отправить резюме, код ошибки: {e}'

    return render_template('astronaut_selection.html', form=form, message=message)


@app.route('/results/<nickname>/<int:level>/<float:rating>')
def results(nickname, level, rating):
    return render_template('results.html', nickname=nickname, level=level, rating=rating)


@app.route('/photo/<nickname>', methods=['GET', 'POST'])
def photo_upload(nickname):
    if request.method == 'POST':
        if 'photo' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['photo']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return render_template('photo_upload.html', nickname=nickname, filename=filename)
    return render_template('photo_upload.html', nickname=nickname, filename=None)


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/gallery')
def gallery():
    images = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('gallery.html', images=images)


@app.route('/upload_image', methods=['POST'])
def upload_image():
    if 'image' in request.files:
        image = request.files['image']
        if image.filename != '':
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return redirect(url_for('gallery'))


app.secret_key = 'super_secret_key'

if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
