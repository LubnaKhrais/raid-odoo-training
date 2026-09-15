from odoo import models, fields


class Bike(models.Model):
    _name = 'bike.management.bike'
    _inherit = ['bike.service.tracking.mixin']
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
    rental_count = fields.Integer(
    	string='Rentals',
    	compute='_compute_rental_count'
    )

    def _compute_rental_count(self):
        for bike in self:
            bike.rental_count = self.env['bike.rental'].search_count([
                ('bike_id', '=', bike.id)
            ])

    def action_view_rentals(self):
        self.ensure_one()

        return {
            'type': 'ir.actions.act_window',
            'name': 'Rental History',
            'res_model': 'bike.rental',
            'view_mode': 'list,form',
            'domain': [('bike_id', '=', self.id)],
            'context': {
                'default_bike_id': self.id,
            },
        }
