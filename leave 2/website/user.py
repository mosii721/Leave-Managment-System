from flask import Blueprint,render_template,request,flash,redirect,url_for,current_app
from flask_login import login_required,current_user
from .models import Leave,Leaveapplication,Employee,Leavebalance,Admin
from werkzeug.security import generate_password_hash
from flask_mail import Message
from datetime import datetime

from . import db,mail

user = Blueprint('user',__name__)

@user.route('/userhome',methods=['GET','POST'])
@login_required
def applyleave():
    
    leaveapplications = Leaveapplication.query.all()
    employee = Employee.query.get(current_user.id)
    applications = Leaveapplication.query.join(Employee).filter(Employee.id == current_user.id).all()
    leaves = Leave.query.all()
    
    leavedays = None # because it is not associated with any value in the form

    if request.method == 'POST':
        sdate = request.form.get('sdate')
        edate = request.form.get('edate')
        leave_id = request.form.get('leave') # fetching the id value here
        descriptions = request.form.get('descriptions')

        leavebalance = Leavebalance.query.filter_by(employee_id=current_user.id,leave_id=leave_id).first()
        stdate = datetime.strptime(sdate, '%Y-%m-%d')
        endate = datetime.strptime(edate, '%Y-%m-%d')

        if leavebalance is None:
            flash("Leave balance not found for this leave type", category="error")
            return redirect(url_for('user.applyleave', leave_id=leave_id))
        # Calculate the number of leave days
        leavedays = (endate - stdate).days + 1  # Add 1 to include both start and end days

        leave = Leave.query.get(leave_id) # Getting all leave ids because we decided we are calling the ids back in the html

        
        if len(descriptions) < 10:
            flash('Too short', category='error')
        elif leavedays > leavebalance.remaining_days:
                flash(f"You only have {leavebalance.remaining_days} days available for that leave type", category='error')  
        else:
            new_app = Leaveapplication(sdate = sdate,edate = edate,leave=leave.leavetype ,descriptions = descriptions,leavedays= leavedays, leave_id=leave_id ,employee_id=current_user.id) # added leave_id field and leave= leave.type went with leave type instead of id 
            db.session.add(new_app)
            db.session.commit()
            flash(f'Leave application sent,You applied a maximum of { leavedays } leave days', category='success')
            #get admin emails that are available
            admin_emails = [admin.email for admin in Admin.query.all()]

            # Send email to admins
            send_email(admin_emails)
        
    return render_template('applyleave.html',leavedays=leavedays,leaves = leaves,applications=applications,leaveapplications=leaveapplications,employee=employee,user = current_user)

@user.route('/userdetails/<int:employee_id>')
def userdetails(employee_id):
    leaveapplications = Leaveapplication.query.all()
    # Assuming you're using SQLAlchemy to query the database
    employee = Employee.query.get(employee_id)
    
    if employee:
        return render_template('userdetails.html',leaveapplications=leaveapplications, employee=employee)

@user.route('/userpasswordedit/<int:employee_id>', methods=['GET', 'POST'])
def userpasswordedit(employee_id):
    leaveapplications = Leaveapplication.query.all()
    employee = Employee.query.get(employee_id)
    if request.method == 'POST':
        # Update employee details only if the form fields are filled out

        password = request.form.get('password')
        if password and password.strip():
            employee.password = generate_password_hash(password.strip())

        # Commit the changes to the database
        db.session.commit()
        flash('Pdasswor changed',category='success')

        # Redirect back to the employee details page
        return redirect(url_for('user.userpasswordedit', employee_id=employee.id))
    
    if employee:
        return render_template('userpasswordedit.html', employee=employee, leaveapplications=leaveapplications, applications=applications)
    
    
@user.route('/userleavehistory')
def userleavehistory():
    # Assuming you're using SQLAlchemy to query the database
    leaveapplications = Leaveapplication.query.filter_by(employee_id = current_user.id).all()
    
    
    return render_template('userleavehistory.html', leaveapplications=leaveapplications,employee= current_user)

@user.route('/userpendingleaves')
def userpendingleaves():
    # Assuming you're using SQLAlchemy to query the database
    employee = Employee.query.get(current_user.id)
    leaveapplications = Leaveapplication.query.filter_by(employee_id = current_user.id,status='Pending').all()
    
    if leaveapplications:
        return render_template('userpendingleaves.html', leaveapplications=leaveapplications,employee= current_user)
    else:
        return render_template('userpendingleaves.html',employee=employee)

@user.route('/leavedays')
@login_required
def leavedays():
    employee = Employee.query.get(current_user.id)
    leavebalances = Leavebalance.query.filter_by(employee_id=current_user.id).all()

    return render_template('leavedays.html', employee=employee,leavebalances=leavebalances,user = current_user)

@user.route('/delete-item', methods=['POST'])
def delete_item():
    data = request.get_json()
    model_name = data.get('model')
    item_id = data.get('itemId')
    
    # Map model names to actual model classes
    model_map = {
        'leaveapplication': Leaveapplication
    }
    
    # Get the model class based on the model name
    model = model_map.get(model_name)
    
    
    # Fetch the item from the database
    item = model.query.get(item_id)
    
    
    # Delete the item and commit changes
    db.session.delete(item)
    db.session.commit()
    
    return jsonify({'success': True}), 200

def send_email(recipients):
    try:
        # Ensure recipients is a list
        if not isinstance(recipients, list):
            recipients = [recipients]
        # also have to import message 
        msg = Message(
            'New Leave Application has been sent',
            recipients=recipients,  # List of recipients
            sender=current_app.config['MAIL_DEFAULT_SENDER']# i have imported current_app above
        )
        msg.body = 'A new Leave application has been submitted.'
        mail.send(msg)
        print(f"Email sent to {recipients}")
    except Exception as e:
        print(f"Failed to send email: {e}")

