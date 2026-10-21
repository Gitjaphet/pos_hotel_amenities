def migrate(cr, version):
    """Réserve produits d'accueil : créée pour les entrepôts des bases où le
    module était déjà installé (le post_init_hook ne se relance pas)."""
    from odoo import api, SUPERUSER_ID
    from odoo.addons.pos_hotel_amenities.hooks import _create_amenity_reserves

    _create_amenity_reserves(api.Environment(cr, SUPERUSER_ID, {}))
