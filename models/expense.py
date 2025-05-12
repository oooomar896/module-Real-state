from odoo import models, fields

class RealEstateExpense(models.Model):
    _name = 'real.estate.expense'
    _description = 'مصروف عقاري'

    property_id = fields.Many2one('real.estate.property', string="العقار", required=True)
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
    invoice_id = fields.Many2one('account.move', string="فاتورة المصروف")
    attachment_ids = fields.Many2many(
        'ir.attachment',
        'expense_attachment_rel',
        'expense_id', 'attachment_id',
        string="مرفقات المصروف"
    )
    notes = fields.Text(string="ملاحظات")
    active = fields.Boolean(string="نشط", default=True)
    expense_number = fields.Char(string="رقم المصروف", required=True)
    expense_invoice_id = fields.Many2one('account.move', string="فاتورة المصروف")