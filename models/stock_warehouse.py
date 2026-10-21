from odoo import fields, models


class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    x_amenity_location_id = fields.Many2one(
        "stock.location", string="Réserve produits d'accueil", copy=False,
        help="Armoire du ménage : les produits d'accueil y sont rangés (achat "
             "reçu directement ici, ou transfert depuis le stock principal) et "
             "en sortent à chaque ménage.",
    )
    x_amenity_picking_type_id = fields.Many2one(
        "stock.picking.type", string="Type d'opération des produits d'accueil", copy=False,
        help="Classeur des bons de ménage (WH/HK/...) : séparé des transferts "
             "internes du magasin.",
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

    def _x_amenity_picking_type(self):
        """Type d'opération « Consommation ménage » (code HK), créé s'il
        n'existe pas encore. Odoo génère la numérotation WH/HK/00001 à partir
        du code de séquence."""
        self.ensure_one()
        if not self.x_amenity_picking_type_id:
            consumption = self.env.ref(
                "pos_hotel_amenities.stock_location_room_consumption", raise_if_not_found=False
            )
            self.sudo().x_amenity_picking_type_id = self.env["stock.picking.type"].sudo().create({
                "name": "Consommation ménage",
                "code": "internal",
                "sequence_code": "HK",
                "warehouse_id": self.id,
                "company_id": self.company_id.id,
                "default_location_src_id": self._x_amenity_reserve_location().id,
                "default_location_dest_id": consumption.id if consumption else False,
            })
        return self.x_amenity_picking_type_id
