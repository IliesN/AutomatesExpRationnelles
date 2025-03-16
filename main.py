import pandas

# on importe la librairie pandas, car elle nous permet de créer des tableaux
# ce qui aide à mieux representé un tableau, en fait il permet d'étiquetter
# des variables sur les lignes et colonnes


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
        if (len(self.entree) == 0) or (entree == True):
            self.entree.add(etat)
        if (len(self.sortie) == 0) or (sortie == True):
            self.sortie.add(etat)

    def ajouter_transition(self, etat_depart, symbole, etat_arrivee):
        """Ajoute une transition à l'automate"""
        if (etat_depart not in self.etats) or (etat_arrivee not in self.etats):
            raise ValueError("Les états doivent être ajoutés avant d'ajouter une transition.")

        if symbole not in self.langage:
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
            for etat in self.transition:
                for lettre in self.langage:
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
        automate_deterministe= Automate()
        automate_deterministe.definir_langage(self.langage)

        etat_initial = "-".join(sorted(self.entree))
        automate_deterministe.ajouter_etat(etat_initial, entree=True)

        liste_etat_a_traiter = [self.entree]
        nouveaux_etats = {etat_initial : self.entree}

        while liste_etat_a_traiter :
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
                        liste_etat_a_traiter.append((nouvel_etat))

                        if any( x in self.sortie for x in nouvel_etat):
                            automate_deterministe.sortie.add(nom_nouvel_etat)


                    automate_deterministe.ajouter_transition(nom_etat_courant,charactere,nom_nouvel_etat)

        self.etats = automate_deterministe.etats
        self.entree = automate_deterministe.entree
        self.sortie = automate_deterministe.sortie
        self.transition= automate_deterministe.transition
        self.deterministe = True


        automate5.afficher_tableau()

        if not self.est_complet():
            automate5.afficher_tableau()
            print("L'automate n'est pas complet\n")
            print("complétion automate")
            self.completion()
            print("Voici l'automate deterministe et complet")
            automate5.afficher_tableau()






automate5 = Automate()
automate5.definir_langage({'a', 'b'})
automate5.ajouter_etat('0', entree=True)
automate5.ajouter_etat('1', entree=True)  # Deux états d'entrée (problème)
automate5.ajouter_etat('2')

automate5.ajouter_transition('0', 'a', '1')
automate5.ajouter_transition('1', 'b', '2')

print("Avant déterminisation :")
automate5.afficher_tableau()

automate5.determinisation()



