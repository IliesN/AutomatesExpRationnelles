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
