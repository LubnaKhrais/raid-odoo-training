from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal


class BikeRentalPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)

        if 'rental_count' in counters:
            partner = request.env.user.partner_id

            rentals = request.env['bike.rental'].search([
                ('customer_id', '=', partner.id)
            ])

            values['rental_count'] = len(rentals)

        return values


class BikeRentalPortalController(http.Controller):

    @http.route(
        ['/my/rentals'],
        type='http',
        auth='user',
        website=True
    )
    def portal_my_rentals(self, **kwargs):

        partner = request.env.user.partner_id

        rentals = request.env['bike.rental'].search([
            ('customer_id', '=', partner.id)
        ], order='start_date desc, id desc')

        values = {
            'rentals': rentals,
            'page_name': 'rental',
        }

        return request.render(
            'bike_management.portal_my_rentals',
            values
        )

    @http.route(
        ['/my/rentals/<int:rental_id>'],
        type='http',
        auth='user',
        website=True
    )
    def portal_rental_detail(self, rental_id, **kwargs):

        rental = request.env['bike.rental'].browse(rental_id)

        if not rental.exists():
            return request.not_found()

        values = {
            'rental': rental,
            'page_name': 'rental',
        }

        return request.render(
            'bike_management.portal_rental_detail',
            values
        )
