from odoo import SUPERUSER_ID, api


def post_init_hook(env):
    group = env.ref('bike_management.group_bike_workshop_staff')
    admin = env['res.users'].browse(SUPERUSER_ID)
    group.write({'user_ids': [(4, admin.id)]})
