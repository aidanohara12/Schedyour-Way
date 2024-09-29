from flask import Flask, render_template, request, redirect, url_for
from pittapi import course as pitt
from flask_sqlalchemy import SQLAlchemy
import datetime

app = Flask(__name__)
db = SQLAlchemy()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db.init_app(app)

class course_grouping(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(10), nullable=False)
    course_code = db.Column(db.String(10), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    days = db.Column(db.String(10), nullable=False)
    recitation_start_time = db.Column(db.DateTime, nullable=True)
    recitation_end_time = db.Column(db.DateTime, nullable=True)
    recitation_day = db.Column(db.String(10), nullable=True)
    index = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return '%r' % self.course_code

with app.app_context():
    db.create_all()

search_results = []

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        try:
            search_results.clear()
            cur_course_details = pitt.get_course_details(term='2251', subject=request.form['sub'], course=request.form['code'])
            lecture = None;
            num_recitations = -1
            i = 0

            for section in cur_course_details.sections:
                if(section.section_type == "Lecture"):
                    if(num_recitations == 0):
                        hour_mins = lecture.start_time.split('.')
                        start_time = datetime.time(hour=int(hour_mins[0]), minute=int(hour_mins[1]))
                        hour_mins = lecture.end_time.split('.')
                        end_time = datetime.time(hour=int(hour_mins[0]), minute=int(hour_mins[1]))
                        new_course = course_grouping(subject=cur_course_details.course.subject_code, 
                                                        course_code=cur_course_details.course.course_number,
                                                        start_time=start_time, end_time=end_time,
                                                        days=lecture.days, index=i)
                        search_results.append(new_course)
                        i += 1

                    lecture = section.meetings[0]
                    num_recitations = 0
                else:
                    for meeting in section.meetings:
                        hour_mins = lecture.start_time.split('.')
                        start_time = datetime.time(hour=int(hour_mins[0]), minute=int(hour_mins[1]))
                        hour_mins = lecture.end_time.split('.')
                        end_time = datetime.time(hour=int(hour_mins[0]), minute=int(hour_mins[1]))
                        hour_mins = meeting.start_time.split('.')
                        recitation_start_time = datetime.time(hour=int(hour_mins[0]), minute=int(hour_mins[1]))
                        hour_mins = meeting.end_time.split('.')
                        recitation_end_time = datetime.time(hour=int(hour_mins[0]), minute=int(hour_mins[1]))

                        new_course = course_grouping(subject=cur_course_details.course.subject_code, 
                                                    course_code=cur_course_details.course.course_number,
                                                    start_time=start_time, end_time=end_time,
                                                    days=lecture.days, recitation_start_time=recitation_start_time,
                                                    recitation_end_time=recitation_end_time, recitation_day=meeting.days,
                                                    index=i)
                        search_results.append(new_course)
                        i += 1
                        num_recitations += 1

            return render_template('class_search.html', print = search_results)
        except:
            return "There was an issue"

    else:
        return render_template('class_search.html')

@app.route('/add/<int:index>')
def add(index):
    class_to_add = search_results[index]

    try:
        db.session.add(class_to_add)
        db.session.commit()
        return render_template('class_search.html', print = search_results)
    except:
        return "There was an issue"

if __name__ == "__main__":
    app.run(debug=True)