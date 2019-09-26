# Balance_to_Excel_timer

### Transfert automatiquement � intervalle r�gulier la pes�e d'une balance vers un tableur Excel

## Pr�requis
* Windows 7+
* Balance de laboratoire �quip�e d'une connectique permettant d'envoyer une trame de donn�e sur un PC (test� sur des balances Sartorius, Mettler Toledo et Precisa)
* Balance programmable pour envoyer automatiquement une pes�e � intervalle r�gulier

## Installation
* Ex�cuter **/Installer/Output/Instal_Interface Balances - Excel - timer.exe**

## Utilisation
* Ouvrir le logiciel en mode administrateur
* Connecter la balance au PC via une c�ble s�rie ou avec convertisseur usb/s�rie
* V�rifier le com dans le gestionnaire de p�riph�rique (attention le driver doit �tre install� sur le PC)
* D�clarer une balance en cliquant sur le bouton "Edit config. balance" et renseigner les param�tres* de communication de la balance
* Ouvrir excel en mode administrateur
* Configurer les options du logiciel (sens de d�placement dans le fichier Excel, enregistrement automatique, forcer l'�criture de la cellule, etc.)
* Les pes�es cons�cutives de la balance sont inscrites dans les cases successives du tableur Excel

*Exemple param�tres d'une balance : Com = COM1, Baudrate = 1200, Parity = N (None/Even/Odd), Stopbits = 1, Timeout = 1, Xonxoff = 0, Rtscts = 0

## Programmation
* Python 2.7 - PyQt4 - cx_Freeze pour g�n�rer l'ex�cutable

## Auteur
* **C�dric PERROT** - INRA - (https://github.com/cperrot-inra)

## License
* Gratuit