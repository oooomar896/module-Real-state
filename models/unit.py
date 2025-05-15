from odoo import models, fields, api, _

class RealEstateUnit(models.Model):
    _name = 'real.estate.unit'
    _description = 'وحدة عقارية (شقة أو مكتب)'
    property_id = fields.Many2one('real.estate.property', string="العقار", required=True, ondelete='cascade')
    name = fields.Char(string="رقم/اسم الوحدة", required=True)
    unit_type = fields.Selection([
        ('apartment', 'شقة'),
        ('showroom', 'معرض'),
        ('shop', 'محل'),
        ('office', 'مكتب')
    ], string="نوع الوحدة", required=True)
    floor = fields.Char(string="الدور")
    area = fields.Float(string="المساحة (م²)")
    active = fields.Boolean(string="نشط", default=True)
    sequence = fields.Integer(string="الترتيب", default=10)

    # الحقل المطلوب لربط العقود بالوحدة
    contract_ids = fields.One2many('real.estate.contract', 'unit_id', string="العقود")
