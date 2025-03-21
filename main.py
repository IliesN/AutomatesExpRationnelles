import pandas

# --------------------------- CLASSE AUTOMATE ---------------------------
class Automate:
    def __init__(self):
        self.etats = set()  # Ensemble des états
        self.langage = set()  # Alphabet du langage
        self.entree = set()  # États d'entrée
        self.sortie = set()  # États de sortie
        self.transition = {}  # Dictionnaire des transitions (Dico de Dico de Set)
        self.complet = False
        self.standard = False
        self.deterministe = False
        self.minimal = False

    def ajouter_etat(self, etat, entree=False, sortie=False):
        """Ajoute un état à l'automate"""
        self.etats.add(etat)
        if entree:
            self.entree.add(etat)
        if sortie:
            self.sortie.add(etat)

    def ajouter_transition(self, etat_depart, symbole, etat_arrivee):
        """Ajoute une transition à l'automate"""
        if (etat_depart not in self.etats) or (etat_arrivee not in self.etats):
            raise ValueError("Les états doivent être ajoutés avant d'ajouter une transition.")
        if symbole != '' and symbole not in self.langage:
            raise ValueError("Le symbole doit appartenir au langage défini.")
        if etat_depart not in self.transition:
            self.transition[etat_depart] = {}
        if symbole in self.transition[etat_depart]:
            self.transition[etat_depart][symbole].add(etat_arrivee)
        else:
            self.transition[etat_depart][symbole] = {etat_arrivee}

    def definir_langage(self, alphabet):
        """Définit l'alphabet du langage"""
        self.langage = set(alphabet)

    def afficher(self):
        """Affiche les informations de l'automate"""
        print("États         :", self.etats)
        print("Alphabet      :", self.langage)
        print("États d'entrée:", self.entree)
        print("États de sortie:", self.sortie)
        print("Transitions   :")
        for etat, trans in self.transition.items():
            for symbole, destinations in trans.items():
                print(f"  {etat} --({symbole})--> {destinations}")
        print(f"- Déterministe            : {self.est_deterministe()}")
        print(f"- Complet                 : {self.est_complet()}")
        print(f"- Standard                : {self.est_standard()}")
        print(f"- Déterministe & Complet  : {self.est_deterministe_complet()}")

    def afficher_tableau(self):
        """Affiche un tableau des transitions de l'automate"""
        colonnes = ['Etat'] + sorted(self.langage)
        rows = []
        for etat in sorted(self.etats):
            ligne = [etat]
            for symbole in sorted(self.langage):
                if etat in self.transition and symbole in self.transition[etat]:
                    ligne.append(', '.join(sorted(self.transition[etat][symbole])))
                else:
                    ligne.append('')
            rows.append(ligne)
        df = pandas.DataFrame(rows, columns=colonnes)
        print(df)

    def est_standard(self):
        if len(self.entree) > 1:
            self.standard = False
            return False
        else:
            for etat in self.transition:
                for symbole in self.transition[etat]:
                    setdEtat = self.transition[etat][symbole]
                    if self.entree == setdEtat:
                        self.standard = False
                        return False
            self.standard = True
            return True

    def standardisation(self):
        if self.est_standard() == False:
            self.ajouter_etat('i')
            for entre in self.entree:
                if entre in self.sortie:
                    self.sortie.add('i')
                    for symbole in self.transition[entre]:
                        for transition in self.transition[entre][symbole]:
                            self.ajouter_transition('i', symbole, transition)
            self.entree = {'i'}
            self.standard = True

    def est_complet(self):
        if len(self.entree) != 0:
            for etat in self.transition:
                for lettre in self.langage:
                    if lettre in self.transition[etat]:
                        continue
                    else:
                        self.complet = False
                        return False
        self.complet = True
        return True

    def completion(self):
        if len(self.entree) != 0 and self.complet == False:
            self.ajouter_etat('P')
            for etat in self.etats:
                for lettre in self.langage:
                    if etat not in self.transition:
                        self.ajouter_transition(etat, lettre, 'P')
                    elif lettre not in self.transition[etat]:
                        self.ajouter_transition(etat, lettre, 'P')
            for lettre2 in self.langage:
                self.ajouter_transition('P', lettre2, 'P')

    def est_deterministe(self):
        if len(self.entree) > 1:
            self.deterministe = False
            return False
        for etat, trans in self.transition.items():
            for symbole, setEtat in trans.items():
                if len(setEtat) > 1:
                    self.deterministe = False
                    return False
        self.deterministe = True
        return True

    def est_deterministe_complet(self):
        if self.est_deterministe() and self.est_complet():
            return True
        return False

    def complementaire(self):
        if self.est_complet() == False:
            self.completion()
        SetT = set()
        SetNT = set()
        for etat in self.etats:
            if etat not in self.sortie:
                SetT.add(etat)
            else:
                SetNT.add(etat)
        self.sortie = SetT

    def determinisation(self):
        if self.est_deterministe():
            print("L'automate est déjà déterministe")
            return
        automate_deterministe = Automate()
        automate_deterministe.definir_langage(self.langage)
        etat_initial = "-".join(sorted(self.entree))
        automate_deterministe.ajouter_etat(etat_initial, entree=True)
        liste_etat_a_traiter = [self.entree]
        nouveaux_etats = {etat_initial: self.entree}
        while liste_etat_a_traiter:
            etats_courants = liste_etat_a_traiter.pop(0)
            nom_etat_courant = '-'.join(sorted(etats_courants))
            for charactere in self.langage:
                nouvel_etat = set()
                for etat in etats_courants:
                    if etat in self.transition and charactere in self.transition[etat]:
                        nouvel_etat.update(self.transition[etat][charactere])
                if nouvel_etat:
                    nom_nouvel_etat = '-'.join(sorted(nouvel_etat))
                    if nom_nouvel_etat not in nouveaux_etats:
                        automate_deterministe.ajouter_etat(nom_nouvel_etat)
                        nouveaux_etats[nom_nouvel_etat] = nouvel_etat
                        liste_etat_a_traiter.append(nouvel_etat)
                        if any(x in self.sortie for x in nouvel_etat):
                            automate_deterministe.sortie.add(nom_nouvel_etat)
                    automate_deterministe.ajouter_transition(nom_etat_courant, charactere, nom_nouvel_etat)
        self.etats = automate_deterministe.etats
        self.entree = automate_deterministe.entree
        self.sortie = automate_deterministe.sortie
        self.transition = automate_deterministe.transition
        self.deterministe = True
        if not self.est_complet():
            automate_deterministe.afficher_tableau()
            print("L'automate n'est pas complet\n")
            print("Complétion de l'automate")
            self.completion()
            print("Voici l'automate déterministe et complet")
            automate_deterministe.afficher_tableau()

    def fermeture_epsilon(self, etats):
        """Retourne la fermeture ε d'un ensemble d'états"""
        fermeture = set(etats)
        pile = list(etats)
        while pile:
            etat = pile.pop()
            if etat in self.transition and '' in self.transition[etat]:
                for e in self.transition[etat]['']:
                    if e not in fermeture:
                        fermeture.add(e)
                        pile.append(e)
        return fermeture

    def determinisation_asynchrone_synchrone(self):
        """
        Transforme un automate asynchrone en un automate synchrone en supprimant les transitions ε,
        puis applique la déterminisation.
        """
        print("Début de la transformation de l'automate asynchrone en synchrone...")
        fermeture_epsilon_dict = {etat: self.fermeture_epsilon({etat}) for etat in self.etats}
        automate_synchrone = Automate()
        automate_synchrone.definir_langage(self.langage)
        # Ajout de tous les états existants
        for etat in self.etats:
            automate_synchrone.ajouter_etat(
                etat,
                entree=(etat in self.entree),
                sortie=any(e in self.sortie for e in fermeture_epsilon_dict[etat])
            )
        # Ajout des transitions sans ε
        for etat in self.etats:
            for symbole in self.langage:
                nouveaux_etats = set()
                for e in fermeture_epsilon_dict[etat]:
                    if e in self.transition and symbole in self.transition[e]:
                        for destination in self.transition[e][symbole]:
                            # Correction : utiliser add() pour ajouter l'état entier
                            nouveaux_etats.add(destination)
                if nouveaux_etats:
                    for i in nouveaux_etats:
                        automate_synchrone.ajouter_transition(etat, symbole, i)
        print("Automate synchrone obtenu :")
        automate_synchrone.afficher_tableau()
        print("Début de la déterminisation de l'automate synchrone...")
        automate_synchrone.determinisation()
        self.etats = automate_synchrone.etats
        self.entree = automate_synchrone.entree
        self.sortie = automate_synchrone.sortie
        self.transition = automate_synchrone.transition
        self.deterministe = True
        print("Automate déterminisé avec succès.")
        if not self.est_complet():
            print("L'automate n'est pas complet, application de la complétion...")
            self.completion()
            print("Automate déterministe et complet obtenu :")
            self.afficher_tableau()

    def minimisation(self):
        if not self.est_deterministe_complet():
            print("L'automate doit être déterministe et complet avant la minimisation. Déterminisation et complétion en cours...")
            self.determinisation()
            self.completion()
        teta = [self.sortie, self.etats - self.sortie]
        nom_partition = {}
        for i, groupe in enumerate(teta):
            nom = f"T{i + 1}" if groupe & self.sortie else f"NT{i + 1}"
            nom_partition[nom] = groupe
        print("Initialisation des partitions:", nom_partition)
        def modif_teta(teta, nom_partition):
            nouvelle_partition = []
            nouveau_nom_partition = {}
            for groupe in teta:
                sous_groupes = {}
                for etat in groupe:
                    signature = tuple(
                        next((i for i, p in enumerate(teta) if self.transition.get(etat, {}).get(symbole) in p), -1)
                        for symbole in sorted(self.langage)
                    )
                    if signature not in sous_groupes:
                        sous_groupes[signature] = set()
                    sous_groupes[signature].add(etat)
                nouvelle_partition.extend(sous_groupes.values())
            for i, groupe in enumerate(nouvelle_partition):
                nom = f"T{i + 1}" if groupe & self.sortie else f"NT{i + 1}"
                nouveau_nom_partition[nom] = groupe
            return nouvelle_partition, nouveau_nom_partition
        ancienne_partition = []
        num_iteration = 0
        while teta != ancienne_partition:
            print(f"Partition {num_iteration}: {nom_partition}")
            ancienne_partition = teta
            teta, nom_partition = modif_teta(teta, nom_partition)
            num_iteration += 1
        print("Minimisation terminée. Automate minimal obtenu.")
        automate_minimal = Automate()
        automate_minimal.definir_langage(self.langage)
        etat_mapping = {nom: set(p) for nom, p in nom_partition.items()}
        print("Correspondance des états de l'AFDC vers l'AFDCM:")
        for nom, groupe in etat_mapping.items():
            print(f"État minimal {nom} correspond à {groupe}")
        for nom, groupe in etat_mapping.items():
            automate_minimal.ajouter_etat(nom, entree=any(e in self.entree for e in groupe),
                                          sortie=any(e in self.sortie for e in groupe))
        for nom, groupe in etat_mapping.items():
            for symbole in sorted(self.langage):
                destinations = set()
                for etat in groupe:
                    if etat in self.transition and symbole in self.transition[etat]:
                        destinations.update(self.transition[etat][symbole])
                destination_nom = next((nom_dest for nom_dest, p in etat_mapping.items() if destinations & p), None)
                if destination_nom is not None:
                    automate_minimal.ajouter_transition(nom, symbole, destination_nom)
        self.etats = automate_minimal.etats
        self.entree = automate_minimal.entree
        self.sortie = automate_minimal.sortie
        self.transition = automate_minimal.transition
        self.minimal = True
        print("Automate minimal obtenu et mis à jour.")
        return self

# --------------------------- CRÉATION DE L'AUTOMATE ---------------------------



automate = Automate()
automate.definir_langage(['a', 'b'])
automate.ajouter_etat('0', entree=True)
automate.ajouter_etat('1')
automate.ajouter_etat('2')
automate.ajouter_etat('3')
automate.ajouter_etat('4')
automate.ajouter_etat('5')
automate.ajouter_etat('6')
automate.ajouter_etat('7')
automate.ajouter_etat('8')
automate.ajouter_etat('9')
automate.ajouter_etat('10', sortie=True)
automate.ajouter_transition('0', '', '1')
automate.ajouter_transition('1', 'a', '2')
automate.ajouter_transition('2', 'b', '3')
automate.ajouter_transition('0', '', '1')  # Transition épsilon
automate.ajouter_transition('3', '', '10')  # Transition épsilon
automate.ajouter_transition('0', '', '4')   # Transition épsilon
automate.ajouter_transition('4', '', '5')   # Transition épsilon
automate.ajouter_transition('4', '', '8')   # Transition épsilon
automate.ajouter_transition('5', 'a', '6')   # Transition épsilon
automate.ajouter_transition('6', 'b', '7')   # Transition épsilon
automate.ajouter_transition('7', '', '5')    # Transition épsilon
automate.ajouter_transition('7', '', '8')    # Transition épsilon
automate.ajouter_transition('8', 'a', '9')    # Transition épsilon
automate.ajouter_transition('9', '', '10')    # Transition épsilon

print("\nAutomate initial :")
automate.afficher_tableau()

automateFichier = "AutomateTest"

automate2 = Automate()
with open ('Automates/' + automateFichier + ".txt") as f:
    f=f.read().splitlines()
    print(f)
    langage=[] # Ajout du langage
    for i in range(int(f[0])):
        langage.append(chr(97+i))
    automate2.definir_langage(langage)

    entrees_automate = f[2].split()[1:] # Vérification des états initiaux et terminaux
    sorties_automate = f[3].split()[1:]

    for i in range(int(f[1])): # Ajout des états 
        if str(i) in entrees_automate:
            automate2.ajouter_etat(str(i), entree=True)
        elif str(i) in sorties_automate:
            automate2.ajouter_etat(str(i), sortie=True)
        else:
            automate2.ajouter_etat(str(i))

    

        




# --------------------------- MENU INTERACTIF ---------------------------
def menu_interactif():
    while True:
        print("\n==== MENU INCROYABLE - GESTION DE L'AUTOMATE ====")
        print("1. Afficher l'automate actuel")
        print("2. Transformation asynchrone → synchrone et déterminisation")
        print("3. Afficher l'automate déterministe et complet")
        print("4. Minimiser l'automate")
        print("q. Quitter")
        choix = input("Entrez votre choix: ").strip()
        if choix == "1":
            print("\n--- Automate Actuel ---")
            automate.afficher_tableau()
            automate.afficher()
        elif choix == "2":
            print("\n--- Transformation asynchrone → synchrone et déterminisation ---")
            automate.determinisation_asynchrone_synchrone()
        elif choix == "3":
            print("\n--- Automate Déterministe et Complet ---")
            automate.afficher_tableau()
            automate.afficher()
        elif choix == "4":
            print("\n--- Minimisation de l'Automate ---")
            automate.minimisation()
        elif choix.lower() == "q":
            print("Au revoir !")
            break
        else:
            print("Choix invalide, veuillez réessayer.")

if __name__ == "__main__":
    menu_interactif()
