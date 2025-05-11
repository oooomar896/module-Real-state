from odoo import models, fields

class Employee(models.Model):
    _name = 'employee'
    _description = 'Employee'

    name = fields.Char(string="Name", required=True)
    job_title = fields.Char(string="Job Title")
