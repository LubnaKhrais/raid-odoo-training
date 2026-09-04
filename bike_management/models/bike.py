from odoo import models, fields


class Bike(models.Model):
    _name = 'bike.management.bike'
    _description = 'Bike'
    _rec_name = 'name'

    name = fields.Char(
        string='Bike Name / Code',
        required=True,
        index=True
    )

    brand = fields.Char(
        string='Brand'
    )

    bike_type = fields.Selection(
        [
            ('road', 'Road'),
            ('mountain', 'Mountain'),
            ('city', 'City'),
            ('electric', 'Electric'),
        ],
        string='Bike Type',
        required=True
    )

    purchase_date = fields.Date(
        string='Purchase Date'
    )

    last_maintenance_date = fields.Date(
        string='Last Maintenance Date'
    )

    daily_rental_price = fields.Monetary(
        string='Daily Rental Price',
        currency_field='currency_id'
    )

    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id,
        required=True
    )

    wheel_size = fields.Float(
        string='Wheel Size (inches)'
    )
