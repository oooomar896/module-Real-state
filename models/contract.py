from odoo import models, fields

class RealEstateContract(models.Model):
    _name = 'real.estate.contract'
    _description = 'عقد عقاري'

    name = fields.Char(string="رقم العقد", required=True)
    property_id = fields.Many2one('real.estate.property', string="العقار", required=True)
    tenant_id = fields.Many2one('res.partner', string="المستأجر/المشتري", required=True)
    payment_ids = fields.One2many('real.estate.payment', 'contract_id', string="الدفعات")

    contract_type = fields.Selection([
        ('rent', 'إيجار'),
        ('sale', 'بيع')
    ], string="نوع العقد", required=True)
    start_date = fields.Date(string="تاريخ البداية", required=True)
    end_date = fields.Date(string="تاريخ النهاية")
    amount = fields.Float(string="القيمة الإجمالية", required=True)
    payment_term = fields.Selection([
        ('monthly', 'شهري'),
        ('quarterly', 'ربع سنوي'),
        ('yearly', 'سنوي')
    ], string="دورية السداد", default='monthly')
    state = fields.Selection([
        ('draft', 'مسودة'),
        ('active', 'نشط'),
        ('expired', 'منتهي'),
        ('cancelled', 'ملغي')
    ], string="الحالة", default='draft')
    attachment_ids = fields.Many2many(
        'ir.attachment',
        'contract_attachment_rel',
        'contract_id', 'attachment_id',
        string="مرفقات العقد"
    )
    notes = fields.Text(string="ملاحظات")
    active = fields.Boolean(string="نشط", default=True)
