# POS Hotel Amenities

Module Odoo 19 de gestion des **produits d'accueil des chambres** (savon, shampoing, papier toilette, eau…).

Chaque type de chambre a son **kit**. Quand la femme de chambre passe le ménage à **« Propre »**, le kit est **débité du stock automatiquement**. Plus besoin de compter à la main ce qui est sorti de la réserve.

Complément du module [POS_HOTEL_INTC](https://github.com/Gitjaphet/POS_HOTEL_INTC).

![Odoo 19](https://img.shields.io/badge/Odoo-19.0-714B67)
![Python](https://img.shields.io/badge/Python-3.11-3776AB)
![Inventory](https://img.shields.io/badge/Odoo-Inventory-875A7B)
![License](https://img.shields.io/badge/License-LGPL--3-blue)

## Fonctionnalités

### Kits de produits d'accueil
- Un **kit par type de chambre** (Chambre Double, Suite…).
- **Surcharge par chambre** : une ligne sur la chambre remplace celle du kit ; une quantité à **0 retire** le produit.
- **Deux quantités** par produit :
  - **Qté départ** : ménage complet après le départ du client ;
  - **Qté séjour** : ménage pendant le séjour (souvent moins de produits).

### Débit automatique au ménage
- La tâche de ménage passe à **« Propre »** → un bon de sortie est créé : **Réserve produits d'accueil → Consommation chambres**.
- Le bon est lié à la tâche et visible dans l'onglet **« Produits d'accueil »**.
- Le message de suivi de la tâche indique ce qui a été débité.

### Produits supplémentaires
- Bouton **« Produits supplémentaires »** sur la tâche de ménage et sur la chambre.
- Pour une demande imprévue du client (serviette en plus, eau…), sans modifier le kit.

### Sécurités
- **Le ménage n'est jamais bloqué** : si le débit échoue (stock mal configuré…), la tâche reste « Propre » et le motif est écrit dans son fil de discussion.
- **Pas de double débit** : une tâche déjà débitée ne l'est pas une deuxième fois.
- **Anciennes tâches ignorées** : si une tâche plus récente existe pour la même chambre, l'ancienne ne débite rien (évite de débiter des ménages vieux de plusieurs semaines en fermant un arriéré).

### Comptabilité
- L'emplacement **Consommation chambres** est valorisé sur le compte **602100**, donc chaque sortie de stock passe en charge.

## Prérequis

| Élément | Détail |
|---|---|
| Odoo | 19.0 |
| Modules requis | [`POS_HOTEL_INTC`](https://github.com/Gitjaphet/POS_HOTEL_INTC), `stock_account` |
| Indirectement | `booking_engine` / `hotel` (industrie Hôtel d'Odoo), `project` |

## Installation

```bash
# 1. Cloner le module dans le dossier des addons personnalisés
cd /chemin/vers/vos/addons
git clone https://github.com/Gitjaphet/pos_hotel_amenities.git

# 2. Ajouter ce dossier à addons_path dans odoo.conf, puis redémarrer Odoo

# 3. Installer le module (ou depuis Applications, après mise à jour de la liste)
python odoo-bin -c odoo.conf -d <base> -i pos_hotel_amenities --stop-after-init
```

À l'installation, pour chaque entrepôt, le module crée :
- l'emplacement interne **« Réserve produits d'accueil »** (séparé de WH/Stock) ;
- le type d'opération **« Consommation ménage »** (numérotation `WH/HK/00001`).

## Configuration

1. **Stock** : mettre les produits d'accueil dans **Réserve produits d'accueil** (réception ou transfert interne depuis WH/Stock).
2. **Kits** : application **Hôtel**, menu des chambres → **Kits produits d'accueil** → ouvrir un type de chambre → ajouter les produits avec leurs quantités départ / séjour.
3. **Chambre particulière** (facultatif) : ouvrir la chambre → section **Produits d'accueil** → **Spécifique à cette chambre**.

## Structure du dépôt

```
pos_hotel_amenities/
├── models/
│   ├── amenity_line.py      Ligne de kit (type de chambre OU chambre, qté départ / séjour)
│   ├── planning_role.py     Kit du type de chambre
│   ├── resource_resource.py Surcharges par chambre, calcul du kit effectif
│   ├── project_task.py      Débit du stock quand le ménage passe à « Propre »
│   ├── stock_warehouse.py   Réserve et type d'opération par entrepôt
│   └── stock_picking.py     Lien bon de sortie ↔ tâche de ménage
├── wizards/                 Produits supplémentaires
├── views/                   Kits, chambre, tâche de ménage, menu
├── data/                    Emplacement « Consommation chambres »
├── migrations/              Scripts de mise à jour
├── security/                Droits d'accès
└── hooks.py                 Création des réserves à l'installation
```

## Déploiement

Chaque `push` sur `main` lance GitHub Actions (test → build → deploy). Sur le serveur, le module est mis à jour sur **toutes les bases** où il est installé, avec une sauvegarde avant et un retour en arrière automatique si une base échoue.

Après une modification de vue ou de champ, faire **Mettre à jour** le module dans Applications.

## Auteur

Développé par **Japhet Valeureux BEZANAKA** pour [INTC Madagascar](https://intc.mg).

Licence : LGPL-3.
