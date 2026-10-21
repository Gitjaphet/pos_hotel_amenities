def post_init_hook(env):
    _create_amenity_reserves(env)


def _create_amenity_reserves(env):
    """Crée, pour chaque entrepôt existant, la réserve produits d'accueil et
    le type d'opération « Consommation ménage » (WH/HK/...), pour qu'ils
    apparaissent dès l'installation."""
    for warehouse in env["stock.warehouse"].search([]):
        warehouse._x_amenity_reserve_location()
        warehouse._x_amenity_picking_type()
