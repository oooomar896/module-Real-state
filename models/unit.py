from odoo import models, fields, api, _

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
            active_contracts = unit.contract_ids.filtered(lambda c: c.state == 'active')
            if active_contracts:
                unit.unit_status = 'rented_sold'
                continue

            # Priority 2: Draft contracts (interpreted as ending soon or new proposals)
            # Based on contract.py, 'draft' state is set for contracts ending within 30 days.
            draft_contracts = unit.contract_ids.filtered(lambda c: c.state == 'draft')
            if draft_contracts:
                unit.unit_status = 'ending_soon'
                continue
            
            # Priority 3: Determine status from the most recent relevant historical contract
            # Sort by end_date descending (recent expirations first), then start_date descending.
            # Contracts without an end_date are considered less relevant for historical status like 'expired'.
            # We prioritize contracts with an end_date first.
            sorted_contracts = unit.contract_ids.sorted(
                key=lambda c: (c.end_date is not None, c.end_date, c.start_date), reverse=True
            )

            latest_meaningful_contract = None
            if sorted_contracts:
                # Find the most recent contract that isn't active or draft (already handled)
                # and can give a historical status (expired, cancelled)
                for contract in sorted_contracts:
                    if contract.state not in ['active', 'draft']:
                        latest_meaningful_contract = contract
                        break 
            
            if latest_meaningful_contract:
                if latest_meaningful_contract.state == 'expired':
                    unit.unit_status = 'expired_vacant'
                elif latest_meaningful_contract.state == 'cancelled':
                    # This implies no active, draft, or non-cancelled expired contract took precedence
                    unit.unit_status = 'has_issues'
                else:
                    # If the latest meaningful historical contract is in an unexpected state
                    # or doesn't clearly define the unit as vacant/problematic, default to available.
                    # This could happen if a contract is, for example, in a custom state not covered.
                    unit.unit_status = 'available'
            else:
                # No active, draft, or other determining historical contracts found.
                # This implies the unit is available (e.g., all contracts were old and in a state like 'done' but not 'expired', or only future contracts exist which are not 'draft' yet)
                unit.unit_status = 'available'

    def write(self, vals):
        # Store old statuses before the write operation for accurate change detection
        old_statuses = {unit.id: unit.unit_status for unit in self}
        
        res = super(RealEstateUnit, self).write(vals)
        
        # After write, self is updated, including recomputation of unit_status if dependencies changed.
        for unit in self:
            old_status = old_statuses.get(unit.id)
            new_status = unit.unit_status
            
            if old_status != new_status and new_status == 'ending_soon':
                message = _("الوحدة '%s' أصبحت الآن قيد الانتهاء.") % unit.name
                title = _("تحديث حالة الوحدة: %s") % unit.name
                
                notification_payload = {
                    'type': 'warning', # Corresponds to Bootstrap alert types: success, info, warning, danger
                    'title': title,
                    'message': message,
                    'sticky': False # If true, user has to close it manually
                }
                # Send to the current user's partner channel
                # The JS service listens for 'estate_molhimah_notification' on the main bus_service channel for the user
                self.env['bus.bus']._sendone(self.env.user.partner_id, 'estate_molhimah_notification', notification_payload)
        
        return res
