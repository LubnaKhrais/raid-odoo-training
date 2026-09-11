from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class BikeRental(models.Model):
    _name = 'bike.rental'
    _description = 'Bike Rental'
    _order = 'id desc'

    name = fields.Char(
        string='Rental Reference',
        required=True,
        copy=False,
        readonly=True,
        default='New'
    )

    customer_id = fields.Many2one(
        'res.partner',
        string='Customer',
        required=True
    )

    bike_id = fields.Many2one(
        'bike.management.bike',
        string='Bike',
        required=True
    )

    start_date = fields.Date(
        string='Rental Start Date',
        required=True
    )

    expected_return_date = fields.Date(
        string='Expected Return Date',
        required=True
    )

    actual_return_date = fields.Date(
        string='Actual Return Date',
        readonly=True
    )

    daily_price = fields.Float(
        string='Daily Rental Price',
        required=True
    )

    rental_duration = fields.Integer(
        string='Rental Duration',
        compute='_compute_rental_duration',
        store=True
    )

    total_amount = fields.Float(
        string='Total Rental Amount',
        compute='_compute_total_amount',
        store=True
    )

    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
            ('returned', 'Returned'),
        ],
        string='Status',
        default='draft',
        required=True
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'bike.rental'
                ) or 'New'

            if vals.get('bike_id') and 'daily_price' not in vals:
                bike = self.env['bike.management.bike'].browse(vals['bike_id'])
                vals['daily_price'] = bike.daily_rental_price

        return super().create(vals_list)

    @api.onchange('bike_id')
    def _onchange_bike_id(self):
        if self.bike_id:
            self.daily_price = self.bike_id.daily_rental_price

    @api.onchange('start_date', 'expected_return_date')
    def _onchange_rental_dates(self):
        if self.start_date and self.expected_return_date:
            if self.expected_return_date <= self.start_date:
                self.rental_duration = 0

                return {
                    'warning': {
                        'title': 'Invalid Return Date',
                        'message': (
                            'Expected Return Date must be after '
                            'Start Date.'
                        ),
                    }
                }

            self.rental_duration = (
                self.expected_return_date - self.start_date
            ).days

    @api.depends('start_date', 'expected_return_date')
    def _compute_rental_duration(self):
        for rental in self:
            if rental.start_date and rental.expected_return_date:
                rental.rental_duration = (
                    rental.expected_return_date
                    - rental.start_date
                ).days
            else:
                rental.rental_duration = 0

    @api.depends('rental_duration', 'daily_price')
    def _compute_total_amount(self):
        for rental in self:
            rental.total_amount = (
                rental.rental_duration * rental.daily_price
            )

    @api.constrains(
        'start_date',
        'expected_return_date',
        'rental_duration',
        'daily_price',
        'total_amount'
    )
    def _check_rental_values(self):
        for rental in self:

            if (
                rental.start_date
                and rental.expected_return_date
                and rental.expected_return_date <= rental.start_date
            ):
                raise ValidationError(
                    'Expected Return Date must be after Start Date.'
                )

            if rental.rental_duration <= 0:
                raise ValidationError(
                    'Rental duration must be greater than zero.'
                )

            if rental.daily_price < 0:
                raise ValidationError(
                    'Daily rental price cannot be negative.'
                )

            if rental.total_amount < 0:
                raise ValidationError(
                    'Total rental amount cannot be negative.'
                )

    def action_confirm(self):
        for rental in self:

            if rental.state != 'draft':
                raise UserError(
                    'Only Draft Rentals can be confirmed.'
                )

            if not rental.bike_id:
                raise UserError(
                    'A bike is required before confirming the rental.'
                )

            if (
                rental.start_date
                and rental.expected_return_date
                and rental.expected_return_date <= rental.start_date
            ):
                raise UserError(
                    'Expected Return Date must be after Start Date.'
                )

            repairs = self.env['bike.repair'].search([
                ('bike_id', '=', rental.bike_id.id),
                ('bike_source', '=', 'workshop'),
                ('state', '=', 'in_progress'),
            ], limit=1)

            if repairs:
                raise UserError(
                    'This bike currently has a Repair Job In Progress. '
                    'The rental cannot be confirmed until the repair is '
                    'completed or cancelled.'
                )

            conflicts = self.search([
                ('id', '!=', rental.id),
                ('bike_id', '=', rental.bike_id.id),
                ('state', '=', 'confirmed'),
                ('start_date', '<', rental.expected_return_date),
                ('expected_return_date', '>', rental.start_date),
            ], limit=1)

            if conflicts:
                raise UserError(
                    'This bike already has a confirmed rental '
                    'during the selected dates.'
                )

            rental.state = 'confirmed'

    def action_return(self):
        for rental in self:

            if rental.state != 'confirmed':
                raise UserError(
                    'Only Confirmed Rentals can be returned.'
                )

            rental.actual_return_date = fields.Date.today()
            rental.state = 'returned'
