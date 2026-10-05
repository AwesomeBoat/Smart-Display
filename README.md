# Smart Display

*[English below](#english)*

> **Projet en cours de réalisation.**

Un écran chez moi qui ne se contente pas d'afficher l'heure et la météo, mais qui connaît
mes données et s'en sert.

## La vision

Aujourd'hui, mes données sont éparpillées : l'agenda dans Google, les tâches et habitudes
ici, et tout le reste dans [Chronicle](https://github.com/AwesomeBoat/Chronicle), mon autre
projet qui collecte en continu mon sommeil, mon rythme cardiaque, mon sport, ce que je
mange, la température de ma chambre, mon temps d'écran, les films que je regarde et ce que
je lis (quoi, quand, combien de temps, à quelle vitesse).

L'idée est de relier tout ça, d'entraîner des modèles de machine learning dessus, et
d'ajouter une couche intelligente qui interprète ce qu'ils trouvent. L'écran devient
l'endroit où cette couche me parle. Quelques exemples de ce qu'elle pourrait faire :

- **Le matin** : *« Tu as dormi 5h40 et ta journée est chargée jusqu'à 18h. Je décale le
  sport de ce soir à demain matin ? »*
- **Le soir** : *« Couche-toi à 22h50 ce soir. C'est l'heure à laquelle tu as le plus de
  sommeil profond, d'après tes 6 derniers mois. »* Pas une règle trouvée sur internet,
  une heure apprise sur moi, qui s'ajuste quand mes habitudes changent.
- **Le prix de mes écrans** : *« Une heure de film le soir te coûte en moyenne 20 minutes de
  sommeil. Une heure de lecture t'en fait gagner 10. »*
- **Avant les symptômes** : *« Ton cœur au repos monte depuis deux nuits et ta variabilité
  cardiaque baisse, alors que rien dans ta journée ne l'explique. C'est le même schéma
  qu'avant ta grippe de mars. Tu couves peut-être quelque chose : journée légère ? »*
- **Des expériences sur moi-même** : je lui dis *« je teste : pas d'écran après 22h pendant
  deux semaines »*. Il suit l'expérience, compare avec avant, et me donne le verdict chiffré.
- **Poser n'importe quelle question** depuis le téléphone, comme *« Est-ce que je dors mieux
  les jours où je fais du sport ? »*, et avoir une réponse tirée de mes propres données.

Rien de tout ça ne vient de conseils génériques : tout est appris sur mes données, avec des
années d'historique.

## Où en est le projet

Ce qui fonctionne déjà : l'écran affiche l'heure, la météo, l'agenda, les tâches et les
habitudes, mis à jour en temps réel. Tout se pilote depuis le téléphone, et chaque personne
de la maison a son profil.

Prochaines étapes : installation sur un Raspberry Pi, branchement sur Chronicle, puis la
couche intelligente.

Python, FastAPI, SQLite, Server-Sent Events, HTML/JS sans framework.

## Lancer le projet

Créer un `.env` avec `LAT` et `LON` (position pour la météo), puis :

```bash
uv sync
uv run uvicorn main:app --host 0.0.0.0 --port 8000
```

L'écran est sur `/display_dashboard`, la télécommande sur `/phone`.

---

## English

> **Work in progress.**

A screen at home that doesn't just show the time and the weather, but knows my data and
uses it.

### The vision

My data is scattered today: my calendar in Google, tasks and habits here, and everything else
in [Chronicle](https://github.com/AwesomeBoat/Chronicle), my other project that continuously
collects my sleep, heart rate, workouts, meals, bedroom temperature, screen time, the movies
I watch and what I read (what, when, for how long, how fast).

The idea is to connect all of it, train machine learning models on it, and add an
intelligent layer that interprets what they find. The screen becomes the place where that
layer talks to me. A few examples of what it could do:

- **In the morning**: *"You slept 5h40 and your day is packed until 6pm. Move tonight's
  workout to tomorrow morning?"*
- **In the evening**: *"Go to bed at 10:50pm tonight. That's when you get the most deep
  sleep, based on your last 6 months."* Not a rule found online, a time learned on me, that
  adjusts when my habits change.
- **The cost of my screens**: *"One hour of movie in the evening costs you 20 minutes of
  sleep on average. One hour of reading gives you 10 back."*
- **Before the symptoms**: *"Your resting heart rate has been rising for two nights and your
  heart rate variability is dropping, with nothing in your days to explain it. Same pattern
  as before your flu in March. You might be coming down with something: light day?"*
- **Experiments on myself**: I tell it *"I'm testing no screens after 10pm for two weeks"*.
  It tracks the experiment, compares with before, and gives me the verdict in numbers.
- **Ask anything** from the phone, like *"Do I sleep better on days I work out?"*, and get
  an answer drawn from my own data.

None of this comes from generic advice: everything is learned on my data, with years of
history behind it.

### Where it stands

Working today: the screen shows the time, weather, calendar, tasks and habits, updated in
real time. Everything is controlled from the phone, and each person in the house has a
profile.

Next: running it on a Raspberry Pi, plugging it into Chronicle, then the intelligent layer.

Python, FastAPI, SQLite, Server-Sent Events, framework-free HTML/JS.

### Run it

Create a `.env` with `LAT` and `LON` (location for the weather), then:

```bash
uv sync
uv run uvicorn main:app --host 0.0.0.0 --port 8000
```

The screen is on `/display_dashboard`, the remote on `/phone`.
