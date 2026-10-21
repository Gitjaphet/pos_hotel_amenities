from odoo import fields, models
from odoo.exceptions import UserError


class PosHotelAmenitySupplementWizard(models.TransientModel):
    """Produits d'accueil supplémentaires demandés par un client pendant son
    séjour. Débit immédiat, à la charge de l'hôtel, rattaché à la tâche de
    ménage ; le kit de la chambre n'est jamais modifié."""
    _name = "pos.hotel.amenity.supplement.wizard"
    _description = "Produits d'accueil supplémentaires"

    task_id = fields.Many2one("project.task", string="Ménage", required=True, readonly=True, ondelete="cascade")
    room_id = fields.Many2one(related="task_id.x_resource_id", string="Chambre")
    line_ids = fields.One2many(
        "pos.hotel.amenity.supplement.wizard.line", "wizard_id", string="Produits",
    )

    def action_confirm(self):
        self.ensure_one()
        quantities = {}
        for line in self.line_ids.filtered(lambda l: l.quantity > 0):
            quantities[line.product_id] = quantities.get(line.product_id, 0) + line.quantity
        if not quantities:
            raise UserError("Ajoutez au moins un produit avec une quantité supérieure à 0.")
        task = self.task_id
        # Action volontaire : contrairement au kit automatique, une erreur de
        # configuration est affichée et rien n'est débité.
        warehouse, dest = task._x_amenity_locations()
        origin = f"Produits supplémentaires {task.x_resource_id.name}"
        picking = task._x_create_amenity_picking(warehouse, dest, quantities, origin)
        details = ", ".join(f"{p.display_name} × {q:g}" for p, q in quantities.items())
        task.message_post(body=f"Produits supplémentaires débités du stock : {picking.name} ({details}).")
        return {"type": "ir.actions.act_window_close"}


class PosHotelAmenitySupplementWizardLine(models.TransientModel):
    _name = "pos.hotel.amenity.supplement.wizard.line"
    _description = "Ligne de produit d'accueil supplémentaire"

    wizard_id = fields.Many2one(
        "pos.hotel.amenity.supplement.wizard", required=True, ondelete="cascade",
    )
    product_id = fields.Many2one(
        "product.product", string="Produit", required=True,
        domain=[("is_storable", "=", True)],
    )
    uom_id = fields.Many2one(related="product_id.uom_id", string="Unité")
    quantity = fields.Float(string="Quantité", default=1.0)
