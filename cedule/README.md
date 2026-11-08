# Cédule de maintenance par algorithme génétique

Implémentation Python d'un algorithme génétique (AG) qui planifie la maintenance de 7 centrales électriques sur 4 intervalles de l'année, de façon à **maximiser la plus petite réserve de puissance**.

## Le problème

| Unité | Capacité (MW) | Intervalles de maintenance requis |
|-------|---------------|-----------------------------------|
| 1     | 20            | 2                                 |
| 2     | 15            | 2                                 |
| 3     | 35            | 1                                 |
| 4     | 40            | 1                                 |
| 5     | 15            | 1                                 |
| 6     | 15            | 1                                 |
| 7     | 10            | 1                                 |

- Capacité totale : 150 MW
- Demande par intervalle : 80, 90, 65 et 70 MW
- La maintenance d'une unité commence au début d'un intervalle et se termine à la fin d'un intervalle.
- La réserve de chaque intervalle doit rester supérieure à zéro.

**Réserve** = capacité totale − puissance en maintenance − demande

## Fonctionnement de l'AG

### Encodage
Un chromosome est composé de 7 gènes de 4 bits (un gène par unité). Chaque bit représente un intervalle : `1` = en maintenance, `0` = en service.

- Unités 1 et 2 : `1100`, `0110`, `0011`
- Unités 3 à 7 : `1000`, `0100`, `0010`, `0001`

Exemple : `0110 0011 0001 1000 0100 0010 1000`

### Fonction objective
La performance d'un chromosome est la **plus petite réserve** parmi les 4 intervalles. Si elle est négative, la performance est ramenée à 0.

### Opérateurs génétiques

| Opérateur | Méthode |
|-----------|---------|
| Sélection | **Loterie (roulette)**, probabilité proportionnelle à la performance |
| Croisement | À un point, aux frontières des blocs de 4 bits |
| Mutation | **Inversion** (par défaut) ou **remplacement** |
| Élitisme | Le meilleur individu est conservé à chaque génération |

**Mutation par inversion** : elle inverse l'ordre des bits d'un gène (`1100` → `0011`, `1000` → `0001`). L'ensemble des gènes valides est stable par cette opération, donc la cédule obtenue reste toujours logique.

**Mutation par remplacement** : elle remplace un gène par un autre gène valide de la même unité.

Les opérations se font toujours sur des blocs de 4 bits entiers, afin d'éviter les cédules illogiques ou fausses.



Le script exécute l'AG avec les deux types de mutation, affiche la meilleure cédule trouvée et enregistre les courbes de convergence dans "convergence.png".

## Exemple de résultat

Meilleur-Cedule.png

Les résultats varient d'une exécution à l'autre, car l'AG est stochastique. Le script fixe `random.seed(42)` pour obtenir des résultats reproductibles.


## Pistes d'amélioration

- Comparer d'autres méthodes de sélection (tournoi, rang) ou de croisement (à deux points, uniforme).
- Faire varier `P_MUTATION`, `P_CROISEMENT` et `TAILLE_POP`, puis comparer la convergence.
- Ajouter d'autres contraintes, comme les délais d'approvisionnement ou un nombre d'intervalles différent.
