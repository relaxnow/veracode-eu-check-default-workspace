# Veracode EU Check Default Workspace

Ce script Python interroge l'API Veracode (région Europe) pour identifier les applications liées à un espace de travail (workspace) spécifique au sein de Veracode Software Composition Analysis (SCA). Il génère des liens directs vers le centre d'analyse Veracode pour les applications nécessitant une correction.

## Prérequis

* Python 3
* [Pipenv](https://pipenv.pypa.io/en/latest/) pour la gestion des dépendances.
* Identifiants de l'API Veracode configurés sur votre machine (généralement dans le fichier `~/.veracode/credentials`).

## Installation

1. Clonez le dépôt :
   ```bash
   git clone [https://github.com/relaxnow/veracode-eu-check-default-workspace.git](https://github.com/relaxnow/veracode-eu-check-default-workspace.git)
   cd veracode-eu-check-default-workspace
   ```

2. Installez les dépendances (`requests` et `veracode-api-signing`) :
   ```bash
   pipenv install
   ```

## Utilisation

Pour exécuter le script en cherchant l'espace de travail par défaut ("Default Workspace") :
```bash
pipenv run python script.py
```

Pour spécifier un autre nom d'espace de travail, utilisez l'argument `-w` :
```bash
pipenv run python script.py -w "Nouveau Workspace"
```

Pour exécuter le script avec les journaux de débogage activés (utile pour voir les URL des requêtes et le JSON brut) :
```bash
pipenv run python script.py -d
```

## Arguments de ligne de commande

* `-w`, `--workspace` : Le nom de l'espace de travail à rechercher. La valeur par défaut est "Default Workspace".
* `-d`, `--debug` : Active le mode débogage pour afficher les requêtes API et vérifier pourquoi certains projets pourraient ne pas être détectés.

## Configuration des identifiants Veracode

Pour que le script puisse s'authentifier auprès de l'API Veracode, vous devez configurer vos identifiants sur votre machine locale.

1. Générez vos clés d'API depuis la plateforme Veracode (Dans le menu utilisateur : **API Credentials**).
2. Créez un dossier `.veracode` dans votre répertoire utilisateur :
   * **Linux / macOS :** `~/.veracode`
   * **Windows :** `%USERPROFILE%\.veracode`
3. Dans ce dossier, créez un fichier texte nommé `credentials` (sans aucune extension).
4. Ajoutez le contenu suivant en remplaçant les valeurs par vos propres clés :

   ```ini
   [default]
   veracode_api_key_id = VOTRE_ID_API
   veracode_api_key_secret = VOTRE_SECRET_API
   ```

**Note de sécurité :** Ne commitez jamais ce fichier d'identifiants dans votre dépôt Git.
