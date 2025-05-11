from odoo import models, fields

class RealEstateOwner(models.Model):
    _name = "real.estate.owner"
    _description = "Real Estate Owner"

    name = fields.Char(string="الاسم الكامل", required=True)
    phone = fields.Char(string="رقم الهاتف")
    email = fields.Char(string="البريد الإلكتروني")
    address = fields.Text(string="العنوان")
    assets_ids = fields.One2many("real.estate.asset", "owner_id", string="العقارات")
