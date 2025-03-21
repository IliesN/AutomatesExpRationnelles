import pandas


# on importe la librairie pandas, car elle nous permet de créer des tableaux
# ce qui aide à mieux representé un tableau, en fait il permet d'étiquetter
# des variables sur les lignes et colonnes


class Automate:
    def _init_(self):
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
        print("États :", self.etats)
        print("Alphabet :", self.langage)
        print("États d'entrée :", self.entree)
        print("États de sortie :", self.sortie)
        print("Transitions :")
        for etat, trans in self.transition.items():  # état prendra les clés du dico et
            # trans les valeurs de ces clés qui sont en soit un autre dico
            for symbole, destinations in trans.items():
                print(f"  {etat} --({symbole})--> {destinations}")
        print(f"- Déterministe            : {self.est_deterministe()}")
        print(f"- Complet                 : {self.est_complet()}")
        print(f"- Standard                : {self.est_standard()}")
        print(f"- Déterministe & Complet  : {self.est_deterministe_complet()}")

    def afficher_tableau(self):
        """Affiche un tableau des transitions de l'automate"""
        # Liste des colonnes pour l'affichage
        colonnes = ['Etat'] + sorted(self.langage)  # les set ne sont à la base pas trié
        # sorted permet de convertir un set en une liste trié

        # Préparer les données pour chaque état
        rows = []
        for etat in sorted(self.etats):
            ligne = [etat]
            for symbole in sorted(self.langage):
                # On récupère les états de transition pour ce symbole, s'il existe
                if etat in self.transition and symbole in self.transition[etat]:
                    ligne.append(', '.join(sorted(self.transition[etat][symbole])))
                    # join permet de produire une chaine de caractere, par exemple {q1, q2} en "q1, q2"
                else:
                    ligne.append('')  # Pas de transition
            rows.append(ligne)

        # Créer un DataFrame avec pandas
        df = pandas.DataFrame(rows, columns=colonnes)
        print(df)  # python reconnait directement le dataFrame d'une maniere speciale et imprime le tableau

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
        if (self.est_complet() == False):
            self.completion()
        SetT = set()
        SetNT = set()
        for etat in self.etats:
            if (etat not in self.sortie):
                SetT.add(etat)
            else:
                SetNT.add(etat)
        self.sortie = SetT

    def determinisation(self):
        if self.est_deterministe():
            print("l'automate est déjà determniste")
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

        if not self.est_complet():
            automate_deterministe.afficher_tableau()
            print("L'automate n'est pas complet\n")
            print("complétion automate")
            self.completion()
            print("Voici l'automate deterministe et complet")
            automate_deterministe.afficher_tableau()

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
        """
        Transforme un automate asynchrone en un automate synchrone en supprimant les transitions ε,
        puis applique la déterminisation.
        """
        print("Début de la transformation de l'automate asynchrone en synchrone...")

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
                            nouveaux_etats.update(destination)  # Ajouter sa fermeture ε

                if nouveaux_etats:
                    for i in nouveaux_etats:  # Ajouter la transition si des états sont atteints
                        automate_synchrone.ajouter_transition(etat, symbole, i)

        print("Automate synchrone obtenu :")
        automate_synchrone.afficher_tableau()

        # Étape 2 : Appliquer la déterminisation sur l'automate synchrone
        print("Début de la déterminisation de l'automate synchrone...")
        automate_synchrone.determinisation()

        # Mettre à jour l'automate actuel avec l'automate déterminisé
        self.etats = automate_synchrone.etats
        self.entree = automate_synchrone.entree
        self.sortie = automate_synchrone.sortie
        self.transition = automate_synchrone.transition
        self.deterministe = True  # L'automate est maintenant déterministe
        print("Automate déterminisé avec succès.")

        # Vérification de la complétude de l'automate
        if not self.est_complet():
            print("L'automate n'est pas complet, application de la complétion...")
            self.completion()  # Compléter l'automate si nécessaire
            print("Automate déterministe et complet obtenu :")
            self.afficher_tableau()

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

    def minimiser(self):
        print("Début de la minimisation de l'automate...")
        automate_minimal = self.clone() #clonage de l'automate

#Séparation Terminaux Non Terminaux
        print("\nCréation des partitions initiales...")
        etats_terminaux = {etat for etat in automate_minimal.sortie}
        etats_non_terminaux = automate_minimal.etats - etats_terminaux
        partitions = [etats_terminaux, etats_non_terminaux]

        print(f"Partitions initiales : {partitions}")

        while True:
            nouvelles_partitions = []
            correspondance = {}

            print("\nAffinement des partitions...")
            for groupe in partitions: #Parcours des groupes/partitions
                motifs = {}
                #Motif = Ligne de transitions
                for etat in groupe:
                    motif = tuple(
                        frozenset(
                            next((part for part in partitions if any(dest in part for dest in automate_minimal.transition.get(etat, {}).get(symbole, set()))), set())
                        )
                        for symbole in automate_minimal.langage
                    )

                    print(f"État {etat} -> Motif {motif}")
                    #Nouveaux groupes/partitions
                    if motif in motifs:
                        motifs[motif].add(etat)
                    else:
                        motifs[motif] = {etat}

                nouvelles_partitions.extend(motifs.values()) #MAJ des nouvelles partitions

            print(f"\nNouvelles partitions : {nouvelles_partitions}")
            #Vérification pour condition d'arrêt
            if nouvelles_partitions == partitions:
                break
            partitions = nouvelles_partitions
        #Nouvelle automate minimisé
        print("\nCréation de l'automate minimisé...")
        automate_minimal_final = Automate()
        automate_minimal_final.definir_langage(automate_minimal.langage)
        correspondance = {}

        #Fusion des états en créant des nouveaux états
        for i, groupe in enumerate(partitions):
            nouvel_etat = "".join(sorted(groupe))  # Utiliser les noms des états fusionnés
            automate_minimal_final.ajouter_etat(nouvel_etat, any(e in automate_minimal.entree for e in groupe), any(e in automate_minimal.sortie for e in groupe))
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


automate = Automate()

    # Définition de l'alphabet
automate.definir_langage({'a', 'b'})

    # Ajout des états
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


    # Ajout des transitions
automate.ajouter_transition('0', '', '1')
automate.ajouter_transition('1', 'a', '2')
automate.ajouter_transition('2', 'b', '3')
automate.ajouter_transition('0', '', '1')  # Transition épsilon
automate.ajouter_transition('3', '', '10')  # Transition épsilon
automate.ajouter_transition('0', '', '4')  # Transition épsilon
automate.ajouter_transition('4', '', '5')  # Transition épsilon
automate.ajouter_transition('4', '', '8')  # Transition épsilon
automate.ajouter_transition('5', 'a', '6')  # Transition épsilon
automate.ajouter_transition('6', 'b', '7')  # Transition épsilon
automate.ajouter_transition('7', '', '5')  # Transition épsilon
automate.ajouter_transition('7', '', '8')  # Transition épsilon
automate.ajouter_transition('8', 'a', '9')  # Transition épsilon
automate.ajouter_transition('9', '', '10')  # Transition épsilon


# Affichage de l'automate initial
print("\nAutomate initial :")
automate.afficher_tableau()

# Transformation en automate déterministe et complet
print("\nTransformation de l'automate :")
automate.determinisation_asynchrone_synchrone()

# Affichage de l'automate déterminisé et complété
print("\nAutomate déterministe et complet :")
automate.afficher_tableau()

automate.minimiser()
