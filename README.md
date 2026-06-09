# xp2026
Feuilles d'expérience de la cohorte 2026


## Générateur de badges

Images tirées de https://twemoji.godi.se/#/

### Créer l'environnement Python local

```bash
python -m venv .python_env
```
### Activer l'environnement Python local

Windows :
```bash
.python_env\Scripts\Activate.ps1
```

macOS / Linux :
```bash
source .python_env/bin/activate
```

### Installer les paquets Python

```bash
pip install -r python_requirements.txt
```

### Générer les badges

La description des badges est dans le fichier `badges.csv`.

```bash
python generate_badges.py
```