def post_init_hook(env):
    _create_amenity_reserves(env)


def _create_amenity_reserves(env):
    """Crée la réserve produits d'accueil de chaque entrepôt existant, pour
    qu'elle apparaisse dès l'installation (achats reçus dedans, transferts)."""
    for warehouse in env["stock.warehouse"].search([]):
        warehouse._x_amenity_reserve_location()
