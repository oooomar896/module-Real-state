from odoo import models, fields, api, _
from datetime import date, timedelta
import logging
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

class RealEstateContract(models.Model):
    _name = 'real.estate.contract'
    _description = 'عقد عقاري'

    name = fields.Char(string="رقم العقد", required=True, copy=False, default=lambda self: _('New'))
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
        ('active', 'عقد ساري'),
        ('ending_soon', 'قرب على الانتهاء'),
        ('expired', 'منتهي العقد'),
        ('cancelled', 'ملغي')
    ], string="الحالة", default='draft', tracking=True, copy=False)
    attachment_ids = fields.Many2many(
        'ir.attachment',
        'contract_attachment_rel',
        'contract_id', 'attachment_id',
        string="مرفقات العقد"
    )
    notes = fields.Text(string="ملاحظات")
    active = fields.Boolean(string="نشط", default=True)
    alert_message = fields.Html(string="تنبيه", compute="_compute_alert_message", store=False)

    _sql_constraints = [
        ('name_unique', 'UNIQUE(name)', 'رقم العقد يجب أن يكون فريداً!'),
        ('check_dates', 'CHECK(end_date IS NULL OR start_date <= end_date)', 'تاريخ نهاية العقد يجب أن يكون بعد تاريخ البداية.')
    ]

    def _get_calculated_state_from_dates(self, start_date, end_date, current_state_val=None):
        """
        Calculates the intended state of a contract based on its dates.
        :param start_date: The start date of the contract.
        :param end_date: The end date of the contract.
        :param current_state_val: The current state, used to avoid transitioning out of 'cancelled'.
        :return: The calculated state string.
        """
        today = fields.Date.today()
        thirty_days_from_today = today + timedelta(days=30)

        if current_state_val == 'cancelled':
            return 'cancelled' # Do not automatically change from cancelled

        # 1. Expired?
        if end_date and end_date < today:
            return 'expired'

        # 2. Active or Ending Soon? (Must have started)
        if start_date and start_date <= today:
            if end_date and end_date <= thirty_days_from_today: # Also covers end_date < today, but 'expired' check is first
                return 'ending_soon'
            # If no end_date, or end_date is beyond 30 days from today
            return 'active'

        # 3. Draft? (Hasn't started yet)
        if start_date and start_date > today:
            return 'draft'
        
        # Fallback for new records if dates are not set or for ambiguous cases
        # If called from create (current_state_val is None) and dates don't define state, default to draft.
        if current_state_val is None:
            return 'draft'
        
        # If current_state_val is provided and no other condition met, maintain current state.
        # This can happen if dates are e.g. both None.
        return current_state_val

    @api.constrains('unit_id', 'state')
    def _check_unit_active_contract_unique(self):
        for contract in self:
            if contract.unit_id and contract.state == 'active':
                domain = [
                    ('unit_id', '=', contract.unit_id.id),
                    ('state', '=', 'active')
                ]
                if contract.id and not isinstance(contract.id, models.NewId):
                    domain.append(('id', '!=', contract.id))
                
                existing_contracts_count = self.env['real.estate.contract'].search_count(domain)
                if existing_contracts_count > 0:
                    unit_name = contract.unit_id.display_name or _("هذه الوحدة")
                    raise ValidationError(_("الوحدة '%s' محجوزة حالياً في عقد آخر ساري.") % (unit_name))

    @api.model
    def _cron_update_contract_states(self):
        _logger.info("Cron job _cron_update_contract_states: Starting update.")
        contracts_to_update = self.env['real.estate.contract'].search([
            ('state', '!=', 'cancelled'),
            ('active', '=', True) 
        ])
        updated_contracts_count = 0
        for contract in contracts_to_update:
            original_state = contract.state
            new_state = contract._get_calculated_state_from_dates(contract.start_date, contract.end_date, contract.state)
            
            if new_state != original_state:
                contract.write({'state': new_state})
                updated_contracts_count += 1
        
        _logger.info(f"Cron job _cron_update_contract_states: Finished. Total updated {updated_contracts_count} contract(s).")

    @api.depends('end_date', 'start_date', 'state')
    def _compute_alert_message(self):
        today = date.today()
        for rec in self:
            rec.alert_message = ""
            if rec.state == 'expired':
                rec.alert_message = (
                    f'<div style="color:#fff; background:#d9534f; padding:8px; border-radius:4px; margin-bottom:8px;">'
                    f'⚠️ هذا العقد منتهي منذ {rec.end_date.strftime("%Y-%m-%d") if rec.end_date else _("تاريخ غير محدد")}!</div>'
                )
            elif rec.state == 'ending_soon' and rec.end_date:
                rec.alert_message = (
                    f'<div style="color:#856404; background:#fff3cd; padding:8px; border-radius:4px; margin-bottom:8px;">'
                    f'⏰ هذا العقد سينتهي خلال أقل من شهر (تاريخ الانتهاء: {rec.end_date.strftime("%Y-%m-%d")})!</div>'
                )
            elif rec.state == 'draft' and rec.start_date and rec.start_date > today:
                days_to_start = (rec.start_date - today).days
                rec.alert_message = (
                    f'<div style="color:#004085; background:#cce5ff; padding:8px; border-radius:4px; margin-bottom:8px;">'
                    f'ℹ️ هذا العقد سيبدأ خلال {days_to_start} يوم/أيام (تاريخ البدء: {rec.start_date.strftime("%Y-%m-%d")}).</div>'
                )

    @api.onchange('property_id', 'contract_type')
    def _onchange_property_unit(self):
        if self.unit_id and (not self.property_id or self.unit_id.property_id != self.property_id):
            self.unit_id = False
        domain_for_unit_id = []
        if self.property_id:
            domain_for_unit_id = [('property_id', '=', self.property_id.id)]
            if self.contract_type == 'rent_residential':
                domain_for_unit_id.append(('unit_type', '=', 'apartment'))
            elif self.contract_type == 'rent_commercial':
                domain_for_unit_id.append(('unit_type', '=', 'office'))
            if self.unit_id:
                if self.contract_type == 'rent_residential' and self.unit_id.unit_type != 'apartment':
                    self.unit_id = False
                elif self.contract_type == 'rent_commercial' and self.unit_id.unit_type != 'office':
                    self.unit_id = False
        else:
            domain_for_unit_id = [('id', '=', 0)] 
        return {'domain': {'unit_id': domain_for_unit_id}}

    def write(self, vals):
        # Check for restricted edits before any other logic
        allowed_fields_in_restricted_state = ['active'] # Fields allowed to be changed in expired/cancelled states
        for contract in self:
            if contract.state in ['expired', 'cancelled']:
                # Check if any non-allowed fields are being modified
                for field_name in vals:
                    if field_name not in allowed_fields_in_restricted_state:
                        raise ValidationError(_("لا يمكن تعديل العقد وهو في الحالة '%s', إلا إذا كان التعديل على الحقول المسموح بها فقط (مثل حقل 'نشط').") % contract.display_name)

        old_states_for_notification = {}
        if 'state' not in vals :
            if any(f in vals for f in ['start_date', 'end_date']):
                pass

        res = super(RealEstateContract, self).write(vals)

        contracts_to_recheck_state = self.env['real.estate.contract']
        if any(f in vals for f in ['start_date', 'end_date']) and 'state' not in vals:
            contracts_to_recheck_state = self

        for contract in self:
            old_state_for_notif = old_states_for_notification.get(contract.id, contract.state if 'state' in vals else None)
            current_persisted_state = contract.state
            
            if contract in contracts_to_recheck_state:
                target_state = contract._get_calculated_state_from_dates(contract.start_date, contract.end_date, current_persisted_state)
                if target_state != current_persisted_state:
                    contract.state = target_state

            old_state = old_states_for_notification.get(contract.id)
            new_state = contract.state
            property_obj = contract.property_id

            if old_state != new_state:
                title = ""
                message = ""
                notification_type = 'info'

                if new_state == 'active':
                    title = _("تفعيل العقد")
                    message = _("عقد العقار رقم %s (%s) أصبح ساري المفعول الآن.") % (contract.name, property_obj.name if property_obj else _('عقار غير محدد'))
                    notification_type = 'success'
                elif new_state == 'ending_soon':
                    title = _("تنبيه قرب انتهاء العقد")
                    message = _("تنبيه: عقد العقار رقم %s (%s) سينتهي قريبًا.") % (contract.name, property_obj.name if property_obj else _('عقار غير محدد'))
                    notification_type = 'warning'
                elif new_state == 'expired':
                    title = _("انتهاء صلاحية العقد")
                    message = _("عقد العقار رقم %s (%s) قد انتهت صلاحيته.") % (contract.name, property_obj.name if property_obj else _('عقار غير محدد'))
                    notification_type = 'info'
                elif new_state == 'draft':
                    title = _("إعادة العقد إلى مسودة")
                    message = _("عقد العقار رقم %s (%s) تم إعادته إلى حالة المسودة.") % (contract.name, property_obj.name if property_obj else _('عقار غير محدد'))
                    notification_type = 'info'
                elif new_state == 'cancelled':
                    title = _("إلغاء العقد")
                    message = _("عقد العقار رقم %s (%s) تم إلغاؤه.") % (contract.name, property_obj.name if property_obj else _('عقار غير محدد'))
                    notification_type = 'danger'

                if message:
                    notification_payload = {
                        'type': notification_type,
                        'title': title,
                        'message': message,
                        'sticky': False
                    }
                    self.env['bus.bus']._sendone(self.env.user.partner_id, 'estate_molhimah_notification', notification_payload)

                    # and check if the updated contract is the one currently viewed.
                    # We create a unique channel name for this specific purpose.
                    channel_name = f"real_estate_contract_state_update_channel"
                    live_update_payload = {'contract_id': contract.id, 'new_state': new_state}
                    self.env['bus.bus']._sendone(channel_name, 'live_contract_update', live_update_payload)
                    # END: Added code for live state update on the form view

        if 'state' not in vals and any(f in vals for f in ['start_date', 'end_date']):
            for contract_rec in self:
                target_state = contract_rec._get_calculated_state_from_dates(contract_rec.start_date, contract_rec.end_date, contract_rec.state)
                if target_state != contract_rec.state:
                    contract_rec.write({'state': target_state})
        
        return res

    @api.model_create_multi
    def create(self, vals_list):
        for i, vals in enumerate(vals_list):
            if vals.get('name', _('New')) == _('New'):
                sequence_code = 'real.estate.contract.sequence'
                vals['name'] = self.env['ir.sequence'].next_by_code(sequence_code) or _('New')
            
            start_date = fields.Date.to_date(vals.get('start_date'))
            end_date = fields.Date.to_date(vals.get('end_date'))
            calculated_state = self._get_calculated_state_from_dates(start_date, end_date, None)
            if 'state' not in vals or vals.get('state') == 'draft':
                vals['state'] = calculated_state
        
        contracts = super(RealEstateContract, self).create(vals_list)
        
        for contract in contracts:
            if contract.state == 'active':
                property_obj = contract.property_id
                title = _("عقد جديد مفعل")
                message = _("تم إنشاء وتفعيل عقد جديد %s للعقار %s.") % (contract.name, property_obj.name if property_obj else _('عقار غير محدد'))
                notification_payload = {
                    'type': 'success', 'title': title, 'message': message, 'sticky': False
                }
                self.env['bus.bus']._sendone(self.env.user.partner_id, 'estate_molhimah_notification', notification_payload)
        return contracts
