# WorldBankProject

![Cartographie emission methane](/images/cartographie_emission_methane.PNG "Cartographie Methane emission")

## Plan

### Data retrieval

Ce projet commence par un script **ETLWorldBank.py** qui permet de récupérer les données sur l’emission de méthane de l’API World Bank. Les indicateurs utilisés sont  définis ci-dessous:

* NY.GDP.PCAP.CD GDP per capita (current US)
* IS.AIR.DPRT Air transport, registered carrier departures worldwide
* EG.USE.ELEC.KH.PC Electric power consumption (kWh per capita)
* AG.LND.TOTL.K2 Land area (sq. km)
* EN.ATM.METH.AG.KT.CE and EN.ATM.METH.AG.ZS : Agricultural methane emissions are emissions from animals, animal waste, rice production, agricultural waste burning (nonenergy, on-site), and savanna burning.
* EN.ATM.METH.EG.KT.CE and EN.ATM.METH.EG.ZS : Methane emissions from energy processes are emissions from the production, handling, transmission, and combustion of fossil fuels and biofuels.
* EN.ATM.METH.KT.CE and EN.ATM.METH.ZG: Methane emissions are those stemming from human activities such as agriculture and from industrial methane production.
* EG.ELC.NGAS.ZS Electricity production from natural gas sources (% of total)
* EG.FEC.RNEW.ZS Renewable energy consumption (% of total final energy consumption)
* EG.USE.COMM.FO.ZS Fossil fuel energy consumption (% of total)
* 'SP.POP.TOTL' Population
* 'EN.POP.DNST' : represent population density, which refers to the number of people per unit of land area.
* 'NY.GDP.MKTP.CD': Gross Domestic Product (GDP) in current US dollars.

le module utilisé pour récupérer les données de WorldBankAPI s'appelle WBGAPI. Il fournit un accès moderne et pythonique à l'API de données de la Banque mondiale. Il est conçu à la fois pour les débutants en données et les types de scientifiques des données.

Ensuite ces données sont complétés par une premiere notation annuelle des pays en fonction de leur emission rapporté a leur superficie. Le choix de ce ratio permet de noté chaque pays en fonction de ces caractéristiques propres. (Land area)

### Data estimation:

Pour estimer les valeurs d’emission de methane manquante. Trois méthode ont été proposé :
- La méthode de rolling_statistical : Il s’agit de completer les valeurs via un 'SMA' : Simple Moving Average, 'WMA' : Weighted Moving Average ou 'EMA' : Exponential Moving Average
- Methode KNNImputer: c’est un algorithme de remplacement de valeurs manquantes basé sur la méthode k plus proches voisins. Il utilise les valeurs des k observations les plus proches pour imputer une valeur manquante dans une colonne donnée. 
- interpolation lineaire : une méthode utilisée pour compléter les valeurs manquantes dans une série chronologique en utilisant une ligne droite pour interpoler les valeurs manquantes entre les valeurs connues.

Le script  **HandlingMissingvalues** permet d'appliquer ces méthodes. 

### Uncertainty computation :

Afin de calculer l’incertitude de l’estimation des valeurs manquantes. La méthode de bootstrapping a été utilisé: il consiste a simuler des valeurs nulles de manière aléatoire, puis d’estimer ces valeurs et enfin de calculer l’erreur obtenu. Cette simulation est repetté plusieurs fois et au final l’incertitude est determiné par l’ecart-type de ces erreurs.
Le script  **HandlingMissingvalues** permet de faire ce traitement. 

### Methane emissions prediction:
Pour la prediction des 10 derniers années: le fichier csv **world_methane_emission_10y** contient les informations sur l'emission des 10 dernieres années. il a été calculer en specifiant dans la requete mrv= 10. 

En ce qui concerne la prediction sur les 5 prochaines années. les données de world bank ne me permet pas de predire avec des modèles de ML correctement l'emission de méthane pour chaque pays.

Néanmoins en se basant sur les methodes de lissage on peut faire des prévisions sur les prochaines emissions.

Une tentative d'utilisation d'un modele de regression lineaire a été effectué. l'idée étant de formuler dans un premier temps Les données de séries chronologiques comme une apprentissage supervisé (methode de sliding windows). Puis d'appliquer des méthodes de ML voir le notebook (**predict_methane_emission**). Cependant au niveau de la prediction il n y a pas suffisamment de features avec des données pour prédire celles la valeur d'emission de méthanes.


### Scoring methodology:

Pour évaluer un pays en fonction de ses émissions de méthane, quatres méthodes ont été testé :

Les émissions totales de méthane : On peut calculer la quantité totale de méthane émise par un pays pour en faire la base de l'évaluation.

les émissions par superficie : Il suffit de diviser les émissions totales par la superficie du pays

Les émissions par habitant : Il suffit de diviser les émissions totales par la population pour obtenir les émissions par habitant, ce qui peut donner une meilleure idée de la responsabilité individuelle pour les émissions.

Intensité des émissions : Cela mesure les émissions par unité de produit intérieur brut (PIB), ce qui donne une idée des émissions produites par unité d'activité économique.

On retient la méthode par superficie.

Grace a la méthode min max scaler, on réduit l’échelle sur une plage de 0 à 4.

Pour affiner le score on calcul ces memes indicateurs mais cette fois ci sur des clusters. on utilise pour cela la methode de clustering en ML pour regrouper sur une année donnée les pays ayant les memes caractéristiques d’emission et ensuite d’établir un score sur ce groupe en particulier.

Au final en se retrouve 


Les scripts   **ETLWorldBank.py** et **ComputeScoreKmeans** permettent de faire ce traitement. 
### REST API:

Une fois les données complet, un restapi a été crée avec FastApi qui prend en entrée le code alpha2 et l’année et retourne :

- La valeur des émissions de méthane du pays défini à une année spécifique (nombre flottant),
- La connaissance si la valeur est mesurée ou estimée (booléen),
- Le code iso alpha 2 du pays (chaîne de caractères),
- Le nom du pays (chaîne de caractères),
- L’incertitude sur les émissions de méthane,
- Le score / index pour ce pays.

Les scripts   **main** et **ComputeInfoMethaneEmission** permettent de faire ce traitement. 
  
