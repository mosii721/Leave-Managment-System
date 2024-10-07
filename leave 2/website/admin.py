from flask import Blueprint,render_template,request,flash,redirect,url_for,jsonify,current_app
from .models import Admin,Employee,Leave,Department,Leaveapplication,Leavebalance
from werkzeug.security import generate_password_hash
from flask_login import login_required,current_user
from . import db,mail
from flask_mail import Message


admin = Blueprint('admin',__name__)

@admin.route('/home')
@login_required
def dashboard():
    employee_count = Employee.query.count()
    department_count = Department.query.count()
    leave_count = Leave.query.count()
    leaveapplications = Leaveapplication.query.all()
    approved_count = Leaveapplication.query.filter_by(status='Approved').count()
    declined_count = Leaveapplication.query.filter_by(status='Declined').count()
    pending_count = Leaveapplication.query.filter_by(status='Pending').count()
    return render_template('Dashboard.html',user = current_user, leaveapplications= leaveapplications, declined_count= declined_count,pending_count= pending_count, approved_count= approved_count,leave_count = leave_count,department_count = department_count,employee_count = employee_count)

@admin.route('/department')
@login_required
def department():
    departments = Department.query.all()
    return render_template('department.html',user = current_user,departments=departments)

@admin.route('/employee')
@login_required
def employee():
    employees = Employee.query.all()
    return render_template('employee.html',employees=employees,user = current_user)

@admin.route('/leave')
@login_required
def leave():
    leaves = Leave.query.all()
    return render_template('leave.html',user = current_user,leaves=leaves)

@admin.route('/addleavetype',methods=['GET','POST'])
@login_required
def addleavetype():
    if request.method == 'POST':
        leavetype = request.form.get('leavetype')
        description = request.form.get('description')
        leavedays = request.form.get('leavedays')

        if len(description) < 5:
            flash('Description should be longer than 5 words',category='error')
        else:
            new_leave = Leave(leavetype=leavetype, description=description,leavedays=leavedays)
            db.session.add(new_leave)
            db.session.commit()
            flash('Leave added', category='success')
            return redirect(url_for('admin.leave'))

    return render_template('addleavetypes.html',user = current_user)


@admin.route('/adddepartment',methods=['GET','POST'])
@login_required
def adddepartment():
    if request.method == 'POST':
        departmentname= request.form.get('departmentname')
        shortform = request.form.get('shortform')
        code = request.form.get('code')

        if len(shortform) > 30:
            flash('shortform is too long',category='error')
        else:
            new_department = Department(departmentname=departmentname, shortform=shortform, code=code)
            db.session.add(new_department)
            db.session.commit()
            flash('Department added', category='success')
            return redirect(url_for('admin.department'))
    return render_template('adddepartment.html',user = current_user)

@admin.route('/approved')
@login_required
def approved():
    
    approved_leaves = Leaveapplication.query.filter_by(status='Approved').all()
    
    return render_template('approved.html',approved_leaves=approved_leaves,user = current_user)

@admin.route('/declined')
@login_required
def declined():
    declined_leaves = Leaveapplication.query.filter_by(status='Declined').all()
    return render_template('declined.html',declined_leaves=declined_leaves,user = current_user)

@admin.route('/pending')
@login_required
def pending():
    pending_leaves = Leaveapplication.query.filter_by(status='Pending').all()
    return render_template('pending.html',pending_leaves=pending_leaves,user = current_user)

@admin.route('/admin/leave_action/<int:leave_id>/<string:action>', methods=['POST'])
def leave_action(leave_id, action):
    leave_application = Leaveapplication.query.get(leave_id)
    
    if action == 'approve':
        leave_application.status = 'Approved'
            
        leavebalance = Leavebalance.query.filter_by(employee_id=leave_application.employee_id, leave_id=leave_application.leave_id).first()

        if leavebalance:
            remaining_days = leavebalance.remaining_days - leave_application.leavedays
            leavebalance.remaining_days = remaining_days
            db.session.commit()
    elif action == 'decline':
        leave_application.status = 'Declined'
        
    
    db.session.commit()
    flash(f'Leave application {action}d successfully!', category='success')

    if leave_application :
        employee = Employee.query.get(leave_application.employee_id)

        recipient = employee.email

        send_email(recipient)
    return redirect(url_for('admin.pending'))


@admin.route('/leavehistory')
@login_required
def leavehistory():
    leaveapplications = Leaveapplication.query.all()
    return render_template('leavehistory.html',leaveapplications=leaveapplications,user = current_user)

@admin.route('/manageadmin')
@login_required
def manageadmin():
    admins = Admin.query.all() # query to get all admins
    return render_template('manageadmin.html',admins=admins,user = current_user)

@admin.route('/addnewemployee',methods=['GET','POST'])
@login_required
def addnewemployee():
    departments = Department.query.all()
    if request.method == 'POST':
        employeeid = request.form.get('employeeid')
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        email = request.form.get('email')
        department_id = request.form.get('department')
        gender = request.form.get('gender')
        address = request.form.get('address')
        contact = request.form.get('contact')
        birth = request.form.get('birth')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        department = Department.query.get(department_id)

        user = Employee.query.filter_by(employeeid=employeeid).first()
        if user:
            flash('Employee already exists',category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(firstname) < 2:
            flash('Firstname must be greater than 1 character.', category='error')
        elif len(lastname) < 2:
            flash('Lastname must be greater than 1 character.', category='error')
        elif len(address) < 4:
            flash('address must be greater than 3 character.', category='error')
        elif len(contact) < 10:
            flash('missing contact numbers.', category='error')
        elif len(employeeid) < 6 :
            flash('admin id is incomplete should be six characters', category='error')
        elif len(employeeid) > 6 :
            flash('admin id is too large should be six characters', category='error')
        elif len(password1) < 7:
            flash('Password must be greater than 6 characters.', category='error')
        elif password1 != password2:
            flash('Passwords do not match.', category='error')
        else:
            new_user1 = Employee(email=email, department=department.departmentname, department_id=department_id,gender=gender,address=address,birth=birth,firstname=firstname, lastname=lastname,contact=contact,employeeid=employeeid,password=generate_password_hash(password1, method='pbkdf2:sha256'))
            db.session.add(new_user1)
            db.session.commit()
            flash('Employee added', category='success')
            return redirect(url_for('admin.employee'))
        
    return render_template('addnewemployee.html',user = current_user, departments=departments)

@admin.route('/addemployeeleavedays',methods=['GET','POST'])
def addemployeeleavedays():
    employee = Employee.query.all()
    leave = Leave.query.all()
    if request.method == 'POST':
        employee_id = request.form.get('employee_id')
        leave_id =  request.form.get('leave_id')
        leavedays = request.form.get('leavedays')

        leave = Leave.query.get(leave_id)
        leavebalance = Leavebalance.query.filter_by(employee_id=employee_id, leave_id=leave_id).first()
        if leavebalance:
            flash('Leave balance for this employee and leave type already exists.',category='error')
        else:
            new_balance = Leavebalance(
                employee_id=employee_id,
                leave_id=leave_id,
                remaining_days=leavedays
            )
            db.session.add(new_balance)
            db.session.commit()
            flash('Employee Leave days added', category='success')
            
        
    return render_template('addemployeeleavedays.html',employee=employee,leave=leave)

@admin.route('/addadmin',methods=['GET','POST'])
@login_required
def addadmin():
    if request.method == 'POST':
        adminid = request.form.get('adminid')
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        email = request.form.get('email')
        contact = request.form.get('contact')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = Admin.query.filter_by(email=email).first()
       
        if user:
            flash('Admin already exists',category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(firstname) < 2:
            flash('Firstname must be greater than 1 character.', category='error')
        elif len(lastname) < 2:
            flash('Lastname must be greater than 1 character.', category='error')
        elif len(contact) < 10:
            flash('missing contact numbers.', category='error')
        elif len(adminid) < 6 :
            flash('admin id is incomplete should be six characters', category='error')
        elif len(adminid) > 6 :
            flash('admin id is too large should be six characters', category='error')
        elif len(password1) < 7:
            flash('Password must be greater than 6 characters.', category='error')
        elif password1 != password2:
            flash('Passwords do not match.', category='error')
        else:
            new_user = Admin(email=email,firstname=firstname, lastname=lastname,contact=contact,adminid=adminid,password=generate_password_hash(password1, method='pbkdf2:sha256'))
            db.session.add(new_user)
            db.session.commit()
            flash('Admin added', category='success')
            return redirect(url_for('admin.manageadmin'))
    return render_template('addadmin.html',user = current_user)

@admin.route('/delete-item', methods=['POST'])
def delete_item():
    data = request.get_json()
    model_name = data.get('model')
    item_id = data.get('itemId')
    
    # Map model names to actual model classes
    model_map = {
        'admin': Admin,
        'employee': Employee,
        'department': Department,
        'leave': Leave,
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


@admin.route('/employee_details/<int:employee_id>')
def employee_details(employee_id):
    # Assuming you're using SQLAlchemy to query the database
    employee = Employee.query.get(employee_id)
    
    if employee:
        return render_template('employee_details.html', employee=employee)
    

@admin.route('/edit_employee/<int:employee_id>', methods=['GET', 'POST'])
def edit_employee(employee_id):
    employee = Employee.query.get(employee_id)
    if request.method == 'POST':
        # Update employee details only if the form fields are filled out
        if request.form.get('firstname'): # .strip to allow users to leave blank and it does not erase existing data
            employee.firstname = request.form.get('firstname').strip()
        if request.form.get('lastname').strip():
            employee.lastname = request.form.get('lastname')
        if request.form.get('email').strip():
            employee.email = request.form.get('email')
        if request.form.get('department').strip():
            employee.department = request.form.get('department')
        if request.form.get('employeeid').strip():
            employee.employeeid = request.form.get('employeeid')
        if request.form.get('address').strip():
            employee.address = request.form.get('address')
        if request.form.get('contact').strip():
            employee.contact = request.form.get('contact')

        password = request.form.get('password')
        if password and password.strip():
            employee.password = generate_password_hash(password.strip())

        # Commit the changes to the database
        db.session.commit()

        # Redirect back to the employee details page
        return redirect(url_for('admin.employee_details', employee_id=employee.id))
    
    if employee:
        return render_template('edit_employee.html', employee=employee)
    
    
@admin.route('/admin_details/<int:admin_id>')
def admin_details(admin_id):
    # Assuming you're using SQLAlchemy to query the database
    admin = Admin.query.get(admin_id)
    
    if admin:
        return render_template('admin_details.html', admin=admin)

@admin.route('/edit_admin/<int:admin_id>', methods=['GET', 'POST'])
def edit_admin(admin_id):
    admin = Admin.query.get(admin_id)
    if request.method == 'POST':
        # Update employee details only if the form fields are filled out
        if request.form.get('firstname'): # .strip to allow users to leave blank and it does not erase existing data
            admin.firstname = request.form.get('firstname').strip()
        if request.form.get('lastname').strip():
            admin.lastname = request.form.get('lastname')
        if request.form.get('email').strip():
            admin.email = request.form.get('email')
        if request.form.get('adminid').strip():
            admin.adminid = request.form.get('adminid')
        if request.form.get('contact').strip():
            admin.contact = request.form.get('contact')

        password = request.form.get('password')
        if password and password.strip():
            admin.password = generate_password_hash(password.strip())

        # Commit the changes to the database
        db.session.commit()

        # Redirect back to the employee details page
        return redirect(url_for('admin.admin_details', admin_id=admin.id))
    
    if admin:
        return render_template('edit_admin.html', admin=admin)
    
@admin.route('/pendingseedetails/<int:leaveapplication_id>')
@login_required
def pendingseedetails(leaveapplication_id):
        
        leaveapplication = Leaveapplication.query.get(leaveapplication_id)
    
        if leaveapplication:
            return render_template('pendingseedetails.html', leaveapplication=leaveapplication)
        else:
            return render_template('pendingseedetails.html')

@admin.route('/approvedseedetails/<int:leaveapplication_id>')
@login_required
def approvedseedetails(leaveapplication_id):
        
        leaveapplication = Leaveapplication.query.get(leaveapplication_id)
    
        if leaveapplication:
            return render_template('approvedseedetails.html', leaveapplication=leaveapplication)
        else:
            return render_template('approvedseedetails.html')

@admin.route('/declinedseedetails/<int:leaveapplication_id>')
@login_required
def declinedseedetails(leaveapplication_id):
        
        leaveapplication = Leaveapplication.query.get(leaveapplication_id)
    
        if leaveapplication:
            return render_template('declinedseedetails.html', leaveapplication=leaveapplication)
        else:
            return render_template('declinedseedetails.html')

@admin.route('/leave_details/<int:leaveapplication_id>')
def leave_details(leaveapplication_id):
    # Assuming you're using SQLAlchemy to query the database
    leaveapplication = Leaveapplication.query.get(leaveapplication_id)
    
    if leaveapplication:
        return render_template('leave_details.html', leaveapplication=leaveapplication)
    else:
            return render_template('leave_details.html')

def send_email(recipient):
    try:
        # also have to import message 
        msg = Message(
            'Your Leave Application has been reviewed',
            recipients=[recipient],  # List of recipients (even if its just one)
            sender=current_app.config['MAIL_DEFAULT_SENDER']# i have imported current_app above
        )
        msg.body = 'Your Leave application has been reviewed.'
        mail.send(msg)
        print(f"Email sent to {recipient}")
    except Exception as e:
        print(f"Failed to send email: {e}")

