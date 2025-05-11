from odoo import models, fields

class RealEstateProperty(models.Model):
    _name = 'real.estate.property'
    _description = 'عقار'

    name = fields.Char(string="اسم العقار", required=True)
    code = fields.Char(string="كود العقار")
    type = fields.Selection([
        ('apartment', 'شقة'),
        ('villa', 'فيلا'),
        ('shop', 'محل'),
        ('land', 'أرض'),
        ('office', 'مكتب'),
        ('warehouse', 'مستودع'),
    ], string="النوع", required=True)
    address = fields.Char(string="العنوان")
    area = fields.Float(string="المساحة (م2)")
    floor = fields.Char(string="الدور")
    building = fields.Char(string="اسم/كود المبنى")
    project = fields.Char(string="اسم المشروع")
    owner_id = fields.Many2one('res.partner', string="المالك")
    state = fields.Selection([
        ('available', 'شاغر'),
        ('rented', 'مؤجر'),
        ('maintenance', 'تحت الصيانة'),
        ('sold', 'مباع')
    ], string="الحالة", default='available')
    description = fields.Text(string="ملاحظات")
    contract_ids = fields.One2many('real.estate.contract', 'property_id', string="العقود")
    expense_ids = fields.One2many('real.estate.expense', 'property_id', string="المصروفات")
    maintenance_ids = fields.One2many('real.estate.maintenance', 'property_id', string="طلبات الصيانة")
    attachment_ids = fields.Many2many(
        'ir.attachment',
        'property_attachment_rel',
        'property_id', 'attachment_id',
        string="المرفقات"
    )
    image = fields.Binary(string="صورة رئيسية")
    latitude = fields.Float(string="خط العرض")
    longitude = fields.Float(string="خط الطول")
    active = fields.Boolean(string="نشط", default=True)
