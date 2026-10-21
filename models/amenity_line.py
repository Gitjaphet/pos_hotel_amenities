from odoo import api, fields, models
from odoo.exceptions import ValidationError


class PosHotelAmenityLine(models.Model):
    """Un produit d'accueil et ses quantités par type de ménage.

    Rattachée SOIT à un type de chambre (kit standard, planning.role), SOIT à
    une chambre précise (surcharge, resource.resource). Au ménage, la ligne
    d'une chambre remplace celle du même produit dans le kit du type ; une
    quantité à 0 retire le produit pour cette chambre.
    """
    _name = "pos.hotel.amenity.line"
    _description = "Produit d'accueil de chambre"
    _order = "sequence, id"

    sequence = fields.Integer(default=10)
    role_id = fields.Many2one(
        "planning.role", string="Type de chambre",
        ondelete="cascade", index=True,
    )
    resource_id = fields.Many2one(
        "resource.resource", string="Chambre",
        ondelete="cascade", index=True,
    )
    product_id = fields.Many2one(
        "product.product", string="Produit", required=True,
        domain=[("is_storable", "=", True)],
        help="Seuls les produits dont l'inventaire est suivi peuvent être débités du stock.",
    )
    uom_id = fields.Many2one(related="product_id.uom_id", string="Unité")
    qty_checkout = fields.Float(
        string="Qté départ", default=1.0,
        help="Quantité débitée au ménage de départ (remise à neuf de la chambre).",
    )
    qty_stayover = fields.Float(
        string="Qté séjour", default=0.0,
        help="Quantité débitée au ménage de séjour (réassort). 0 = rien.",
    )

    @api.constrains("role_id", "resource_id")
    def _check_single_owner(self):
        for line in self:
            if bool(line.role_id) == bool(line.resource_id):
                raise ValidationError(
                    "Un produit d'accueil appartient soit à un type de chambre, "
                    "soit à une chambre précise — jamais aux deux, jamais à aucun."
                )

    @api.constrains("role_id", "resource_id", "product_id")
    def _check_no_duplicate(self):
        for line in self:
            owner = ("role_id", line.role_id.id) if line.role_id else ("resource_id", line.resource_id.id)
            if self.search_count([
                (owner[0], "=", owner[1]),
                ("product_id", "=", line.product_id.id),
                ("id", "!=", line.id),
            ]):
                raise ValidationError(
                    f"« {line.product_id.display_name} » figure déjà dans ce kit : "
                    "modifiez la ligne existante plutôt que d'en ajouter une seconde."
                )

    @api.constrains("qty_checkout", "qty_stayover")
    def _check_positive(self):
        for line in self:
            if line.qty_checkout < 0 or line.qty_stayover < 0:
                raise ValidationError("Les quantités ne peuvent pas être négatives.")
