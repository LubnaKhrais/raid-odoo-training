from odoo import api, fields, models
from odoo.exceptions import ValidationError

class RepairPart(models.Model):
    _name = 'bike.repair.part'
    _description = 'Repair Spare Part'

    repair_id = fields.Many2one(
        'bike.repair',
        string='Repair Job',
        required=True,
        ondelete='cascade'
    )

    product_id = fields.Many2one(
        'product.product',
        string='Spare Part',
        required=True,
	domain=[('product_tmpl_id.is_spare_part', '=', True)]
    )

    quantity = fields.Float(
        string='Quantity',
        required=True,
        default=1.0
    )

    unit_price = fields.Float(
        string='Unit Price',
        required=True
    )

    subtotal = fields.Float(
        string='Subtotal',
        compute='_compute_subtotal',
        store=True
    )

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.unit_price = self.product_id.lst_price

    @api.depends('quantity', 'unit_price')
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.quantity * line.unit_price

    @api.constrains('quantity', 'unit_price', 'subtotal')
    def _check_spare_part_values(self):
        for line in self:
            if line.quantity < 0:
                raise ValidationError(
                    "Spare part quantity cannot be negative."
                )

            if line.unit_price < 0:
                raise ValidationError(
                    "Spare part unit price cannot be negative."
                )

            if line.subtotal < 0:
                raise ValidationError(
                    "Spare part subtotal cannot be negative."
                )
