from odoo import fields, models


class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    x_amenity_location_id = fields.Many2one(
        "stock.location", string="Réserve produits d'accueil", copy=False,
        help="Armoire du ménage : les produits d'accueil y sont rangés (achat "
             "reçu directement ici, ou transfert depuis le stock principal) et "
             "en sortent à chaque ménage.",
    )

    def _x_amenity_reserve_location(self):
        """Réserve produits d'accueil de l'entrepôt, créée si elle n'existe
        pas encore (emplacement interne à côté de WH/Stock, pas dedans : les
        deux stocks se comptent séparément)."""
        self.ensure_one()
        if not self.x_amenity_location_id:
            self.sudo().x_amenity_location_id = self.env["stock.location"].sudo().create({
                "name": "Réserve produits d'accueil",
                "usage": "internal",
                "location_id": self.view_location_id.id,
                "company_id": self.company_id.id,
            })
        return self.x_amenity_location_id
