from odoo import _, api, fields, models
from odoo.exceptions import UserError


class RepairJob(models.Model):
    _name = 'bike.repair'
    _inherit = ['bike.service.tracking.mixin']
    _description = 'Bike Repair Job'
    _order = 'id desc'

    _sql_constraints = [
        (
            'name_unique',
            'unique(name)',
            'Repair reference must be unique.',
        ),
    ]

    name = fields.Char(
        string='Repair Reference',
        required=True,
        copy=False,
        readonly=True,
        default='New',
    )

    customer_id = fields.Many2one(
        'res.partner',
        string='Customer',
    )

    bike_source = fields.Selection(
        [
            ('workshop', 'Workshop Bike'),
            ('external', 'External Bike'),
        ],
        string='Bike Source',
        required=True,
        default='workshop',
    )

    bike_id = fields.Many2one(
        'bike.management.bike',
        string='Workshop Bike',
    )

    external_bike_reference = fields.Char(
        string='External Bike Reference',
    )

    external_bike_brand = fields.Char(
        string='External Bike Brand',
    )

    external_bike_type = fields.Selection(
        [
            ('road', 'Road'),
            ('mountain', 'Mountain'),
            ('city', 'City'),
            ('electric', 'Electric'),
        ],
        string='External Bike Type',
    )

    reported_issue = fields.Text(
        string='Reported Issue',
    )

    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('in_progress', 'In Progress'),
            ('completed', 'Completed'),
            ('cancelled', 'Cancelled'),
        ],
        string='Status',
        default='draft',
        required=True,
    )

    spare_part_line_ids = fields.One2many(
        'bike.repair.part',
        'repair_id',
        string='Spare Parts',
    )

    total_spare_parts_cost = fields.Float(
        string='Total Spare Parts Cost',
        compute='_compute_total_spare_parts_cost',
        store=True,
    )

    @api.depends('spare_part_line_ids.subtotal')
    def _compute_total_spare_parts_cost(self):
        for repair in self:
            repair.total_spare_parts_cost = sum(
                repair.spare_part_line_ids.mapped('subtotal')
            )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'bike.repair'
                ) or 'New'

        return super().create(vals_list)

    def action_start(self):
        for repair in self:
            if repair.state != 'draft':
                raise UserError(
                    _('Only Draft Repair Jobs can be started.')
                )

            if not repair.customer_id:
                raise UserError(
                    _('A customer is required before starting the repair.')
                )

            if not repair.reported_issue:
                raise UserError(
                    _('A reported issue is required before starting the repair.')
                )

            if not repair.mechanic_id:
                raise UserError(
                    _('An assigned mechanic is required before starting the repair.')
                )

            if repair.bike_source == 'workshop' and not repair.bike_id:
                raise UserError(
                    _('A workshop bike is required for a workshop repair.')
                )

            if repair.bike_source == 'external':
                if not repair.external_bike_reference:
                    raise UserError(
                        _('An external bike reference is required.')
                    )

                if not repair.external_bike_brand:
                    raise UserError(
                        _('An external bike brand is required.')
                    )

                if not repair.external_bike_type:
                    raise UserError(
                        _('An external bike type is required.')
                    )

            repair.state = 'in_progress'

    def action_complete(self):
        for repair in self:
            if repair.state != 'in_progress':
                raise UserError(
                    _('Only Repair Jobs in progress can be completed.')
                )

            if not repair.service_notes:
                raise UserError(
                    _('Service Notes are required before completing the repair.')
                )

            if not repair.last_service_date:
                raise UserError(
                    _('Last Service Date is required before completing the repair.')
                )

            repair.state = 'completed'

    def action_cancel(self):
        for repair in self:
            if repair.state not in ('draft', 'in_progress'):
                raise UserError(
                    _('Only Draft or In Progress Repair Jobs can be cancelled.')
                )

            repair.state = 'cancelled'
