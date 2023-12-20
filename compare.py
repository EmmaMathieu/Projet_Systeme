
import os
import sys
import re
import parcourir


# echantillon_et_replicats ={   'P30': ['/home/emmamlinux/documents/Aide/Data/Data/P30/P30-1.trimed1000.sv_sniffles.vcf', 
#                                       '/home/emmamlinux/documents/Aide/Data/Data/P30/P30-2.trimed1000.sv_sniffles.vcf', 
#                                       '/home/emmamlinux/documents/Aide/Data/Data/P30/P30-3.trimed1000.sv_sniffles.vcf'], 
#                               'P15': ['/home/emmamlinux/documents/Aide/Data/Data/P15/P15-3.trimed1000.sv_sniffles.vcf', 
#                                       '/home/emmamlinux/documents/Aide/Data/Data/P15/P15-1.trimed1000.sv_sniffles.vcf', 
#                                       '/home/emmamlinux/documents/Aide/Data/Data/P15/P15-2.trimed1000.sv_sniffles.vcf']} 


def dictionnaire_final(echantillon_et_replicats) -> dict:  
    resultat_final = {}  # Initialise le dictionnaire final pour stocker les résultats par échantillon.

    # Crée un dictoinnaire a chaque échantillon .items() retourne une vue sur le dictionnaire qui est itérée.
    for echantillon, chemins_rep in echantillon_et_replicats.items():
        resultat_echantillon = {}

        # Pour chaque réplicat, il crée un nouveau dictionnaire
        for chemin_r in chemins_rep:
            valeurs_colonne_1_4 = {} 
            nom_fichier = chemin_r.split('/')[-1]  # Récupère le nom du fichier à partir du chemin complet.

            with open(chemin_r, 'r') as f:
                for ligne in f:
                    if ligne.startswith('#'):
                        continue

                    # Divise la ligne en colonnes en utilisant la tabulation comme séparateur.
                    colonne = ligne.split('\t')
                    # Récupère les valeurs des colonnes 1 et 4 en supprimant les espaces vides autour.
                    valeur_colonne_1, valeur_colonne_4 = colonne[1], colonne[4]
                    
                    # Vérifie si la valeur de la colonne 4 n'est pas '<DUP>', '<DEL>', ou '<INS>'.
                    if valeur_colonne_4 not in ('<DUP>', '<DEL>', '<INS>'):
                        # Si la valeur de la colonne 1 n'est pas déjà présente, crée une nouvelle entrée dans le dictionnaire.
                        if valeur_colonne_1 not in valeurs_colonne_1_4:
                            valeurs_colonne_1_4[valeur_colonne_1] = []
                        
                        # Ajoute la valeur de la colonne 4 à la liste correspondante dans le dictionnaire.
                        valeurs_colonne_1_4[valeur_colonne_1].append(valeur_colonne_4)
            
            # Associe les valeurs des colonnes 1 et 4 au nom du fichier.
            if valeurs_colonne_1_4:
                resultat_echantillon[nom_fichier] = valeurs_colonne_1_4

        # Modification des clés du dictionnaire final pour enlever les informations supplémentaires et rendre la sortie plus visible
        resultat_echantillon_modifie = {}
        for cle, valeur in resultat_echantillon.items():
            nouvelle_cle = cle.split('.')[0] if '.' in cle else cle
            resultat_echantillon_modifie[nouvelle_cle] = valeur
        
        if resultat_echantillon_modifie:
            resultat_final[echantillon] = resultat_echantillon_modifie

    return resultat_final

    


# resultat_final = {
#		'P30': {
#			'P30-1': {'22620': ['GTAGTAGTGGT'], '37879': ['TGTGGTG', 'TGTGTGTG', 'TGACAGAGAC']}, 
#			'P30-2': {'196282': ['TCTCTCTCAAA']}}, 
#		'P15': {
#			'P15-3': {'3243': ['TAATGTGATGGGCCTCGGCG'], '11375': ['GTAAGTACATCAATTAAGACAGAC']}, 
#			'P15-1': {'1210': ['TGTGATGTATTG'], '11375': ['GTAAGGTGTCCTCC']}, 
#			'P15-2': {'11375': ['GTAAGTACATCTGT']}}                                              
# }



def comparer_dictionnaires(resultat_final: dict,decalage,pourcentage) -> dict:
    comparaisons = {} 

    for echantillon, fichiers_valeurs in resultat_final.items():
        fichiers = list(fichiers_valeurs)  
       
        for i, fichier_1 in enumerate(fichiers):
            valeurs_1 = fichiers_valeurs[fichier_1]  

           
            for fichier_2 in fichiers[i + 1:]:
                valeurs_2 = fichiers_valeurs[fichier_2] 

                # Compte le nombre de clé identiques (à 10 nucléotides près) avec des valeurs avec un pourcentage d'identité superieur à 75%
                compteur_communs = sum(
                        1
                        for cle1, valeur1 in valeurs_1.items()
                        for cle2, valeur2 in valeurs_2.items()
                        for a, b in zip(valeur1, valeur2)
                        if abs(int(cle1) - int(cle2)) <= decalage and (sum(1 for a, b in zip(valeur1, valeur2) if a == b) / max(len(valeur1), len(valeur2))) * 100 >= pourcentage
                    )
                cle_comparaison = f"{fichier_1} - {fichier_2}"
                
                comparaisons[cle_comparaison] = compteur_communs
    return comparaisons  


# comparaisons = {  'P30-1 - P30-2': 0,
#                   'P30-1 - P30-3': 7, 
#                   'P30-2 - P30-3': 0, 
#                   'P15-3 - P15-1': 14, 
#                   'P15-3 - P15-2': 3, 
#                   'P15-1 - P15-2': 3       }  


def mise_en_forme(comparaisons: dict,str) -> None:
    print ("\n"+str)
    print("\n-----------------------Premier echantillon-----------------------")
    cles = list(comparaisons.keys())  # Extraction des clés du dictionnaire 'comparaisons' et conversion en liste

    for i, cle in enumerate(cles):
        print("le couple de réplicat : ", cle, "a un nombre de variant commun égal à : ", comparaisons[cle])
        # Trouve l'index du premier "-" dans la clé
        premier_tiret_cle = cle.index('-') if '-' in cle else len(cle)
        
        # Vérifie si ce n'est pas le dernier élément et si la sous-chaîne jusqu'au premier "-" est différente de la suivante
        if i < len(cles) - 1 and cle[:premier_tiret_cle] != cles[i + 1][:premier_tiret_cle]:
            print("\n-----------------------Echantillon suivant-----------------------")
            # Affiche une ligne de séparation entre les échantillons distincts



def main():

    chemin = sys.argv[1]

    if len(sys.argv) == 4: 
        decalage = int(sys.argv[2])
        pourcentage = int(sys.argv[3])
    elif len(sys.argv) == 3 :
        decalage = int(sys.argv[2])
        pourcentage = 100
    else : 
        decalage = 0
        pourcentage = 100
    
    echantillon_et_replicats = parcourir.parc(chemin)
    resultat = comparer_dictionnaires(dictionnaire_final(echantillon_et_replicats),decalage,pourcentage)
    mise_en_forme(resultat, "Bienvenue dans ce programme qui analyse le nombre de variants (par insertions connues) commun entre chaque réplicats deux à deux au sein d'un échantillon.\n")

if __name__ == "__main__": # Si la fonction sépciale s'appelle main alors il faut lancer la fonction main
    main() 


