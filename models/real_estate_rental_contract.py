from odoo import models, fields, api

class RealEstateRentalContract(models.Model):
    _name = "real.estate.rental.contract"
    _description = "Rental Contract"
    asset_id = fields.Many2one("real.estate.asset", string="العقار")  # هذا ضروري للرابط
    tenant_name = fields.Char(string="اسم المستأجر", required=True)
    tenant_phone = fields.Char(string="هاتف المستأجر")
    start_date = fields.Date(string="تاريخ البداية", required=True)
    end_date = fields.Date(string="تاريخ النهاية", required=True)
    rent_amount = fields.Float(string="قيمة الإيجار", required=True)
    notes = fields.Text(string="ملاحظات")
    state = fields.Selection([
        ('draft', 'مسودة'),
        ('active', 'ساري'),
        ('expired', 'منتهي'),
    ], string="حالة العقد", default='draft')

    @api.model
    def create(self, vals):
        rec = super().create(vals)
        # عند تفعيل العقد، اجعل حالة العقار "مؤجر"
        if vals.get('state') == 'active' and rec.asset_id:
            rec.asset_id.status = 'rented'
        return rec

    def write(self, vals):
        res = super().write(vals)
        for rec in self:
            if rec.state == 'active' and rec.asset_id:
                rec.asset_id.status = 'rented'
        return res
