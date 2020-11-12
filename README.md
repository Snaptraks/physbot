# PhysBot

Bot pour le serveur Discord de la [PHYSUM](http://www.aephysum.umontreal.ca/).

## Description

Ce projet est un bot custom fait expressément pour le serveru Discord de la PHYSUM, avec des fonctions à la fois de divertissement pour les membres et de gestion du serveur pour les administrateurs.
Il se veut un projet ouvert à tous, où les personnes qui veulent s'initier à la programmation intermédiaire à avancée en Python.

## Comment contribuer

Contribuer au projet peut se faire de multiples façons:

- Écrire des suggestions d'ajouts ou modifications dans les [Issues](https://github.com/Snaptraks/physbot/issues)
- Signaler des bugs, encore une fois dans les [Issues](https://github.com/Snaptraks/physbot/issues)
- Apporter vos propres modifications à l'aide de [Pull Requests](https://github.com/Snaptraks/physbot/pulls)

Pour contribuer au niveau du code, il va être nécessaire de pouvoir exécuter le bot sur votre propre ordinateur.
La section qui suit détaille le processus à suivre.

### Dépendances
Avant tout, pour pouvoir exécuter le bot, il vous faut Python 3.8+ ainsi que les modules énumérés dans `requirements.txt`.

Il est possible d'installer rapidement tous les modules avec la commande `pip install -r requirements.txt`
Il est recommandé de créer un environement virtuel pour le bot (voir [le guide conda](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html), par exemple).
Il est possible de vérifier l'installation avec la commande `python -m discord.py -v` qui devrait retourner un message similaire:
```
- Python v3.8.5-final
- discord.py v1.5.1-final
- aiohttp v3.6.2
- system info: Windows 10 10.0.19041
```
Il est désormais possible de cloner le code dans le répertoire de votre choix.

### Exécuter le bot localement
Une fois que les modules sont bien installés, suivez la merche à suivre pour créer votre propre bot:

1. [Créer un compte bot](https://discordpy.readthedocs.io/en/latest/discord.html#creating-a-bot-account).
2. Copier le "token" secret de votre bot dans un fichier appellé `config.py` sous la variable `token` (voire `config.py.example` pour plus de détails).
3. [Inviter le bot dans votre serveur](https://discordpy.readthedocs.io/en/latest/discord.html#inviting-your-bot). Je recommande de créer un serveur dédié à ceci, afin de vois assurer d'avoir le contrôle total du bot (et de ses permissions).
4. Démarrer le bot avec `python PhysBot.py` à partir d'un terminal (il est probable que d'autres méthodes fonctionnent, comme par PyCharm ou Spyder, mais elles n'ont pas été testées).
