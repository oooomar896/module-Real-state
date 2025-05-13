from odoo import models, fields

class RealEstateExpense(models.Model):
    _name = 'real.estate.expense'
    _description = 'مصروف عقاري'

    expense_number = fields.Char(string="رقم المصروف", required=True)
    property_id = fields.Many2one('real.estate.property', string="العقار", required=True)
    unit_id = fields.Many2one(
        'real.estate.unit',
        string="الوحدة (شقة/مكتب)",
        domain="[('property_id', '=', property_id)]"
    )
    date = fields.Date(string="التاريخ", required=True, default=fields.Date.today)
    description = fields.Char(string="الوصف", required=True)
    amount = fields.Float(string="المبلغ", required=True)
    expense_type = fields.Selection([
        ('maintenance', 'صيانة'),
        ('electricity', 'كهرباء'),
        ('water', 'ماء'),
        ('government', 'رسوم حكومية'),
        ('commission', 'عمولة'),
        ('other', 'أخرى'),
    ], string="نوع المصروف")
    paid = fields.Boolean(string="تم السداد", default=False)
    payment_date = fields.Date(string="تاريخ السداد")
    notes = fields.Text(string="ملاحظات")
    active = fields.Boolean(string="نشط", default=True)

    attachment_ids = fields.Many2many(
        'ir.attachment',
        'real_estate_expense_ir_attachments_rel',
        'expense_id',
        'attachment_id',
        string='المرفقات',
        domain="[('res_model', '=', 'real.estate.expense')]",
        context={'default_res_model': 'real.estate.expense'}
    )
