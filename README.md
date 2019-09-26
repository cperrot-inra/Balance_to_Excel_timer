# Balance_to_Excel_timer

### Transfert automatiquement à intervalle régulier la pesée d'une balance vers un tableur Excel

## Prérequis
* Windows 7+
* Balance de laboratoire équipée d'une connectique permettant d'envoyer une trame de donnée sur un PC (testé sur des balances Sartorius, Mettler Toledo et Precisa)
* Balance programmable pour envoyer automatiquement une pesée à intervalle régulier

## Installation
* Exécuter **/Installer/Output/Instal_Interface Balances - Excel - timer.exe**

## Utilisation
* Ouvrir le logiciel en mode administrateur
* Connecter la balance au PC via une câble série ou avec convertisseur usb/série
* Vérifier le com dans le gestionnaire de périphérique (attention le driver doit être installé sur le PC)
* Déclarer une balance en cliquant sur le bouton "Edit config. balance" et renseigner les paramètres* de communication de la balance
* Ouvrir excel en mode administrateur
* Configurer les options du logiciel (sens de déplacement dans le fichier Excel, enregistrement automatique, forcer l'écriture de la cellule, etc.)
* Les pesées consécutives de la balance sont inscrites dans les cases successives du tableur Excel

*Exemple paramètres d'une balance : Com = COM1, Baudrate = 1200, Parity = N (None/Even/Odd), Stopbits = 1, Timeout = 1, Xonxoff = 0, Rtscts = 0

## Programmation
* Python 2.7 - PyQt4 - cx_Freeze pour générer l'exécutable

## Auteur
* **Cédric PERROT** - INRA - (https://github.com/cperrot-inra)

## License
* Gratuit