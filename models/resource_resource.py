from odoo import fields, models


class ResourceResource(models.Model):
    _inherit = "resource.resource"

    x_amenity_line_ids = fields.One2many(
        "pos.hotel.amenity.line", "resource_id",
        string="Produits d'accueil spécifiques",
        help="Surcharge du kit du type de chambre pour cette chambre : une ligne "
             "remplace celle du même produit, une quantité à 0 le retire.",
    )
    # Champs d'affichage uniquement (non stockés) : une condition invisible=""
    # ne peut pas suivre une relation, et la fiche montre le kit du type à
    # côté des surcharges de la chambre.
    x_is_hotel_room = fields.Boolean(
        related="default_role_id.x_is_a_room_offer", string="Est une chambre",
    )
    x_role_amenity_line_ids = fields.One2many(
        related="default_role_id.x_amenity_line_ids",
        string="Kit du type de chambre", readonly=True,
    )
