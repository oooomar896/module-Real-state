from odoo import models, fields

class RealEstateMaintenance(models.Model):
    _name = 'real.estate.nottajer_ids'
    _description = 'طلب صيانة عقاري'

    property_id = fields.Many2one('real.estate.contract', string="العقود", required=True)
    unit_id = fields.Many2one(
        'real.estate.unit',
        string="الوحدة (شقة/مكتب)",
        domain="[('property_id', '=', property_id)]"
    )
    

