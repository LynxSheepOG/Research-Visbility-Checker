import requests

import pandas as pd

def base_link(prefix: str = None, query:str = None) -> dict:
    """
    Cette fonction permet de rechercher des informations de base telles que l'auteur, une recherche simple, etc.
    
    Args : 
        prefix(str) : nom du domaine
        query(str) : information à rechercher, paramètre pouvant être utilisé. 
    """
    # Lien de base
    root = f"https://api.archives-ouvertes.fr/{"ref/" + prefix 
                                            if prefix in ["anrproject","doctype","instance","metadata","structure","metadatalist","journal","domain","europeanproject","author"] 
                                            else "search/"}"
    endpoint = f"?q={query}&wt=json"
    return requests.get(root+endpoint).json()

def req_id_hal(idhal:str) -> list:
    root = "https://api.archives-ouvertes.fr/ref/author"
    endpoint = f"?q=idHal_s:{idhal}&wt=json"
    req = requests.get(root+endpoint).json()

    if req["response"]["numFound"] == 0:
        return "Erreur Recherche HAL : Nous n'avons pas trouvé de données\nVérifiez les informations renseignées."
    else:
        docid = [a["docid"] for a in req["response"]["docs"]]
        return docid

def id_author(lastName:str, firstName:str) -> list:
    """
    Cette fonction permet de rechercher les identifiants des auteurs que vous souhaitez.
    
    Args :
        lastName(str) : Nom de l'auteur
        firstName(str) : prénom de l'auteur

    Return:
        list : liste des identifiants des auteurs
    """
    if not lastName:
        return "Erreur Recherche HAL : Veuillez renseigner le nom de famille."
    if not firstName:
        return "Erreur Recherche HAL : Veuillez renseigner le prénom."
    
    req = base_link(prefix = "author", query= f"{lastName} {firstName}")

    id_auth = []
    docs = req["response"]["docs"]
    numFound = req["response"]["numFound"]
        
    if int(numFound) == 0:
        return "Erreur Recherche HAL : Nous n'avons pas trouvé de données\nVérifiez les informations renseignées."
    
    for doc in docs:
        docid = doc["docid"]
        if docid.split("-")[1] not in id_auth:
            id_auth.append(docid) # .split("-")[1]
    return id_auth

def get_hal_researcher_data(lastName:str = None, firstName:str = None, idhal:str = None) -> pd.DataFrame:
    """
    Cette fonction permet de rechercher les identifiants des auteurs que vous souhaitez.
    
    Args :
        lastName(str) : Nom de l'auteur
        firstName(str) : prénom de l'auteur
    
    Return:
        pd.DataFrame : DataFrame avec les données de l'auteur
    """

    # authIdForm_i:158428 -> Marc Humbert -> 449
    if lastName and firstName:
        ids = id_author(lastName = lastName, firstName=firstName)
    if idhal:
        ids = req_id_hal(idhal=idhal)
    else:
        return "Erreur Recherche HAL : Veuillez renseigner le nom et le prénom ou l'ID HAL."

    if isinstance(ids, list):
        data_hal = []
        for id in ids:
            req = base_link(query=f"authIdFormPerson_s:{id}&fl=title_s,doiId_s,authIdHal_s,pubmedId_id,journalTitle_s,journalPublisher_s,publicationDate_s,authLastNameFirstName_s&start=0&rows=1000")
            docs = req["response"]["docs"]
            for doc in docs:
                title_s = doc["title_s"][0]
                journalTitle_s = doc.get("journalTitle_s", None)
                journalPublisher_s = doc.get("journalPublisher_s", None)
                publicationDate_s = doc["publicationDate_s"].split("-")[0]
                doiId_s = doc.get("doiId_s", None)
                pubmedId_id = doc.get("pubmedId_id", None)
                authLastNameFirstName_s = doc.get("authLastNameFirstName_s", None)
                data_hal.append({
                    "Titre Journal": journalTitle_s,
                    "Auteur" : authLastNameFirstName_s,
                    "Titre Article": title_s,
                    "Journal Publisher" : journalPublisher_s,
                    "Date de publication" : publicationDate_s,
                    "DOI": doiId_s,
                    "pubmedId": pubmedId_id
                })
    return pd.DataFrame(data_hal)