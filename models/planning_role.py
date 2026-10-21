from odoo import fields, models


class PlanningRole(models.Model):
    _inherit = "planning.role"

    x_amenity_line_ids = fields.One2many(
        "pos.hotel.amenity.line", "role_id",
        string="Produits d'accueil",
        help="Kit standard débité au ménage de toute chambre de ce type.",
    )
