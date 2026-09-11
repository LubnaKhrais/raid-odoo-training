from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    preferred_bike_type = fields.Selection(
        [
            ('road', 'Road'),
            ('mountain', 'Mountain'),
            ('city', 'City'),
            ('electric', 'Electric'),
        ],
        string='Preferred Bike Type'
    )
