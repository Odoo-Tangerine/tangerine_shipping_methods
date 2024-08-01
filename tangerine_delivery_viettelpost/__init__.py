from . import models, controllers, wizard, api, settings
from odoo import api, SUPERUSER_ID


def _generate_master_data(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env['viettelpost.service'].service_synchronous()
    env['viettelpost.service.extend'].service_extend_synchronous()
