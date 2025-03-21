import pandas
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.syntax import Syntax
from rich import print as rprint

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

    def definir_langage(self, alphabet):
        """Définit l'alphabet du langage"""
        self.langage = set(alphabet)

    def afficher(self):
        """Affiche les informations de l'automate"""
        console.print("États :", ", ".join(sorted(self.etats)), style="green")
        console.print("Alphabet :", ", ".join(sorted(self.langage)), style="green")
        console.print("États d'entrée :", ", ".join(sorted(self.entree)), style="green")
        console.print("États de sortie :", ", ".join(sorted(self.sortie)), style="green")

        table = Table(title="Transitions", show_header=True, header_style="bold magenta")
        table.add_column("État de départ", style="cyan")
        table.add_column("Symbole", style="yellow")
        table.add_column("États d'arrivée", style="green")

        for etat, trans in self.transition.items():
            for symbole, destinations in trans.items():
                table.add_row(str(etat), f"({symbole})" if symbole else "(ε)", ", ".join(sorted(destinations)))

        console.print(table)

        table_props = Table(title="Propriétés de l'automate", show_header=True, header_style="bold magenta")
        table_props.add_column("Propriété", style="cyan")
        table_props.add_column("Valeur", style="yellow")

        table_props.add_row("Déterministe", "✅ Oui" if self.est_deterministe() else "❌ Non")
        table_props.add_row("Complet", "✅ Oui" if self.est_complet() else "❌ Non")
        table_props.add_row("Standard", "✅ Oui" if self.est_standard() else "❌ Non")
        table_props.add_row("Déterministe & Complet", "✅ Oui" if self.est_deterministe_complet() else "❌ Non")
        table_props.add_row("Minimal", "✅ Oui" if self.minimal else "❌ Non")

        console.print(table_props)

    def afficher_tableau(self):
        """Affiche un tableau des transitions de l'automate"""
        console.print("Tableau de transitions:", style="bold blue")

        # Liste des colonnes pour l'affichage
        colonnes = ['Etat'] + sorted(self.langage)  # les set ne sont à la base pas trié

        # Préparer les données pour chaque état
        rows = []
        for etat in sorted(self.etats):
            ligne = [etat]
            for symbole in sorted(self.langage):
                # On récupère les états de transition pour ce symbole, s'il existe
                if etat in self.transition and symbole in self.transition[etat]:
                    ligne.append(', '.join(sorted(self.transition[etat][symbole])))
                else:
                    ligne.append('')  # Pas de transition
            rows.append(ligne)

        # Créer un DataFrame avec pandas
        df = pandas.DataFrame(rows, columns=colonnes)

        # Créer un tableau Rich à partir du DataFrame
        table = Table(title="Transitions par symbole")
        for col in df.columns:
            table.add_column(col, style="cyan" if col == "Etat" else "yellow")

        for _, row in df.iterrows():
            table.add_row(*[str(val) for val in row])

        console.print(table)

    def est_standard(self):
        if len(self.entree) > 1:
            self.standard = False
            return False
        else:
            for etat in self.transition:
                for symbole in self.transition[etat]:
                    # if (self.entree in self.transition[etat][symbole]):
                    setdEtat = self.transition[etat][symbole]
                    if (self.entree == setdEtat):
                        self.standard = False
                        return False
            self.standard = True
            return True

    def standardisation(self):
        console.print("Standardisation de l'automate...", style="bold blue")
        if (self.est_standard() == False):
            self.ajouter_etat('i')
            for entre in self.entree:
                if (entre in self.sortie) == True:
                    self.sortie.add('i')
                    for symbole in self.transition[entre]:
                        for transition in self.transition[entre][symbole]:
                            self.ajouter_transition('i', symbole, transition)
            self.entre = {'i'}
            self.standard = True
            console.print("L'automate a été standardisé avec succès.", style="green")
        else:
            console.print("L'automate est déjà standard.", style="yellow")

    def est_complet(self):
        if (len(self.entree) != 0):
            for etat in self.transition:
                for lettre in self.langage:
                    if (lettre in self.transition[etat]):
                        continue
                    else:
                        self.complet = False
                        return False
        self.complet = True
        return True

    def completion(self):
        console.print("Complétion de l'automate...", style="bold blue")
        if (len(self.entree) != 0) and (self.complet == False):
            self.ajouter_etat('P')
            for etat in self.etats:
                for lettre in self.langage:
                    if (etat not in self.transition):
                        self.ajouter_transition(etat, lettre, 'P')

                    if (lettre in self.transition[etat]):
                        continue
                    else:
                        self.ajouter_transition(etat, lettre, 'P')
            for lettre2 in self.langage:
                self.ajouter_transition('P', lettre2, 'P')
            console.print("L'automate a été complété avec succès.", style="green")
        else:
            console.print("L'automate est déjà complet.", style="yellow")

    def est_deterministe(self):
        if (len(self.entree) > 1):
            self.deterministe = False
            return False

        for etat, trans in self.transition.items():
            for symbole, SetEtat in trans.items():
                if len(SetEtat) > 1:
                    self.deterministe = False
                    return False
        self.deterministe = True
        return True

    def est_deterministe_complet(self):
        if (self.est_deterministe() == True) and (self.est_complet() == True):
            return True
        return False

    def complementaire(self):
        console.print("Calcul du complémentaire de l'automate...", style="bold blue")
        if (self.est_complet() == False):
            console.print("L'automate n'est pas complet, application de la complétion...", style="yellow")
            self.completion()
        SetT = set()
        SetNT = set()
        for etat in self.etats:
            if (etat not in self.sortie):
                SetT.add(etat)
            else:
                SetNT.add(etat)
        self.sortie = SetT
        console.print("Le complémentaire de l'automate a été calculé avec succès.", style="green")
        console.print(f"Nouveaux états de sortie : {', '.join(sorted(self.sortie))}", style="green")

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

    def minimisation(self):
        console.print("Minimisation de l'automate...", style="bold blue")
        if not self.est_deterministe_complet():
            console.print(
                "L'automate doit être déterministe et complet avant la minimisation.", style="yellow")
            if Confirm.ask("Voulez-vous déterminiser et compléter l'automate ?"):
                console.print("Déterminisation et complétion en cours...", style="blue")
                self.determinisation()
                self.completion()
            else:
                console.print("Minimisation annulée.", style="red")
                return

        # Étape 1 : Initialisation des partitions
        teta = [self.sortie, self.etats - self.sortie]
        teta = [p for p in teta if p]  # Éliminer les ensembles vides
        nom_partition = {}

        for i, groupe in enumerate(teta):
            nom = f"T{i + 1}" if groupe & self.sortie else f"NT{i + 1}"
            nom_partition[nom] = groupe

        console.print("Initialisation des partitions:", style="blue")
        for nom, groupe in nom_partition.items():
            console.print(f"{nom}: {{{', '.join(sorted(groupe))}}}", style="cyan")

        def modif_teta(teta, nom_partition):
            nouvelle_partition = []
            nouveau_nom_partition = {}

            for groupe in teta:
                sous_groupes = {}

                for etat in groupe:
                    signature = []
                    for symbole in sorted(self.langage):
                        if etat in self.transition and symbole in self.transition[etat]:
                            dest = next(iter(self.transition[etat][symbole]))
                            partition_idx = next((i for i, p in enumerate(teta) if dest in p), -1)
                            signature.append(partition_idx)
                        else:
                            signature.append(-1)

                    signature = tuple(signature)
                    if signature not in sous_groupes:
                        sous_groupes[signature] = set()
                    sous_groupes[signature].add(etat)

                nouvelle_partition.extend(sous_groupes.values())

            # Attribuer de nouveaux noms aux partitions
            for i, groupe in enumerate(nouvelle_partition):
                nom = f"T{i + 1}" if groupe & self.sortie else f"NT{i + 1}"
                nouveau_nom_partition[nom] = groupe

            return nouvelle_partition, nouveau_nom_partition

        # Étape 2 : Affinement successif
        ancienne_partition = []
        num_iteration = 0

        while sorted(map(frozenset, teta)) != sorted(map(frozenset, ancienne_partition)):
            console.print(f"Partition {num_iteration}:", style="blue")
            for nom, groupe in nom_partition.items():
                console.print(f"{nom}: {{{', '.join(sorted(groupe))}}}", style="cyan")

            ancienne_partition = teta.copy()
            teta, nom_partition = modif_teta(teta, nom_partition)
            num_iteration += 1

        console.print("Minimisation terminée. Automate minimal obtenu.", style="green")

        # Étape 3 : Construction de l'automate minimal
        automate_minimal = Automate()
        automate_minimal.definir_langage(self.langage)

        etat_mapping = {nom: set(p) for nom, p in nom_partition.items()}
        console.print("Correspondance des états de l'AFDC vers l'AFDCM:", style="blue")
        for nom, groupe in etat_mapping.items():
            console.print(f"État minimal {nom} correspond à {{{', '.join(sorted(groupe))}}}", style="cyan")

        for nom, groupe in etat_mapping.items():
            automate_minimal.ajouter_etat(nom, entree=any(e in self.entree for e in groupe),
                                          sortie=any(e in self.sortie for e in groupe))

        for nom, groupe in etat_mapping.items():
            etat_rep = next(iter(groupe))  # Prendre un état représentatif du groupe
            for symbole in sorted(self.langage):
                if etat_rep in self.transition and symbole in self.transition[etat_rep]:
                    dest = next(iter(self.transition[etat_rep][symbole]))
                    destination_nom = next((nom_dest for nom_dest, p in etat_mapping.items() if dest in p), None)
                    if destination_nom:
                        automate_minimal.ajouter_transition(nom, symbole, destination_nom)

        # Mise à jour de l'automate
        self.etats = automate_minimal.etats
        self.entree = automate_minimal.entree
        self.sortie = automate_minimal.sortie
        self.transition = automate_minimal.transition
        self.minimal = True

        console.print("Automate minimal obtenu et mis à jour.", style="green")
        return self


# --------------------------- CRÉATION DE L'AUTOMATE ---------------------------

automateFichier = "AutomateTest"

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
        elif str(i) in sorties_automate:
            automate.ajouter_etat(str(i), sortie=True)
        else:
            automate.ajouter_etat(str(i))

    for transition in (f[5:]):
        split  = transition.split("-")
        automate.ajouter_transition(split[0], split[1], split[2])

        
print("\nAutomate initial :")
automate.afficher_tableau()



# --------------------------- MENU INTERACTIF ---------------------------
def menu_interactif():
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


def menu_principal():
    """Affiche le menu principal"""
    automate = None

    while True:
        console.clear()
        console.print(Panel.fit("[bold cyan]Automates Finis[/bold cyan]", title="Menu Principal"))

        options = [
            "1. Créer un automate d'exemple",
            "2. Créer un automate personnalisé",
            "3. Afficher l'automate",
            "4. Afficher l'automate sous forme de tableau",
            "5. Vérifier si l'automate est standard",
            "6. Standardiser l'automate",
            "7. Vérifier si l'automate est complet",
            "8. Compléter l'automate",
            "9. Vérifier si l'automate est déterministe",
            "10. Calculer le complémentaire de l'automate",
            "11. Déterminiser l'automate",
            "12. Déterminiser un automate asynchrone",
            "13. Minimiser l'automate",
            "0. Quitter"
        ]

        for option in options:
            # Griser les options qui nécessitent un automate si aucun n'est chargé
            if automate is None and option[0] not in "120":
                console.print(option, style="dim")
            else:
                console.print(option, style="bold" if option[0] == "0" else "")

        choix = Prompt.ask("Entrez votre choix", choices=[str(i) for i in range(len(options))])

        if choix == "0":
            console.print("Au revoir !", style="bold green")
            break

        elif choix == "1":
            automate = creer_automate_exemple()
            console.print("Automate d'exemple créé avec succès !", style="bold green")
            automate.afficher()

        elif choix == "2":
            automate = creer_automate_personnalise()
            console.print("Automate personnalisé créé avec succès !", style="bold green")
            automate.afficher()

        elif choix == "3":
            if automate:
                automate.afficher()

        elif choix == "4":
            if automate:
                automate.afficher_tableau()

        elif choix == "5":
            if automate:
                est_standard = automate.est_standard()
                console.print(f"L'automate est {'standard' if est_standard else 'non standard'}.",
                              style="green" if est_standard else "yellow")

        elif choix == "6":
            if automate:
                automate.standardisation()
                automate.afficher()

        elif choix == "7":
            if automate:
                est_complet = automate.est_complet()
                console.print(f"L'automate est {'complet' if est_complet else 'non complet'}.",
                              style="green" if est_complet else "yellow")

        elif choix == "8":
            if automate:
                automate.completion()
                automate.afficher()

        elif choix == "9":
            if automate:
                est_deterministe = automate.est_deterministe()
                console.print(f"L'automate est {'déterministe' if est_deterministe else 'non déterministe'}.",
                              style="green" if est_deterministe else "yellow")

        elif choix == "10":
            if automate:
                automate.complementaire()
                automate.afficher()

        elif choix == "11":
            if automate:
                automate.determinisation()
                automate.afficher()

        elif choix == "12":
            if automate:
                automate.determinisation_asynchrone_synchrone()
                automate.afficher()

        elif choix == "13":
            if automate:
                automate.minimisation()
                automate.afficher()

if __name__ == "__main__":
    menu_principal()