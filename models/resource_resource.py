from odoo import fields, models
from odoo.exceptions import UserError


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

    def _x_get_amenity_quantities(self, cleaning):
        """Kit effectif de la chambre pour un type de ménage.

        Kit du type de chambre (default_role_id), puis surcharges de la
        chambre : une ligne de la chambre remplace celle du même produit,
        une quantité à 0 le retire.

        :param cleaning: 'checkout' (départ) ou 'stayover' (séjour)
        :return: dict {product.product: quantité > 0}
        """
        self.ensure_one()
        qty_field = "qty_stayover" if cleaning == "stayover" else "qty_checkout"
        quantities = {
            line.product_id: line[qty_field]
            for line in self.default_role_id.x_amenity_line_ids
        }
        for line in self.x_amenity_line_ids:
            quantities[line.product_id] = line[qty_field]
        return {product: qty for product, qty in quantities.items() if qty > 0}

    def _x_latest_hk_task(self):
        """Tâche de ménage la plus récente de la chambre (le ménage du jour).

        booking_engine crée une tâche chaque nuit sans fermer les précédentes,
        et sa « tâche en cours » (x_ongoing_task_id) peut pointer vers une
        ancienne : on prend toujours la plus récente, même règle que
        project.task._x_is_superseded().
        """
        self.ensure_one()
        return self.env["project.task"].sudo().search([
            ("x_resource_id", "=", self.id),
            ("project_id.x_is_house_keeping_project", "=", True),
        ], order="id desc", limit=1)

    def action_open_amenity_supplement_wizard(self):
        """Produits supplémentaires depuis la fiche chambre : la demande est
        rangée dans le ménage le plus récent de la chambre."""
        self.ensure_one()
        task = self._x_latest_hk_task()
        if not task:
            raise UserError(
                f"La chambre {self.name} n'a encore aucune tâche de ménage : "
                "les produits supplémentaires se rattachent à un ménage."
            )
        return task.action_open_amenity_supplement_wizard()
