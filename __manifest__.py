{
    "name": "POS Hotel INTC - Produits d'accueil",
    "version": "19.0.1.0.6",
    "summary": "Kits de produits d'accueil par type de chambre, débités du stock au ménage",
    "description": """
Produits d'accueil des chambres (savon, shampoing, papier toilette...) :
- kit par type de chambre, avec surcharge possible par chambre ;
- quantités distinctes pour le ménage de départ et le ménage de séjour ;
- débit automatique du stock vers un emplacement de consommation quand la
  tâche de ménage passe à « Propre ».
""",
    "author": "INTC Madagascar",
    "website": "https://intc.mg",
    "category": "Inventory",
    "license": "LGPL-3",
    "depends": ["POS_HOTEL_INTC", "stock_account"],
    "data": [
        "security/ir.model.access.csv",
        "data/stock_location_data.xml",
        "views/planning_role_views.xml",
        "views/resource_resource_views.xml",
        "views/menu_views.xml",
        "views/amenity_supplement_wizard_views.xml",
        "views/project_task_views.xml",
    ],
    "post_init_hook": "post_init_hook",
    "installable": True,
    "application": False,
}
