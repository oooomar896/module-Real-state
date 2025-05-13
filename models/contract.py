from odoo import models, fields, api
from datetime import date, timedelta

class RealEstateContract(models.Model):
    _name = 'real.estate.contract'
    _description = 'عقد عقاري'

    name = fields.Char(string="رقم العقد", required=True)
    property_id = fields.Many2one('real.estate.property', string="العقار", required=True)
    unit_id = fields.Many2one('real.estate.unit', string="الوحدة (شقة/مكتب)")
    tenant_id = fields.Many2one('res.partner', string="المستأجر/المشتري", required=True)
    payment_ids = fields.One2many('real.estate.payment', 'contract_id', string="الدفعات")
    contract_type = fields.Selection([
        ('rent_residential', 'إيجار سكني'),
        ('rent_commercial', 'إيجار تجاري'),
        ('sale', 'بيع')
    ], string="نوع العقد", required=True)
    start_date = fields.Date(string="تاريخ البداية", required=True)
    end_date = fields.Date(string="تاريخ النهاية")
    amount = fields.Float(string="القيمة الإجمالية", required=True)
    payment_term = fields.Selection([
        ('monthly', 'شهري'),
        ('quarterly', 'ربع سنوي'),
        ('halfyearly', 'نصف سنوي'),
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
    alert_message = fields.Html(string="تنبيه", compute="_compute_alert_message", store=False)

    @api.depends('end_date')
    def _compute_alert_message(self):
        today = date.today()
        for rec in self:
            rec.alert_message = ""
            if rec.end_date:
                if rec.end_date < today:
                    rec.alert_message = (
                        f'<div style="color:#fff; background:#d9534f; padding:8px; border-radius:4px; margin-bottom:8px;">'
                        f'⚠️ هذا العقد منتهي منذ {rec.end_date.strftime("%Y-%m-%d")}!</div>'
                    )
                elif today <= rec.end_date <= today + timedelta(days=30):
                    rec.alert_message = (
                        f'<div style="color:#856404; background:#fff3cd; padding:8px; border-radius:4px; margin-bottom:8px;">'
                        f'⏰ هذا العقد سينتهي خلال أقل من شهر (تاريخ الانتهاء: {rec.end_date.strftime("%Y-%m-%d")})!</div>'
                    )

    @api.onchange('property_id', 'contract_type')
    def _onchange_property_unit(self):
        domain = []
        if self.property_id and self.contract_type:
            if self.contract_type == 'rent_residential':
                domain = [('property_id', '=', self.property_id.id), ('unit_type', '=', 'apartment')]
            elif self.contract_type == 'rent_commercial':
                domain = [('property_id', '=', self.property_id.id), ('unit_type', '=', 'office')]
        return {'domain': {'unit_id': domain}}
