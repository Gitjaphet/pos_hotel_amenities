from odoo import fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    x_hk_task_id = fields.Many2one(
        "project.task", string="Tâche de ménage",
        index=True, copy=False, readonly=True,
        help="Tâche de ménage pour laquelle ces produits d'accueil ont été "
             "débités (kit automatique ou produits supplémentaires).",
    )
