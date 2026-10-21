def migrate(cr, version):
    """Type d'opération « Consommation ménage » (WH/HK/...) créé pour les
    entrepôts des bases où le module était déjà installé."""
    from odoo import api, SUPERUSER_ID
    from odoo.addons.pos_hotel_amenities.hooks import _create_amenity_reserves

    _create_amenity_reserves(api.Environment(cr, SUPERUSER_ID, {}))
