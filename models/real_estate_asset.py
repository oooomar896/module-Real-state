from odoo import models, fields

class RealEstateAsset(models.Model):
    _name = "real.estate.asset"
    _description = "Real Estate Asset"

    name = fields.Char(string="اسم العقار", required=True)
    description = fields.Text(string="وصف تفصيلي")
    price = fields.Float(string="السعر")
    area = fields.Float(string="المساحة (م²)")
    location = fields.Char(string="الموقع")
    property_type = fields.Selection([
        ('land', 'أرض'),
        ('apartment', 'شقة'),
        ('villa', 'فيلا'),
        ('shop', 'محل تجاري'),
        ('other', 'أخرى'),
    ], string="نوع العقار", required=True)
    status = fields.Selection([
    ('available', 'متاح'),
    ('sold', 'مباع'),
    ('reserved', 'محجوز'),
    ('rented', 'مؤجر'),  # ← أضف هذا الخيار
], string="حالة العقار", default='available')

    owner_id = fields.Many2one("real.estate.owner", string="المالك")
    project_id = fields.Many2one("real.estate.project", string="المشروع")
    
    rental_contract_ids = fields.One2many("real.estate.rental.contract", "asset_id", string="عقود الإيجار")

    
    image = fields.Image(string="صورة العقار")
