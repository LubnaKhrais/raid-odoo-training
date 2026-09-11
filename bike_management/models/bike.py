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

    daily_rental_price = fields.Float(
        string='Daily Rental Price'
    )

    wheel_size = fields.Float(
        string='Wheel Size (inches)'
    )
