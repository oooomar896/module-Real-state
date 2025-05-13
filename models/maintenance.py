from odoo import models, fields

class RealEstateMaintenance(models.Model):
    _name = 'real.estate.maintenance'
    _description = 'طلب صيانة عقاري'

    property_id = fields.Many2one('real.estate.property', string="العقار", required=True)
    unit_id = fields.Many2one(
        'real.estate.unit',
        string="الوحدة (شقة/مكتب)",
        domain="[('property_id', '=', property_id)]"
    )
    
    request_date = fields.Date(string="تاريخ الطلب", default=fields.Date.today, required=True)
    description = fields.Text(string="وصف المشكلة", required=True)
    assigned_to = fields.Many2one('res.users', string="الفني المسؤول")
    state = fields.Selection([
        ('new', 'جديد'),
        ('in_progress', 'قيد التنفيذ'),
        ('done', 'منجز'),
        ('cancelled', 'ملغي')
    ], string="حالة الطلب", default='new')
    cost = fields.Float(string="تكلفة الصيانة")
    completion_date = fields.Date(string="تاريخ الإنجاز")
    notes = fields.Text(string="ملاحظات")
    attachment_ids = fields.Many2many(
        'ir.attachment',
        'maintenance_attachment_rel',
        'maintenance_id', 'attachment_id',
        string="مرفقات الصيانة"
    )
    active = fields.Boolean(string="نشط", default=True)
    request_number = fields.Char(string="رقم الطلب", required=True)
