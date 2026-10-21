def migrate(cr, version):
    """Rattache à leur tâche les bons du kit créés avant le champ
    stock.picking.x_hk_task_id, pour qu'ils apparaissent dans l'onglet
    « Produits d'accueil » de la tâche."""
    from odoo import api, SUPERUSER_ID

    env = api.Environment(cr, SUPERUSER_ID, {})
    for task in env["project.task"].search([("x_amenity_picking_id", "!=", False)]):
        if not task.x_amenity_picking_id.x_hk_task_id:
            task.x_amenity_picking_id.x_hk_task_id = task
