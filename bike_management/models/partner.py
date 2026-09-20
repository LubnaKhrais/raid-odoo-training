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

    rental_ids = fields.One2many(
        'bike.rental',
        'customer_id',
        string='Rental History',
        readonly=True,
    )
