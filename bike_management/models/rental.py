from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class BikeRental(models.Model):
    _name = 'bike.rental'
    _description = 'Bike Rental'
    _order = 'start_date desc, id desc'

    _sql_constraints = [
        (
            'name_unique',
            'unique(name)',
            'Rental reference must be unique.',
        ),
    ]

    name = fields.Char(
        string='Rental Reference',
        required=True,
        copy=False,
        readonly=True,
        default='New',
    )

    customer_id = fields.Many2one(
        'res.partner',
        string='Customer',
        required=True,
    )

    bike_id = fields.Many2one(
        'bike.management.bike',
        string='Bike',
        required=True,
    )

    bike_type = fields.Selection(
        related='bike_id.bike_type',
        string='Bike Type',
        store=True,
        readonly=True,
    )

    start_date = fields.Date(
        string='Start Date',
        required=True,
    )

    expected_return_date = fields.Date(
        string='Expected Return Date',
        required=True,
    )

    actual_return_date = fields.Date(
        string='Actual Return Date',
        readonly=True,
    )

    daily_price = fields.Float(
        string='Daily Price',
        required=True,
    )

    rental_duration = fields.Integer(
        string='Rental Duration',
        compute='_compute_rental_duration',
        store=True,
    )

    total_amount = fields.Float(
        string='Total Amount',
        compute='_compute_total_amount',
        store=True,
    )

    rental_count = fields.Integer(
        string='Rental Count',
        compute='_compute_rental_count',
        store=True,
    )

    return_performance = fields.Selection(
        [
            ('on_time', 'On Time'),
            ('late', 'Late'),
            ('pending', 'Pending'),
        ],
        string='Return Performance',
        compute='_compute_return_performance',
        store=True,
    )

    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
            ('returned', 'Returned'),
        ],
        string='Status',
        default='draft',
        required=True,
    )

    @api.depends('start_date', 'expected_return_date')
    def _compute_rental_duration(self):
        for rental in self:
            if rental.start_date and rental.expected_return_date:
                rental.rental_duration = (
                    rental.expected_return_date - rental.start_date
                ).days
            else:
                rental.rental_duration = 0

    @api.depends('rental_duration', 'daily_price')
    def _compute_total_amount(self):
        for rental in self:
            rental.total_amount = rental.rental_duration * rental.daily_price

    @api.depends()
    def _compute_rental_count(self):
        for rental in self:
            rental.rental_count = 1

    @api.depends('actual_return_date', 'expected_return_date')
    def _compute_return_performance(self):
        for rental in self:
            if not rental.actual_return_date:
                rental.return_performance = 'pending'
            elif rental.actual_return_date <= rental.expected_return_date:
                rental.return_performance = 'on_time'
            else:
                rental.return_performance = 'late'

    @api.onchange('bike_id')
    def _onchange_bike_id(self):
        if self.bike_id:
            self.daily_price = self.bike_id.daily_rental_price

    @api.onchange('start_date', 'expected_return_date')
    def _onchange_return_date(self):
        if (
            self.start_date
            and self.expected_return_date
            and self.expected_return_date <= self.start_date
        ):
            return {
                'warning': {
                    'title': _('Invalid Return Date'),
                    'message': _(
                        'The expected return date must be after '
                        'the rental start date.'
                    ),
                }
            }

    @api.constrains('start_date', 'expected_return_date')
    def _check_dates(self):
        for rental in self:
            if (
                rental.start_date
                and rental.expected_return_date
                and rental.expected_return_date <= rental.start_date
            ):
                raise ValidationError(
                    _(
                        'The expected return date must be after '
                        'the rental start date.'
                    )
                )

    @api.constrains('daily_price')
    def _check_daily_price(self):
        for rental in self:
            if rental.daily_price < 0:
                raise ValidationError(
                    _('Daily rental price cannot be negative.')
                )

    @api.constrains('rental_duration')
    def _check_rental_duration(self):
        for rental in self:
            if rental.rental_duration <= 0:
                raise ValidationError(
                    _('Rental duration must be greater than zero.')
                )

    @api.constrains('total_amount')
    def _check_total_amount(self):
        for rental in self:
            if rental.total_amount < 0:
                raise ValidationError(
                    _('Total rental amount cannot be negative.')
                )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'bike.rental'
                ) or 'New'

            if vals.get('bike_id') and not vals.get('daily_price'):
                bike = self.env['bike.management.bike'].browse(
                    vals['bike_id']
                )
                vals['daily_price'] = bike.daily_rental_price

        return super().create(vals_list)

    def action_confirm(self):
        for rental in self:
            if rental.state != 'draft':
                raise UserError(
                    _('Only draft rentals can be confirmed.')
                )

            if not rental.bike_id:
                raise UserError(
                    _('Please select a bike before confirming the rental.')
                )

            if not rental.start_date or not rental.expected_return_date:
                raise UserError(
                    _(
                        'Please set the rental start date and '
                        'expected return date.'
                    )
                )

            if rental.expected_return_date <= rental.start_date:
                raise UserError(
                    _(
                        'The expected return date must be after '
                        'the rental start date.'
                    )
                )

            repair_in_progress = self.env['bike.repair'].search(
                [
                    ('bike_id', '=', rental.bike_id.id),
                    ('state', '=', 'in_progress'),
                ],
                limit=1,
            )

            if repair_in_progress:
                raise UserError(
                    _(
                        'This bike currently has a repair in progress '
                        'and cannot be rented.'
                    )
                )

            overlapping_rental = self.search(
                [
                    ('id', '!=', rental.id),
                    ('bike_id', '=', rental.bike_id.id),
                    ('state', '=', 'confirmed'),
                    ('start_date', '<=', rental.expected_return_date),
                    ('expected_return_date', '>=', rental.start_date),
                ],
                limit=1,
            )

            if overlapping_rental:
                raise UserError(
                    _(
                        'This bike already has an overlapping rental.'
                    )
                )

            rental.state = 'confirmed'

    def action_return(self):
        for rental in self:
            if rental.state != 'confirmed':
                raise UserError(
                    _('Only confirmed rentals can be returned.')
                )

            rental.actual_return_date = fields.Date.context_today(rental)
            rental.state = 'returned'

    def action_view_rentals(self):
        self.ensure_one()

        return {
            'type': 'ir.actions.act_window',
            'name': _('Rental History'),
            'res_model': 'bike.rental',
            'view_mode': 'list,form',
            'domain': [
                ('bike_id', '=', self.bike_id.id),
            ],
            'context': {
                'default_bike_id': self.bike_id.id,
            },
        }
