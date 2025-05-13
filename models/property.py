from odoo import models, fields, api, _
from datetime import date

class RealEstateProperty(models.Model):
    _name = 'real.estate.property'
    _description = 'عقار'

    name = fields.Char(string="اسم العقار", required=True)
    code = fields.Char(string="كود العقار")
    type = fields.Selection([
        ('apartment', 'شقة'),
        ('villa', 'فيلا'),
        ('shop', 'محل'),
        ('land', 'أرض'),
        ('building', 'عمارة'),
        ('office', 'مكتب'),
        ('warehouse', 'مستودع'),
    ], string="النوع", required=True)
    address = fields.Char(string="العنوان")
    city = fields.Char(string="المدينة")
    area = fields.Float(string="المساحة (م2)")
    floor = fields.Char(string="الدور")
    building = fields.Char(string="اسم/كود المبنى")
    project = fields.Char(string="اسم المشروع")
    owner_id = fields.Many2one('res.partner', string="المالك")
    state = fields.Selection([
        ('available', 'شاغر'),
        ('rented', 'مؤجر'),
        ('endrented', 'منتهي العقد'),
        ('maintenance', 'تحت الصيانة'),
        ('sold', 'مباع')
    ], string="الحالة", default='available')
    total_units = fields.Integer(string="إجمالي الوحدات")
    finishing_status = fields.Selection([
        ('unfinished', 'غير مكتمل'),
        ('semi_finished', 'نصف تشطيب'),
        ('fully_finished', 'تشطيب كامل'),
        ('luxury', 'فاخر'),
    ], string="حالة التشطيب")
    usage_type = fields.Selection([
        ('residential', 'سكني'),
        ('commercial', 'تجاري'),
        ('mixed', 'سكني وتجاري'),
        ('industrial', 'صناعي'),
        ('other', 'أخرى'),
    ], string="نوع الاستخدام")
    service_notes = fields.Text(string="ملاحظات الخدمة")
    license_number = fields.Char(string="رقم الرخصة")
    purchase_date = fields.Date(string="تاريخ التأجير ")
    property_value = fields.Float(string="مبلغ الإجار")
    rented_units = fields.Integer(string="الوحدات المؤجرة")
    commercial_rented_units = fields.Integer(string="الوحدات التجارية المؤجرة")
    residential_rented_units = fields.Integer(string="الوحدات السكنية المؤجرة")
    occupancy_rate = fields.Float(string="نسبة الإشغال", compute="_compute_occupancy_rate", store=True)
    description = fields.Text(string="ملاحظات")
    contract_ids = fields.One2many('real.estate.contract', 'property_id', string="العقود")
    expense_ids = fields.One2many('real.estate.expense', 'property_id', string="المصروفات")
    maintenance_ids = fields.One2many('real.estate.maintenance', 'property_id', string="طلبات الصيانة")
    unit_ids = fields.One2many('real.estate.unit', 'property_id', string="الوحدات")

    # الحقول الجديدة للمستأجرين
    tenant_ids = fields.Many2many(
        'res.partner',
        compute='_compute_tenant_ids',
        string="جميع المستأجرين",
        store=False
    )
    tenant_names = fields.Char(
        string="أسماء المستأجرين",
        compute='_compute_tenant_names',
        store=False
    )

    available_unit_count = fields.Integer(
        string="عدد الوحدات المتوفرة",
        compute="_compute_available_unit_count",
        store=False
    )
    attachment_ids = fields.Many2many(
        'ir.attachment',
        'property_attachment_rel',
        'property_id', 'attachment_id',
        string="المرفقات"
    )
    image = fields.Binary(string="صورة رئيسية")
    latitude = fields.Float(string="خط العرض")
    longitude = fields.Float(string="خط الطول")
    active = fields.Boolean(string="نشط", default=True)
    registration_date = fields.Date(string="تاريخ التسجيل")
    country = fields.Char(string="الدولة", default="السعودية")
    balance = fields.Float(string="الرصيد المالي")
    contract_count = fields.Integer(string="عدد العقود", compute="_compute_contract_count", store=True)
    tenant_count = fields.Integer(string="عدد المستأجرين", compute="_compute_tenant_count", store=True)
    owner_count = fields.Integer(string="عدد الملاك", compute="_compute_owner_count", store=True)
    ended_contract_ids = fields.Many2many(
        'real.estate.contract',
        string="العقود المنتهية",
        compute="_compute_ended_contracts",
        store=True
    )

    # --- دوال الحقول المحسوبة ---

    def _compute_occupancy_rate(self):
        for record in self:
            total_rented_units = record.commercial_rented_units + record.residential_rented_units
            if record.total_units > 0:
                record.occupancy_rate = (total_rented_units / record.total_units) * 100
            else:
                record.occupancy_rate = 0.0

    @api.depends('unit_ids', 'unit_ids.contract_ids.state')
    def _compute_available_unit_count(self):
        for record in self:
            count = 0
            for unit in record.unit_ids:
                active_contracts = unit.contract_ids.filtered(lambda c: c.state == 'active')
                if not active_contracts:
                    count += 1
            record.available_unit_count = count

    @api.depends('contract_ids')
    def _compute_contract_count(self):
        for record in self:
            record.contract_count = len(record.contract_ids)

    @api.depends('contract_ids.tenant_id')
    def _compute_tenant_count(self):
        for record in self:
            tenants = record.contract_ids.mapped('tenant_id')
            record.tenant_count = len(set(tenants))

    @api.depends('owner_id')
    def _compute_owner_count(self):
        for record in self:
            record.owner_count = 1 if record.owner_id else 0

    @api.depends('contract_ids.state')
    def _compute_ended_contracts(self):
        for record in self:
            ended = record.contract_ids.filtered(lambda c: c.state == 'endrented')
            record.ended_contract_ids = ended

    @api.depends('contract_ids.tenant_id')
    def _compute_tenant_ids(self):
        for rec in self:
            tenants = rec.contract_ids.mapped('tenant_id')
            rec.tenant_ids = [(6, 0, tenants.ids)]

    @api.depends('contract_ids.tenant_id')
    def _compute_tenant_names(self):
        for rec in self:
            tenants = rec.contract_ids.mapped('tenant_id.name')
            rec.tenant_names = ', '.join(tenants) if tenants else 'لا يوجد مستأجرين'

    @api.depends('contract_ids.end_date')
    def _check_and_update_property_state(self):
        for record in self:
            all_contracts_ended = all(
                contract.end_date and contract.end_date < date.today()
                for contract in record.contract_ids
            )
            if all_contracts_ended and record.contract_ids:
                if record.state != 'endrented':
                    record.state = 'endrented'
                    if record.owner_id and record.owner_id.user_ids:
                        record.message_post(
                            body=_("تم انتهاء جميع العقود لهذا العقار: %s" % record.name),
                            partner_ids=record.owner_id.user_ids.mapped('partner_id').ids
                        )

    @api.onchange('contract_ids')
    def onchange_contract_ids(self):
        self._check_and_update_property_state()
