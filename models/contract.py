from odoo import models, fields, api, _
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
        ('draft', 'قرب على الانتهاء'),
        ('active', 'عقد ساري'),
        ('expired', 'منتهي العقد'),
        ('cancelled', 'ملغي')
    ], string="الحالة", default='draft', tracking=True)
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

    def write(self, vals):
        old_states = {contract.id: contract.state for contract in self}
        res = super(RealEstateContract, self).write(vals)

        for contract in self:
            old_state = old_states.get(contract.id)
            new_state = contract.state
            property_obj = contract.property_id

            if old_state != new_state:
                title = ""
                message = ""
                notification_type = 'info'

                if new_state == 'active':
                    title = _("تأكيد العقد")
                    neighborhood_name = property_obj.address if property_obj and property_obj.address else _("المحدد")
                    message = _("العقار في %s تم تأجيره أو بيعه بنجاح.") % (neighborhood_name)
                    notification_type = 'success'

                elif new_state == 'draft':
                    title = _("تنبيه قرب انتهاء العقد")
                    message = _("تنبيه: عقد العقار رقم %s شارف على الانتهاء.") % (contract.name)
                    notification_type = 'warning'

                elif new_state == 'expired':
                    title = _("انتهاء صلاحية العقد")
                    property_location = property_obj.name if property_obj and property_obj.name else _("المحدد")
                    message = _("العقار %s أصبح شاغرًا بعد انتهاء العقد.") % (property_location)
                    notification_type = 'info'

                if message:
                    notification_payload = {
                        'type': notification_type,
                        'title': title,
                        'message': message,
                        'sticky': False
                    }
                    self.env['bus.bus']._sendone(self.env.user.partner_id, 'estate_molhimah_notification', notification_payload)
        return res

    @api.model_create_multi
    def create(self, vals_list):
        contracts = super(RealEstateContract, self).create(vals_list)
        for contract in contracts:
            new_state = contract.state
            property_obj = contract.property_id
            title = ""
            message = ""
            notification_type = 'info'

            if new_state == 'active':
                title = _("عقد جديد مفعل")
                neighborhood_name = property_obj.address if property_obj and property_obj.address else _("المحدد")
                message = _("تم تفعيل عقد جديد للعقار في %s.") % (neighborhood_name)
                notification_type = 'success'

            if message:
                notification_payload = {
                    'type': notification_type,
                    'title': title,
                    'message': message,
                    'sticky': False
                }
                self.env['bus.bus']._sendone(self.env.user.partner_id, 'estate_molhimah_notification', notification_payload)
        return contracts
