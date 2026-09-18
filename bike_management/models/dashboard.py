from odoo import fields, models


class BikeWorkshopDashboard(models.TransientModel):
    _name = 'bike.workshop.dashboard'
    _description = 'Bike Workshop Operations Dashboard'

    active_rentals_today = fields.Integer(
        string='Active Rentals Today',
        compute='_compute_dashboard_counts'
    )

    returns_due_today = fields.Integer(
        string='Returns Due Today',
        compute='_compute_dashboard_counts'
    )

    repairs_in_progress = fields.Integer(
        string='Repairs In Progress',
        compute='_compute_dashboard_counts'
    )

    def _compute_dashboard_counts(self):
        today = fields.Date.today()

        rental_model = self.env['bike.rental']
        repair_model = self.env['bike.repair']

        for dashboard in self:
            dashboard.active_rentals_today = rental_model.search_count([
                ('state', '=', 'confirmed'),
                ('start_date', '<=', today),
                ('expected_return_date', '>=', today),
            ])

            dashboard.returns_due_today = rental_model.search_count([
                ('state', '=', 'confirmed'),
                ('expected_return_date', '=', today),
            ])

            dashboard.repairs_in_progress = repair_model.search_count([
                ('state', '=', 'in_progress'),
            ])

    def action_open_dashboard(self):
        """Open one fixed dashboard record."""
        dashboard = self.search([], limit=1)

        if not dashboard:
            dashboard = self.create({})

        return {
            'type': 'ir.actions.act_window',
            'name': 'Workshop Operations Dashboard',
            'res_model': 'bike.workshop.dashboard',
            'view_mode': 'form',
            'views': [
                (
                    self.env.ref(
                        'bike_management.view_bike_workshop_dashboard_form'
                    ).id,
                    'form',
                ),
            ],
            'res_id': dashboard.id,
            'target': 'current',
            'context': {
                'create': False,
                'edit': False,
                'delete': False,
            },
        }

    def action_view_active_rentals(self):
        self.ensure_one()

        today = fields.Date.today()

        return {
            'type': 'ir.actions.act_window',
            'name': 'Active Rentals Today',
            'res_model': 'bike.rental',
            'view_mode': 'list,form',
            'domain': [
                ('state', '=', 'confirmed'),
                ('start_date', '<=', today),
                ('expected_return_date', '>=', today),
            ],
        }

    def action_view_returns_due(self):
        self.ensure_one()

        today = fields.Date.today()

        return {
            'type': 'ir.actions.act_window',
            'name': 'Returns Due Today',
            'res_model': 'bike.rental',
            'view_mode': 'list,form',
            'domain': [
                ('state', '=', 'confirmed'),
                ('expected_return_date', '=', today),
            ],
        }

    def action_view_repairs_in_progress(self):
        self.ensure_one()

        return {
            'type': 'ir.actions.act_window',
            'name': 'Repairs In Progress',
            'res_model': 'bike.repair',
            'view_mode': 'list,form',
            'domain': [
                ('state', '=', 'in_progress'),
            ],
        }
