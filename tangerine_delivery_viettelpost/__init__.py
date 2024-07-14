from . import models, controllers, wizard, api, settings


def _generate_master_data(env):
    env['viettelpost.service'].service_synchronous()
    env['viettelpost.service.extend'].service_extend_synchronous()
