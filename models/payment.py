from odoo import models, fields, api
from odoo.exceptions import ValidationError

class RealEstatePayment(models.Model):
    _name = 'real.estate.payment'
    _description = 'دفعة عقارية'

    contract_id = fields.Many2one('real.estate.contract', string="العقد", required=True)
    property_id = fields.Many2one(
    related='contract_id.property_id',
    string="العقار",
    store=True,
    readonly=True
)
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
    payment_number = fields.Char(string="رقم الدفعة", required=True)
    electronic_invoice_id = fields.Many2one('account.move', string="فاتورة إلكترونية")

    @api.constrains('amount')
    def _check_amount(self):
        for record in self:
            if record.amount <= 0:
                raise ValidationError("يجب أن يكون المبلغ أكبر من صفر.")

    @api.constrains('payment_date', 'due_date')
    def _check_payment_date(self):
        for record in self:
            if record.payment_date and record.due_date and record.payment_date < record.due_date:
                raise ValidationError("تاريخ السداد لا يمكن أن يكون قبل تاريخ الاستحقاق.")

    @api.onchange('contract_id')
    def _onchange_contract_id(self):
        if self.contract_id and hasattr(self.contract_id, 'id'):
            # مثال على إجراء آمن باستخدام contract_id
            self.notes = f"مرتبطة بعقد رقم: {self.contract_id.name or self.contract_id.id}"
        else:
            self.notes = "⚠️ لا يوجد عقد محدد"

