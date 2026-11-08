import random
import matplotlib.pyplot as plt

# ----------------------------------------------------------------------
# Données du problème
# ----------------------------------------------------------------------
CAPACITES = [20, 15, 35, 40, 15, 15, 10]          # MW par unité
DEMANDES = [80, 90, 65, 70]                       # MW par intervalle
CAPACITE_TOTALE = sum(CAPACITES)                  # 150 MW

# Gènes valides pour chaque unité (maintenance possible)
GENES_2_INTERVALLES = ["1100", "0110", "0011"]    # unités 1 et 2 (2 intervalles)
GENES_1_INTERVALLE = ["1000", "0100", "0010", "0001"]
GENES_VALIDES = [GENES_2_INTERVALLES] * 2 + [GENES_1_INTERVALLE] * 5

N_UNITES = len(CAPACITES)
N_INTERVALLES = len(DEMANDES)

# ----------------------------------------------------------------------
# Paramètres de l'AG
# ----------------------------------------------------------------------
TAILLE_POP = 6 * N_UNITES + 3      # ~ 6 à 7 fois le nombre de variables (=45)
N_GENERATIONS = 100
P_CROISEMENT = 0.8
P_MUTATION = 0.1                   # probabilité de muter un gène
TYPE_MUTATION = "inversion"        # "inversion" ou "remplacement"
ELITISME = True


# ----------------------------------------------------------------------
# Représentation / évaluation
# ----------------------------------------------------------------------
def creer_chromosome():
    """Un chromosome = liste de 7 gènes (chaînes de 4 bits)."""
    return [random.choice(g) for g in GENES_VALIDES]


def calculer_reserves(chrom):
    """Réserve = capacité totale - puissance en maintenance - demande."""
    reserves = []
    for i in range(N_INTERVALLES):
        perdue = sum(CAPACITES[u] for u in range(N_UNITES) if chrom[u][i] == "1")
        reserves.append(CAPACITE_TOTALE - perdue - DEMANDES[i])
    return reserves


def performance(chrom):
    """Plus petite réserve de l'année ; 0 si une réserve est négative."""
    return max(0, min(calculer_reserves(chrom)))


# ----------------------------------------------------------------------
# Sélection par loterie (roulette)
# ----------------------------------------------------------------------
def selection_loterie(population, perfs):
    total = sum(perfs)
    if total == 0:                               # aucun individu valide
        return random.choice(population)
    tirage = random.uniform(0, total)
    cumul = 0
    for chrom, p in zip(population, perfs):
        cumul += p
        if cumul >= tirage:
            return chrom
    return population[-1]


# ----------------------------------------------------------------------
# Croisement à un point (aux frontières des blocs de 4 bits)
# ----------------------------------------------------------------------
def croisement(p1, p2):
    if random.random() > P_CROISEMENT:
        return p1[:], p2[:]
    point = random.randint(1, N_UNITES - 1)
    return p1[:point] + p2[point:], p2[:point] + p1[point:]


# ----------------------------------------------------------------------
# Mutations (toujours sur des blocs de 4 bits => cédules toujours valides)
# ----------------------------------------------------------------------
def mutation_inversion(chrom):
    """Inverse l'ordre des bits d'un gène (ex: 1100 -> 0011, 1000 -> 0001).
    L'ensemble des gènes valides est stable par inversion, donc le
    résultat reste toujours une cédule logique."""
    enfant = chrom[:]
    for u in range(N_UNITES):
        if random.random() < P_MUTATION:
            enfant[u] = enfant[u][::-1]
    return enfant


def mutation_remplacement(chrom):
    """Remplace un gène par un autre gène valide (comme l'exemple du cours)."""
    enfant = chrom[:]
    for u in range(N_UNITES):
        if random.random() < P_MUTATION:
            enfant[u] = random.choice(GENES_VALIDES[u])
    return enfant


MUTATIONS = {"inversion": mutation_inversion, "remplacement": mutation_remplacement}


# ----------------------------------------------------------------------
# Boucle principale
# ----------------------------------------------------------------------
def algorithme_genetique(type_mutation=TYPE_MUTATION, verbose=True):
    mutation = MUTATIONS[type_mutation]
    population = [creer_chromosome() for _ in range(TAILLE_POP)]
    historique_best, historique_moy = [], []
    meilleur = max(population, key=performance)

    for gen in range(N_GENERATIONS):
        perfs = [performance(c) for c in population]
        best = population[perfs.index(max(perfs))]
        if performance(best) >= performance(meilleur):
            meilleur = best[:]
        historique_best.append(max(perfs))
        historique_moy.append(sum(perfs) / len(perfs))

        nouvelle_pop = [meilleur[:]] if ELITISME else []
        while len(nouvelle_pop) < TAILLE_POP:
            p1 = selection_loterie(population, perfs)
            p2 = selection_loterie(population, perfs)
            e1, e2 = croisement(p1, p2)
            nouvelle_pop.append(mutation(e1))
            if len(nouvelle_pop) < TAILLE_POP:
                nouvelle_pop.append(mutation(e2))
        population = nouvelle_pop

        if verbose and gen % 10 == 0:
            print(f"Génération {gen:3d} | meilleure = {historique_best[-1]:3d} MW "
                  f"| moyenne = {historique_moy[-1]:.1f} MW")

    return meilleur, historique_best, historique_moy


def afficher_solution(chrom):
    print("\n=== Meilleure cédule ===")
    for u, g in enumerate(chrom, start=1):
        intervalles = [str(i + 1) for i, b in enumerate(g) if b == "1"]
        print(f"Unité {u} ({CAPACITES[u-1]:2d} MW) : {g} -> maintenance aux intervalles "
              f"{', '.join(intervalles)}")
    reserves = calculer_reserves(chrom)
    for i, r in enumerate(reserves, start=1):
        print(f"Intervalle {i} : réserve = {r} MW")
    print(f"Performance (plus petite réserve) = {performance(chrom)} MW")


if __name__ == "__main__":
    random.seed(42)
    resultats = {}
    for type_mut in MUTATIONS:
        print(f"\n##### Mutation : {type_mut} #####")
        meilleur, hist_best, hist_moy = algorithme_genetique(type_mut)
        afficher_solution(meilleur)
        resultats[type_mut] = (hist_best, hist_moy)

    # Courbes de convergence
    plt.figure(figsize=(8, 5))
    for nom, (b, m) in resultats.items():
        plt.plot(b, label=f"Meilleure ({nom})")
        plt.plot(m, "--", label=f"Moyenne ({nom})")
    plt.xlabel("Génération")
    plt.ylabel("Réserve minimale (MW)")
    plt.title("Convergence de l'AG - cédule de maintenance")
    plt.legend()
    plt.grid(True)
    plt.savefig("convergence.png", dpi=120)
    plt.show()
