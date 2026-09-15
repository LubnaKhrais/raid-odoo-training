from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal


class BikeRentalPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)

        if 'rental_count' in counters:
            partner = request.env.user.partner_id

            rentals = request.env['bike.rental'].sudo().search([]).filtered(
                lambda rental: rental.customer_id.id == partner.id
            )

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

        # Get rentals belonging ONLY to the logged-in user's Contact.
        rentals = request.env['bike.rental'].sudo().search([]).filtered(
            lambda rental: rental.customer_id.id == partner.id
        )

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

        partner = request.env.user.partner_id

        rental = request.env['bike.rental'].sudo().browse(rental_id)

        # Rental must belong to the logged-in user's Contact.
        if not rental.exists() or rental.customer_id.id != partner.id:
            return request.not_found()

        values = {
            'rental': rental,
            'page_name': 'rental',
        }

        return request.render(
            'bike_management.portal_rental_detail',
            values
        )
