from flask import Blueprint,render_template,request,flash,redirect,url_for
from .models import Admin,Employee
from werkzeug.security import check_password_hash
from . import db
from flask_login import login_user,logout_user,login_required,current_user

auth = Blueprint('auth',__name__)

@auth.route('/',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        firstname = request.form.get('firstname')
        password = request.form.get('password')

        user = Admin.query.filter_by(firstname=firstname).first()
        print(user)
        if user and user.password:
            if check_password_hash(user.password, password):
                user.status = 'active'
                db.session.commit()
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('admin.dashboard'))
            else:
                flash('Incorrect password,try again!',category='error')
        else:
            flash('Username does not exist', category='error')
    return render_template('login.html', user=current_user)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/employeeLogin',methods=['GET','POST'])
def user_login():
    if request.method == 'POST':
        employeeid = request.form.get('employeeid')
        password = request.form.get('password')

        user = Employee.query.filter_by(employeeid=employeeid).first()
        if user and user.password:
            if check_password_hash(user.password, password):
                user.status = 'active'
                db.session.commit()
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('user.applyleave'))
            else:
                flash('Incorrect password,try again!',category='error')
        else:
            flash('employye id does not exist', category='error')
    return render_template('employeelogin.html',user=current_user)





