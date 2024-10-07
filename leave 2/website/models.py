from . import db
from datetime import datetime
from flask_login import UserMixin

from sqlalchemy import Enum



class Admin(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    adminid = db.Column(db.String(6),unique=True)
    firstname = db.Column(db.String(150))
    lastname = db.Column(db.String(150))
    email = db.Column(db.String(150),unique=True)
    contact = db.Column(db.Integer)
    password = db.Column(db.String(512))
    status = db.Column(db.String(10))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    departments = db.relationship('Department') 
    employees = db.relationship('Employee') 

class Employee(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    employeeid = db.Column(db.String(6),unique=True)
    firstname = db.Column(db.String(150))
    lastname = db.Column(db.String(150))
    email = db.Column(db.String(150),unique=True)
    contact = db.Column(db.Integer)
    password = db.Column(db.String(512))
    department = db.Column(db.String(150))
    gender = db.Column(db.String(15))
    address = db.Column(db.String(150))
    birth = db.Column(db.String(10))                     ##########################
    status = db.Column(db.String(10)) 
    leaveapplications = db.relationship('Leaveapplication')
    leavebalances = db.relationship('Leavebalance', backref='employee')
    department_id = db.Column(db.Integer,db.ForeignKey('department.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    admin_id = db.Column(db.Integer,db.ForeignKey('admin.id'))

    def get_id(self):
        return self.id
class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    departmentname = db.Column(db.String(200))
    shortform = db.Column(db.String(30))
    code = db.Column(db.String(150))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    admin_id = db.Column(db.Integer,db.ForeignKey('admin.id')) # used to establish relationship
    employees = db.relationship('Employee')
    

class Leave(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    leavetype = db.Column(db.String(150))
    description = db.Column(db.String(200))
    leavedays = db.Column(db.Integer)
    leaveapplications = db.relationship('Leaveapplication')
    leavebalances = db.relationship('Leavebalance', backref='leave')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


    
class Leaveapplication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sdate =  db.Column(db.Date)
    edate =  db.Column(db.Date)
    leave = db.Column(db.String(150))
    descriptions = db.Column(db.String(500))
    leavedays = db.Column(db.Integer)
    employee_id = db.Column(db.Integer,db.ForeignKey('employee.id'))
    employee = db.relationship('Employee', backref='leave_applications')
    leave_id = db.Column(db.Integer,db.ForeignKey('leave.id'))
    leaver = db.relationship('Leave', backref='leave_applications')
    status = db.Column(Enum('Pending', 'Approved', 'Declined'), default='Pending', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Leavebalance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    leave_id = db.Column(db.Integer, db.ForeignKey('leave.id'), nullable=False)
    remaining_days = db.Column(db.Integer, nullable=False)  # Track the employee-specific leave balance


