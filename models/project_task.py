import logging

from odoo import Command, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class ProjectTask(models.Model):
    _inherit = "project.task"

    x_amenity_picking_id = fields.Many2one(
        "stock.picking", string="Consommation produits d'accueil",
        readonly=True, copy=False,
        help="Transfert de stock créé quand ce ménage est passé à « Propre ». "
             "Rempli = déjà débité : un ménage n'est jamais débité deux fois.",
    )

    def write(self, vals):
        res = super().write(vals)
        if "stage_id" in vals:
            clean_stage = self.env.ref(
                "booking_engine.project_task_type_17", raise_if_not_found=False
            )
            if clean_stage and vals["stage_id"] == clean_stage.id:
                self.filtered(
                    lambda t: not t.x_amenity_picking_id
                    and t.x_resource_id
                    and t.project_id.x_is_house_keeping_project
                )._x_consume_amenities()
        return res

    def _x_consume_amenities(self):
        """Débite le kit de la chambre : WH/Stock -> Consommation chambres.

        Ne bloque JAMAIS le ménage : en cas d'échec, seul le débit est annulé
        (savepoint), la tâche reste « Propre » et le motif est posté dans son
        fil de discussion.
        """
        dest = self.env.ref(
            "pos_hotel_amenities.stock_location_room_consumption", raise_if_not_found=False
        )
        for task in self:
            room = task.x_resource_id
            cleaning = task.x_cleaning or "checkout"
            quantities = room._x_get_amenity_quantities(cleaning)
            if not quantities:
                continue
            label = "Séjour" if cleaning == "stayover" else "Départ"
            origin = f"Ménage {room.name} ({label})"
            try:
                with self.env.cr.savepoint():
                    if not dest:
                        raise UserError("Emplacement « Consommation chambres » introuvable.")
                    company = task.company_id or self.env.company
                    warehouse = self.env["stock.warehouse"].sudo().search(
                        [("company_id", "=", company.id)], limit=1
                    )
                    if not warehouse:
                        raise UserError(f"Aucun entrepôt pour la société {company.name}.")
                    picking = task._x_create_amenity_picking(warehouse, dest, quantities, origin)
                    task.x_amenity_picking_id = picking
                task.message_post(body=f"Produits d'accueil débités du stock : {picking.name} ({origin}).")
            except Exception as e:  # noqa: BLE001 — le ménage ne doit jamais être bloqué
                _logger.exception("pos_hotel_amenities : débit impossible pour %s", origin)
                task.message_post(body=f"⚠️ Débit des produits d'accueil impossible ({origin}) : {e}")

    def _x_create_amenity_picking(self, warehouse, dest, quantities, origin):
        """Crée et valide le transfert de consommation. Le stock peut devenir
        négatif : le comptage d'inventaire corrigera l'écart."""
        Move = self.env["stock.move"]
        src = warehouse.lot_stock_id
        move_cmds = []
        for product, qty in quantities.items():
            vals = {
                "product_id": product.id,
                "product_uom_qty": qty,
                "location_id": src.id,
                "location_dest_id": dest.id,
            }
            # Noms de champs variables selon les versions d'Odoo : renseignés
            # seulement s'ils existent.
            if "name" in Move._fields:
                vals["name"] = product.display_name
            if "product_uom" in Move._fields:
                vals["product_uom"] = product.uom_id.id
            move_cmds.append(Command.create(vals))
        picking = self.env["stock.picking"].sudo().with_company(warehouse.company_id).create({
            "picking_type_id": warehouse.int_type_id.id,
            "location_id": src.id,
            "location_dest_id": dest.id,
            "origin": origin,
            "move_ids": move_cmds,
        })
        picking.action_confirm()
        for move in picking.move_ids:
            move.quantity = move.product_uom_qty
            move.picked = True
        picking.with_context(skip_backorder=True, cancel_backorder=True, skip_sms=True).button_validate()
        if picking.state != "done":
            raise UserError(f"Le transfert {picking.name} n'a pas pu être validé (état : {picking.state}).")
        return picking
