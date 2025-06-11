from odoo import models, fields, api, _
from datetime import date, timedelta

class RealEstateUnit(models.Model):
    _name = 'real.estate.unit'
    _description = 'وحدة عقارية (شقة أو مكتب)'
    property_id = fields.Many2one('real.estate.property', string="العقار", required=True, ondelete='cascade')
    name = fields.Char(string="رقم/اسم الوحدة", required=True)
    unit_type = fields.Selection([
        ('apartment', 'شقة'),
        ('showroom', 'معرض'),
        ('shop', 'محل'),
        ('office', 'مكتب')
    ], string="نوع الوحدة", required=True)
    floor = fields.Char(string="الدور")
    area = fields.Float(string="المساحة (م²)")
    active = fields.Boolean(string="نشط", default=True)
    sequence = fields.Integer(string="الترتيب", default=10)

    # الحقل المطلوب لربط العقود بالوحدة
    contract_ids = fields.One2many('real.estate.contract', 'unit_id', string="العقود")
    unit_status = fields.Selection([
        ('available', 'متاحة'),
        ('rented_sold', 'مؤجرة/مباعة'),
        ('ending_soon', 'قيد الانتهاء'), # Contract is in draft (ending in <30 days or new proposal)
        ('expired_vacant', 'عقد منتهي (شاغرة)'),
        ('has_issues', 'بها مشاكل/ملغاة') # e.g. last relevant contract was cancelled
    ], string="حالة الوحدة", compute='_compute_unit_status', store=True, readonly=True,
       help="تحدد حالة الوحدة بناءً على عقودها المرتبطة:\n"
            "- متاحة: لا توجد عقود أو أحدث عقد لا يضعها في حالة أخرى.\n"
            "- مؤجرة/مباعة: يوجد عقد ساري المفعول.\n"
            "- قيد الانتهاء: يوجد عقد مسودة (سينتهي قريباً أو عرض جديد).\n"
            "- عقد منتهي (شاغرة): أحدث عقد ذو صلة منتهي الصلاحية.\n"
            "- بها مشاكل/ملغاة: أحدث عقد ذو صلة تم إلغاؤه.")

    @api.depends('contract_ids.state', 'contract_ids.end_date', 'contract_ids.start_date')
    def _compute_unit_status(self):
        for unit in self:
            if not unit.contract_ids:
                unit.unit_status = 'available'
                continue

            # Priority 1: Active contracts
            # Use any() for potentially better performance if a match is found early
            if any(c.state == 'active' for c in unit.contract_ids):
                unit.unit_status = 'rented_sold'
                continue

            # Priority 2: Ending Soon contracts (contracts that are active but ending within 30 days)
            if any(c.state == 'ending_soon' for c in unit.contract_ids):
                unit.unit_status = 'ending_soon'
                continue
            
            # Priority 3: Determine status from historical or other non-active/non-ending_soon contracts.
            # (e.g., draft, expired, cancelled)
            
            # Sort these remaining contracts (all non-active, non-draft)
            # to find the most relevant one.
            # Prioritize contracts with an end_date, then by most recent end_date, then start_date.
            # Since unit.contract_ids is guaranteed to be non-empty here (due to the first check)
            # and contains no active/draft (due to previous checks),
            # sorted_contracts will also be non-empty.
            sorted_contracts = unit.contract_ids.sorted(
                key=lambda c: (c.end_date is not None, c.end_date, c.start_date), reverse=True
            )
            
            # The first contract in this sorted list is the most relevant one.
            most_relevant_contract = sorted_contracts[0]
            
            if most_relevant_contract.state == 'expired':
                unit.unit_status = 'expired_vacant'
            elif most_relevant_contract.state == 'cancelled':
                unit.unit_status = 'has_issues'
            else:
                # If the most recent contract (that's not active/draft) is in some other state
                # (e.g., 'done' but not 'expired', or a custom state not covered),
                # the unit is considered 'available'.
                unit.unit_status = 'available'

    def write(self, vals):
        old_statuses = {unit.id: unit.unit_status for unit in self}
        
        res = super(RealEstateUnit, self).write(vals)
        
        for unit in self:
            old_status = old_statuses.get(unit.id)
            new_status = unit.unit_status # This is the status after the write and recomputation
            
            if old_status != new_status:
                message = ""
                title = ""
                notification_type = 'info' # Default type
                sticky = False

                if new_status == 'available':
                    title = _("تحديث حالة الوحدة: %s") % unit.name
                    message = _("الوحدة '%s' أصبحت الآن متاحة.") % unit.name
                    notification_type = 'info'
                elif new_status == 'rented_sold':
                    title = _("تحديث حالة الوحدة: %s") % unit.name
                    message = _("الوحدة '%s' تم تأجيرها/بيعها.") % unit.name
                    notification_type = 'success'
                elif new_status == 'ending_soon':
                    title = _("تنبيه حالة الوحدة: %s") % unit.name
                    message = _("الوحدة '%s' أصبحت الآن قيد الانتهاء.") % unit.name
                    notification_type = 'warning'
                elif new_status == 'expired_vacant':
                    title = _("تحديث حالة الوحدة: %s") % unit.name
                    message = _("الوحدة '%s' أصبح عقدها منتهيًا وهي شاغرة.") % unit.name
                    notification_type = 'warning' # Or 'info' depending on desired urgency
                    sticky = True # Make it sticky as it might require action
                # Add elif for 'has_issues' if specific notification is desired
                # elif new_status == 'has_issues':
                #     title = _("تنبيه مشكلة بالوحدة: %s") % unit.name
                #     message = _("الوحدة '%s' تم تسجيل مشكلة بها أو تم إلغاء عقدها الأخير.") % unit.name
                #     notification_type = 'danger'
                #     sticky = True

                if message: # Ensure a message was set
                    notification_payload = {
                        'type': notification_type,
                        'title': title,
                        'message': message,
                        'sticky': sticky
                    }
                    self.env['bus.bus']._sendone(self.env.user.partner_id, 'estate_molhimah_notification', notification_payload)
        
        return res

    @api.depends('end_date')
    def _compute_alert_message(self):
        today = date.today() # يستخدم تاريخ اليوم فقط، بدون وقت
        for rec in self:
            rec.alert_message = ""
            if rec.end_date:
                if rec.end_date < today: # يقارن تاريخ الانتهاء بتاريخ اليوم
                    rec.alert_message = (
                        f'<div style="color:#fff; background:#d9534f; padding:8px; border-radius:4px; margin-bottom:8px;">'
                        f'⚠️ هذا العقد منتهي منذ {rec.end_date.strftime("%Y-%m-%d")}!</div>'
                    )
                elif today <= rec.end_date <= today + timedelta(days=30): # يقارن بين تاريخ اليوم وتاريخ الانتهاء + 30 يوم
                    rec.alert_message = (
                        f'<div style="color:#856404; background:#fff3cd; padding:8px; border-radius:4px; margin-bottom:8px;">'
                        f'⏰ هذا العقد سينتهي خلال أقل من شهر (تاريخ الانتهاء: {rec.end_date.strftime("%Y-%m-%d")})!</div>'
                    )
