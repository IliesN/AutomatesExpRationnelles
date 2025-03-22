from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm

console = Console()

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
        self.etats.add(etat)  # add fonction prédéfini permettant d'ajouter une valeur à un set
        if (entree == True):
            self.entree.add(etat)
        if (sortie == True):
            self.sortie.add(etat)

    def ajouter_transition(self, etat_depart, symbole, etat_arrivee):
        """Ajoute une transition à l'automate"""
        if (etat_depart not in self.etats) or (etat_arrivee not in self.etats):
            raise ValueError("Les états doivent être ajoutés avant d'ajouter une transition.")

        if symbole != '' and symbole not in self.langage:
            raise ValueError("Le symbole doit appartenir au langage défini.")

        if etat_depart not in self.transition:
            self.transition[etat_depart] = {}

        if symbole in self.transition[etat_depart]:  # Si le langage est déjà existante dans les transitions
            self.transition[etat_depart][symbole].add(etat_arrivee)
        else:  # Si le langage n'est pas présent alors on l'ajoute et on crée le set
            self.transition[etat_depart][symbole] = {etat_arrivee}

    # Méthode permettant de créer une copie d'une instance 
    def clone(self):
        """Crée une copie complète de l'automate."""
        copie = Automate()
        copie.etats = self.etats.copy()
        copie.langage = self.langage.copy()
        copie.entree = self.entree.copy()
        copie.sortie = self.sortie.copy()
        copie.transition = {etat: {symbole: destinations.copy() for symbole, destinations in trans.items()}
                            for etat, trans in self.transition.items()}
        copie.complet = self.complet
        copie.standard = self.standard
        copie.deterministe = self.deterministe
        copie.minimal = self.minimal
        return copie

    # Méthode permettant de minimiser l'automate
    def minimiser(self):
            print("Début de la minimisation de l'automate...")
            automate_minimal = self.clone()  # clonage de l'automate

            # Séparation Terminaux Non Terminaux
            print("\nCréation des partitions initiales...")
            etats_terminaux = {etat for etat in automate_minimal.sortie}
            etats_non_terminaux = automate_minimal.etats - etats_terminaux
            partitions = [etats_terminaux, etats_non_terminaux]

            print(f"Partitions initiales : {partitions}")

            while True:
                nouvelles_partitions = []
                correspondance = {}

                print("\nAffinement des partitions...")
                for groupe in partitions:  # Parcours des groupes/partitions
                    motifs = {}
                    # Motif = Ligne de transitions
                    for etat in groupe:
                        motif = tuple(
                            frozenset(
                                next((part for part in partitions if any(dest in part for dest in
                                                                         automate_minimal.transition.get(etat, {}).get(
                                                                             symbole, set()))), set())
                            )
                            for symbole in automate_minimal.langage
                        )


                        # Nouveaux groupes/partitions
                        if motif in motifs:
                            motifs[motif].add(etat)
                        else:
                            motifs[motif] = {etat}

                    nouvelles_partitions.extend(motifs.values())  # MAJ des nouvelles partitions

                print(f"\nNouvelles partitions : {nouvelles_partitions}")
                # Vérification pour condition d'arrêt
                if nouvelles_partitions == partitions:
                    break
                partitions = nouvelles_partitions
            # Nouvelle automate minimisé
            print("\nCréation de l'automate minimisé...")
            automate_minimal_final = Automate()
            automate_minimal_final.definir_langage(automate_minimal.langage)
            correspondance = {}

            # Fusion des états en créant des nouveaux états
            for i, groupe in enumerate(partitions):
                nouvel_etat = "".join(sorted(groupe))  # Utiliser les noms des états fusionnés
                automate_minimal_final.ajouter_etat(nouvel_etat, any(e in automate_minimal.entree for e in groupe),
                                                    any(e in automate_minimal.sortie for e in groupe))
                for e in groupe:
                    correspondance[e] = nouvel_etat

            print("\nMise à jour des transitions de l'automate minimisé...")
            for etat in automate_minimal.etats:
                if etat in correspondance:
                    for symbole, destinations in automate_minimal.transition.get(etat, {}).items():
                        if destinations:
                            automate_minimal_final.ajouter_transition(
                                correspondance[etat],
                                symbole,
                                correspondance[next(iter(destinations))]
                            )

            self.etats = automate_minimal_final.etats
            self.entree = automate_minimal_final.entree
            self.sortie = automate_minimal_final.sortie
            self.transition = automate_minimal_final.transition
            self.minimal = True

            print("\nAutomate minimisé avec succès !")
            self.afficher_tableau()
            return automate_minimal_final

    # Méthode permettant de definir le langage que l'on utilisera dans l'autmate
    def definir_langage(self, alphabet):
        """Définit l'alphabet du langage"""
        self.langage = set(alphabet)


    def afficher_tableau(self):
        """Affiche un tableau des transitions de l'automate"""
        console.print("Tableau de transitions:", style="bold blue")

        # Liste des colonnes pour l'affichage
        colonnes = ['Type', 'Etat'] + sorted(self.langage)  # Ajout de la colonne "Type"

        # Création du tableau Rich
        table = Table(title="Transitions par symbole")
        for col in colonnes:
            style_col = "cyan" if col in ["Etat", "Type"] else "yellow"
            table.add_column(col, style=style_col)

        # Ajouter les lignes avec les transitions
        for etat in sorted(self.etats):
            # Déterminer si l'état est d'entrée (E), de sortie (S) ou les deux (E/S)
            type_etat = ""
            if etat in self.entree and etat in self.sortie:
                type_etat = "E/S"
            elif etat in self.entree:
                type_etat = "E"
            elif etat in self.sortie:
                type_etat = "S"

            ligne = [type_etat, etat]  # Ajout du type d'état

            for symbole in sorted(self.langage):
                # On récupère les états de transition pour ce symbole, s'il existe
                if etat in self.transition and symbole in self.transition[etat]:
                    ligne.append(', '.join(sorted(self.transition[etat][symbole])))
                else:
                    ligne.append('')  # Pas de transition

            table.add_row(*map(str, ligne))  # Convertir en texte et ajouter au tableau

        console.print(table)

    # Méthode permettant d'afficher les informations de l'automate
    def afficher(self):
        """Affiche les informations de l'automate"""
        console.print("États :", ", ".join(sorted(self.etats)), style="green") ## le join pour relier des chaines de caracteres et le sorted
        # pour trier le set lors de l'ajout
        console.print("Alphabet :", ", ".join(sorted(self.langage)), style="green")
        console.print("États d'entrée :", ", ".join(sorted(self.entree)), style="green")
        console.print("États de sortie :", ", ".join(sorted(self.sortie)), style="green")

        self.afficher_tableau()

        table_props = Table(title="Propriétés de l'automate", show_header=True, header_style="bold magenta")
        table_props.add_column("Propriété", style="cyan")
        table_props.add_column("Valeur", style="yellow")

        table_props.add_row("Déterministe", "Oui" if self.est_deterministe() else "Non")
        table_props.add_row("Complet", "Oui" if self.est_complet() else "Non")
        table_props.add_row("Standard", "Oui" if self.est_standard() else "Non")
        table_props.add_row("Déterministe & Complet", "Oui" if self.est_deterministe_complet() else "Non")
        table_props.add_row("Minimal", "Oui" if self.minimal else "Non")

        console.print(table_props)

    # Méthode qui nous permet de savoir si l'automate est standard
    def est_standard(self):
        if len(self.entree) > 1: # si plusieurs entrées il n'est pas standard et on retourne false
            self.standard = False
            return False
        else: # sinon on verifie qu'il nous est impossible de revenir sur l'etat d'entrée
            for etat in self.transition:
                for symbole in self.transition[etat]:
                    # if (self.entree in self.transition[etat][symbole]):
                    setdEtat = self.transition[etat][symbole]
                    if (self.entree == setdEtat):
                        self.standard = False
                        return False
            self.standard = True
            return True

    # Méthode qui permet la standardisation de l'automate
    def standardisation(self):
        console.print("Standardisation de l'automate...", style="bold blue")
        if (self.est_standard() == False):
            self.ajouter_etat('i') # Ajout d'un etat i qui sera la nouvelle entrée
            for entre in self.entree:
                if (entre in self.sortie) == True:
                    self.sortie.add('i') # si une des entrées est une sortie alors i sera une sortie 
                    for symbole in self.transition[entre]:
                        for transition in self.transition[entre][symbole]:
                            self.ajouter_transition('i', symbole, transition) # boucle permettant d'ajouter les transitions des entrées à i
            self.entree = {'i'}
            self.standard = True
            console.print("L'automate a été standardisé avec succès.", style="green")
        else:
            console.print("L'automate est déjà standard.", style="yellow")

    # Méthode permettant de vérifier si un automate est complet
    def est_complet(self):
        if (len(self.entree) != 0):
            for etat in self.etats:
                for lettre in self.langage:
                    if (etat not in self.transition): # si etat n'est pas dans les transitions cela signifie qu'il n'est pas complet
                        return False
                    if (lettre in self.transition[etat]): # si lettre est dans les transitions alors cela signifie qu'il n'y a pas de prb pour l'instant
                        continue
                    else:
                        self.complet = False
                        return False
        self.complet = True
        return True

    # Méthode permettant de completer un automate
    def completion(self):
        console.print("Complétion de l'automate...", style="bold blue")
        if (len(self.entree) != 0) and (self.complet == False):
            self.ajouter_etat('P')
            for etat in self.etats:
                for lettre in self.langage:
                    if (etat not in self.transition):
                        self.ajouter_transition(etat, lettre, 'P') # Ajout d'une transition vers P, si n'existe aucune transition 
                        # d'un etat vers une autre pour une lettre du langage
                    if (lettre in self.transition[etat]):
                        continue
                    else:
                        self.ajouter_transition(etat, lettre, 'P') # si la lettre n'est pas dans les transitions alors on l'ajoute
            console.print("L'automate a été complété avec succès.", style="green")
        else:
            console.print("L'automate est déjà complet.", style="yellow")

    # Méthode permettant de savoir si un automate est determiniser.
    def est_deterministe(self):
        if (len(self.entree) > 1): # si plusieurs entrée alors il n'est pas determiniser
            self.deterministe = False
            return False

        for etat, trans in self.transition.items():
            for symbole, SetEtat in trans.items():
                if len(SetEtat) > 1: # si plusieurs etats dans une des transitions alors il n'est pas determiniser
                    self.deterministe = False
                    return False
        self.deterministe = True
        return True

    # Méthode qui nous permet de savoir si un automate est determinisé et complet
    def est_deterministe_complet(self):
        if (self.est_deterministe() == True) and (self.est_complet() == True):
            return True
        return False

    # Méthode renvoyons le complementaire d'un automate
    def complementaire(self):
        console.print("Calcul du complémentaire de l'automate...", style="bold blue")
        if (self.est_complet() == False):
            console.print("L'automate n'est pas complet, application de la complétion...", style="yellow")
            self.completion() # Pour complementer un automate il est necessaire qu'il soit fini / complet
        SetT = set()
        SetNT = set()
        for etat in self.etats:
            if (etat not in self.sortie):
                SetT.add(etat) # On ajoute les etats non sorties au noveau set sorties
            else:
                SetNT.add(etat) # sinon on ajoute les états sorties au non sorties
        self.sortie = SetT # on modifie le set precedent des sorties en l'initialisant avec le nouveau set 
        console.print("Le complémentaire de l'automate a été calculé avec succès.", style="green")
        console.print(f"Nouveaux états de sortie : {', '.join(sorted(self.sortie))}", style="green")

    # Méthode permettant de déterminiser
    def determinisation(self):
        console.print("Déterminisation de l'automate...", style="bold blue")
        if self.est_deterministe():
            console.print("L'automate est déjà déterministe.", style="yellow")
            return
        automate_deterministe = Automate()
        automate_deterministe.definir_langage(self.langage)

        etat_initial = "-".join(sorted(self.entree))  ## on fusionne les états entres en un seul chaine de caractere
        automate_deterministe.ajouter_etat(etat_initial, entree=True)

        liste_etat_a_traiter = [self.entree]  ## les états à traiter seront d'abord les entrées
        nouveaux_etats = {
            etat_initial: self.entree}  # On crée un dico avec clé nouvelle état entree et valeur les autres entres

        ## On fait une boucle qui s'arretera quand liste_etat_a_traiter sera vide
        while liste_etat_a_traiter:
            etats_courants = liste_etat_a_traiter.pop(0)  ## On supprime les états courants
            nom_etat_courant = '-'.join(sorted(etats_courants))

            # Parcourt tous les symboles de l'alphabet
            for charactere in self.langage:
                nouvel_etat = set()  # Ensemble pour stocker les états atteints

                # Vérifie les transitions possibles pour chaque état de l'ensemble actuel
                for etat in etats_courants:
                    if etat in self.transition and charactere in self.transition[etat]:
                        nouvel_etat.update(self.transition[etat][charactere])

                # Si un nouvel état est atteint avec ce caractère
                if nouvel_etat:
                    nom_nouvel_etat = '-'.join(sorted(nouvel_etat))

                    # Si ce nouvel état n'existe pas encore dans l'automate déterminisé, on l'ajoute
                    if nom_nouvel_etat not in nouveaux_etats:
                        automate_deterministe.ajouter_etat(nom_nouvel_etat)
                        nouveaux_etats[nom_nouvel_etat] = nouvel_etat
                        liste_etat_a_traiter.append((nouvel_etat))

                        # Vérifie si l'un des anciens états de ce nouvel état fusionné était un état de sortie
                        if any(x in self.sortie for x in nouvel_etat):
                            automate_deterministe.sortie.add(nom_nouvel_etat)

                    # Ajoute la transition correspondante dans le nouvel automate
                    automate_deterministe.ajouter_transition(nom_etat_courant, charactere, nom_nouvel_etat)

        # Mise à jour des attributs de l'automate actuel avec ceux de l'automate déterminisé
        self.etats = automate_deterministe.etats
        self.entree = automate_deterministe.entree
        self.sortie = automate_deterministe.sortie
        self.transition = automate_deterministe.transition
        self.deterministe = True

        console.print("L'automate a été déterminisé avec succès.", style="green")

        if not self.est_complet():
            automate_deterministe.afficher_tableau()
            console.print("L'automate n'est pas complet.", style="yellow")
            if Confirm.ask("Voulez-vous compléter l'automate ?"):
                console.print("Complétion de l'automate...", style="blue")
                self.completion()
                console.print("Voici l'automate déterministe et complet :", style="green")
                self.afficher_tableau()

    def fermeture_epsilon(self, etats):
        """Retourne la fermeture ε d'un ensemble d'états"""
        fermeture = set(etats)  # Initialisation avec les états donnés
        pile = list(etats)  # Utilisation d'une pile pour le parcours en profondeur

        while pile:
            etat = pile.pop()  # Récupérer un état de la pile
            if etat in self.transition and '' in self.transition[etat]:  # Vérifier s'il y a une transition ε
                for e in self.transition[etat]['']:  # Explorer les états atteignables via ε
                    if e not in fermeture:  # Ajouter uniquement les nouveaux états
                        fermeture.add(e)
                        pile.append(e)  # Ajouter à la pile pour exploration
        return fermeture

    def determinisation_asynchrone_synchrone(self):
        console.print("Transformation de l'automate asynchrone en synchrone puis déterminisation...", style="bold blue")

        # Étape 1 : Calcul de la fermeture ε pour chaque état de l'automate
        fermeture_epsilon = {etat: self.fermeture_epsilon({etat}) for etat in self.etats}

        # Création d'un nouvel automate sans transitions ε
        automate_synchrone = Automate()
        automate_synchrone.definir_langage(self.langage)  # Définir le même alphabet

        # Transférer les états en tenant compte de leur fermeture ε
        for etat in self.etats:
            automate_synchrone.ajouter_etat(etat,
                                            entree=(etat in self.entree),  # Conserver les entrées
                                            sortie=any(e in self.sortie for e in
                                                       fermeture_epsilon[etat]))  # Vérifier les sorties

        # Ajout des transitions sans transitions ε
        for etat in self.etats:
            for symbole in self.langage:
                nouveaux_etats = set()
                for e in fermeture_epsilon[etat]:  # Explorer chaque état atteignable par ε
                    if e in self.transition and symbole in self.transition[e]:  # Vérifier la transition par symbole
                        for destination in self.transition[e][symbole]:
                            nouveaux_etats.update(fermeture_epsilon[destination])  # Ajouter sa fermeture ε

                if nouveaux_etats:
                    for i in nouveaux_etats:  # Ajouter la transition si des états sont atteints
                        automate_synchrone.ajouter_transition(etat, symbole, i)

        console.print("Automate synchrone obtenu :", style="green")
        automate_synchrone.afficher_tableau()

        # Étape 2 : Appliquer la déterminisation sur l'automate synchrone
        console.print("Début de la déterminisation de l'automate synchrone...", style="blue")
        automate_synchrone.determinisation()

        # Mettre à jour l'automate actuel avec l'automate déterminisé
        self.etats = automate_synchrone.etats
        self.entree = automate_synchrone.entree
        self.sortie = automate_synchrone.sortie
        self.transition = automate_synchrone.transition
        self.deterministe = True  # L'automate est maintenant déterministe
        console.print("Automate déterminisé avec succès.", style="green")

        # Vérification de la complétude de l'automate
        if not self.est_complet():
            console.print("L'automate n'est pas complet.", style="yellow")
            if Confirm.ask("Voulez-vous compléter l'automate ?"):
                console.print("Application de la complétion...", style="blue")
                self.completion()  # Compléter l'automate si nécessaire
                console.print("Automate déterministe et complet obtenu :", style="green")
                self.afficher_tableau()


    def reconnaissanceMot(self, mots):
        """Vérifie quels mots d'une liste sont reconnus par l'automate."""
        resultats = {}
        liste_mots = mots.split()  # Séparer la chaîne en mots

        for mot in liste_mots:
            etats_actuels = set(self.entree)  # Initialisation correcte des états de départ

            for symbole in mot:
                nouveaux_etats = set()
                for etat in etats_actuels:
                    # Vérification si l'état actuel possède une transition pour le symbole
                    if etat in self.transition and symbole in self.transition[etat]:
                        nouveaux_etats.update(self.transition[etat][symbole])
                
                if not nouveaux_etats:  # Si aucun état n'est atteint, rejet du mot
                    resultats[mot] = False
                    break  
                
                etats_actuels = nouveaux_etats  # Mise à jour des états courants
            
            else:
                # Si on a fini de parcourir le mot, on regarde si on est dans un état final
                resultats[mot] = any(etat in self.sortie for etat in etats_actuels)

        return resultats
    

def creer_automate_personnalise():
    """Permet à l'utilisateur de créer un automate personnalisé"""
    automate = Automate()

    # Définition de l'alphabet
    alphabet_str = Prompt.ask("Entrez l'alphabet (séparé par des espaces)")
    alphabet = set(alphabet_str.split())
    automate.definir_langage(alphabet)

    # Ajout des états
    while True:
        etat = Prompt.ask("Entrez un état (ou 'fin' pour terminer)")
        if etat.lower() == 'fin':
            break

        entree = Confirm.ask(f"Est-ce que {etat} est un état d'entrée?")
        sortie = Confirm.ask(f"Est-ce que {etat} est un état de sortie?")

        automate.ajouter_etat(etat, entree=entree, sortie=sortie)

    # Ajout des transitions
    console.print("Ajout des transitions :", style="bold blue")
    console.print("Pour ajouter une transition epsilon, laissez le symbole vide", style="italic yellow")

    while True:
        console.print("États disponibles :", ", ".join(sorted(automate.etats)), style="cyan")
        console.print("Alphabet :", ", ".join(sorted(automate.langage)), style="cyan")

        depart = Prompt.ask("État de départ (ou 'fin' pour terminer)")
        if depart.lower() == 'fin':
            break

        if depart not in automate.etats:
            console.print(f"L'état {depart} n'existe pas!", style="bold red")
            continue

        symbole = Prompt.ask("Symbole (laissez vide pour epsilon)")
        if symbole and symbole not in automate.langage:
            console.print(f"Le symbole {symbole} n'appartient pas à l'alphabet!", style="bold red")
            continue

        arrivee = Prompt.ask("État d'arrivée")
        if arrivee not in automate.etats:
            console.print(f"L'état {arrivee} n'existe pas!", style="bold red")
            continue

        try:
            automate.ajouter_transition(depart, symbole, arrivee)
            console.print(f"Transition ajoutée : {depart} --({symbole or 'ε'})--> {arrivee}", style="green")
        except ValueError as e:
            console.print(f"Erreur : {str(e)}", style="bold red")

    return automate



# --------------------------- CRÉATION DE L'AUTOMATE ---------------------------

def lireFichier(automateFichier):
    automate = Automate()
    with open ('Automates/' + automateFichier + ".txt") as f:
        f=f.read().splitlines()
        langage=[] # Ajout du langage
        for i in range(int(f[0])):
            langage.append(chr(97+i))
        automate.definir_langage(langage)

        entrees_automate = f[2].split()[1:] # Vérification des états initiaux et terminaux
        sorties_automate = f[3].split()[1:]

        for i in range(int(f[1])): # Ajout des états
            if str(i) in entrees_automate:
                automate.ajouter_etat(str(i), entree=True)
            if str(i) in sorties_automate:
                automate.ajouter_etat(str(i), sortie=True)
            else:
                automate.ajouter_etat(str(i))

        for transition in (f[5:]):
            split  = transition.split("-")
            automate.ajouter_transition(split[0], split[1], split[2])
    return automate



# --------------------------- MENU INTERACTIF ---------------------------


def menu_principal():
    """Affiche le menu principal"""
    automate = None
    while True:
        console.print(Panel.fit("[bold cyan]Automates Finis[/bold cyan]", title="Menu Principal"))

        options = [
            "1. Sélectionner un automate",
            "2. Afficher l'automate",
            "3. Vérifier si l'automate est standard",
            "4. Standardiser l'automate",
            "5. Vérifier si l'automate est complet",
            "6. Compléter l'automate",
            "7. Vérifier si l'automate est déterministe",
            "8. Calculer le complémentaire de l'automate",
            "9. Déterminiser l'automate",
            "10. Déterminiser un automate asynchrone",
            "11. Minimiser l'automate",
            "12. Créer un automate personnalisée",
            "0. Quitter"
        ]

        for option in options:
            # Griser les options qui nécessitent un automate si aucun n'est chargé
            if automate is None and option[0] not in "120":
                console.print(option, style="dim")
            else:
                console.print(option, style="bold" if option[0] == "0" else "")

        choix = input("Entrez votre choix (0-" + str(len(options) - 1) + "): ")

        if choix == "0":
            console.print("Au revoir !", style="bold green")
            break

        elif choix == "1":
            choix = input("Veuillez entrer le nom du fichier correspondant : ")
            automate = lireFichier(choix)
            automate.afficher()

        elif choix == "2":
            if automate:
                automate.afficher()

        elif choix == "3":
            if automate:
                est_standard = automate.est_standard()
                console.print(f"L'automate est {'standard' if est_standard else 'non standard'}.",
                              style="green" if est_standard else "yellow")

        elif choix == "4":
            if automate:
                automate.standardisation()


        elif choix == "5":
            if automate:
                est_complet = automate.est_complet()
                console.print(f"L'automate est {'complet' if est_complet else 'non complet'}.",
                              style="green" if est_complet else "yellow")

        elif choix == "6":
            if automate:
                automate.completion()


        elif choix == "7":
            if automate:
                est_deterministe = automate.est_deterministe()
                console.print(f"L'automate est {'déterministe' if est_deterministe else 'non déterministe'}.",
                              style="green" if est_deterministe else "yellow")

        elif choix == "8":
            if automate:
                automate.complementaire()


        elif choix == "9":
            if automate:
                automate.determinisation()


        elif choix == "10":
            if automate:
                automate.determinisation_asynchrone_synchrone()


        elif choix == "11":
            if automate and automate.est_deterministe_complet():
                automate.minimiser()
            else:
                print("L'automate doit être deterministe et complet avant d'être minimisé")

        elif choix == "12":
            automate = creer_automate_personnalise()
            automate.afficher()

        elif choix == "13":
            listeMots = input("Veuillez entrer une liste de mots à essayer : ")
            print(automate.reconnaissanceMot(listeMots))

if __name__ == "__main__":
    menu_principal()
