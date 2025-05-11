from odoo import models, fields

class RealEstateProject(models.Model):
    _name = "real.estate.project"
    _description = "Real Estate Project"

    name = fields.Char(string="اسم المشروع", required=True)
    description = fields.Text(string="وصف المشروع")
    location = fields.Char(string="الموقع")
    property_ids = fields.One2many("real.estate.asset", "project_id", string="العقارات")
