from odoo import fields, models


class ServiceTrackingMixin(models.AbstractModel):
    _name = 'bike.service.tracking.mixin'
    _description = 'Reusable Service Tracking'

    mechanic_id = fields.Many2one(
        'res.users',
        string='Assigned Mechanic'
    )

    last_service_date = fields.Date(
        string='Last Service Date'
    )

    service_notes = fields.Text(
        string='Service Notes'
    )
