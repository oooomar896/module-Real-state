from odoo import models, fields

class RealEstatePayment(models.Model):
    _name = 'real.estate.payment'
    _description = 'دفعة عقارية'

    contract_id = fields.Many2one('real.estate.contract', string="العقد", required=True)
    due_date = fields.Date(string="تاريخ الاستحقاق", required=True)
    amount = fields.Float(string="المبلغ", required=True)
    paid = fields.Boolean(string="تم السداد", default=False)
    payment_date = fields.Date(string="تاريخ السداد")
    payment_method = fields.Selection([
        ('cash', 'نقدي'),
        ('bank', 'تحويل بنكي'),
        ('cheque', 'شيك'),
        ('electronic', 'إلكتروني'),
    ], string="طريقة الدفع")
    invoice_id = fields.Many2one('account.move', string="الفاتورة الإلكترونية")
    notes = fields.Char(string="ملاحظات")
    attachment_ids = fields.Many2many(
        'ir.attachment',
        'payment_attachment_rel',
        'payment_id', 'attachment_id',
        string="مرفقات الدفعة"
    )
    active = fields.Boolean(string="نشط", default=True)
