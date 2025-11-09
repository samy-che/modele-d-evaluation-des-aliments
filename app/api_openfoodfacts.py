"""Module d'API pour récupérer les données nutritionnelles depuis OpenFoodFacts."""

import logging
from typing import Dict, List, Optional, Any
import requests
import pandas as pd
import time

logger = logging.getLogger(__name__)


class OpenFoodFactsAPI:
    """Client API pour interroger la base OpenFoodFacts."""
    
    BASE_URL = "https://world.openfoodfacts.org/api/v2"
    SEARCH_URL = f"{BASE_URL}/search"
    
    def __init__(self, user_agent: str = "NutriScore-ELECTRE-App/1.0"):
        """
        Initialise le client API.
        
        Args:
            user_agent: User agent à utiliser pour les requêtes
        """
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': user_agent
        })
        self.rate_limit_delay = 1.0  # Délai entre les requêtes (secondes)
    
    def search_products(
        self,
        query: str = "",
        category: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
        countries: str = "France",
        fields: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Recherche des produits sur OpenFoodFacts.
        
        Args:
            query: Terme de recherche
            category: Catégorie de produits (ex: "cereals", "yogurts")
            page: Numéro de page
            page_size: Nombre de résultats par page (max 100)
            countries: Pays des produits
            fields: Liste des champs à récupérer
            
        Returns:
            Réponse JSON de l'API
        """
        if fields is None:
            fields = [
                'product_name',
                'brands',
                'categories',
                'nutriscore_grade',
                'nutriscore_score',
                'energy_100g',
                'fat_100g',
                'saturated-fat_100g',
                'sugars_100g',
                'salt_100g',
                'sodium_100g',
                'proteins_100g',
                'fiber_100g',
                'fruits-vegetables-nuts_100g',
                'additives_n'
            ]
        
        params = {
            'page': page,
            'page_size': min(page_size, 100),
            'fields': ','.join(fields),
            'json': 1
        }
        
        if query:
            params['search_terms'] = query
        
        if category:
            params['categories_tags'] = category
        
        if countries:
            params['countries_tags'] = countries.lower()
        
        try:
            time.sleep(self.rate_limit_delay)  # Respect du rate limiting
            response = self.session.get(self.SEARCH_URL, params=params)
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur lors de la requête API: {e}")
            return {'products': [], 'count': 0}
    
    def get_product_by_barcode(self, barcode: str) -> Optional[Dict[str, Any]]:
        """
        Récupère un produit par son code-barres.
        
        Args:
            barcode: Code-barres du produit
            
        Returns:
            Données du produit ou None
        """
        url = f"{self.BASE_URL}/product/{barcode}.json"
        
        try:
            time.sleep(self.rate_limit_delay)
            response = self.session.get(url)
            response.raise_for_status()
            data = response.json()
            
            if data.get('status') == 1:
                return data.get('product')
            return None
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur lors de la récupération du produit {barcode}: {e}")
            return None
    
    def search_to_dataframe(
        self,
        query: str = "",
        category: Optional[str] = None,
        max_products: int = 100,
        countries: str = "France"
    ) -> pd.DataFrame:
        """
        Recherche des produits et retourne un DataFrame pandas.
        
        Args:
            query: Terme de recherche
            category: Catégorie de produits
            max_products: Nombre maximum de produits à récupérer
            countries: Pays des produits
            
        Returns:
            DataFrame contenant les produits
        """
        all_products = []
        page = 1
        page_size = min(100, max_products)
        
        logger.info(f"Recherche de produits: query='{query}', category='{category}', max={max_products}")
        
        while len(all_products) < max_products:
            result = self.search_products(
                query=query,
                category=category,
                page=page,
                page_size=page_size,
                countries=countries
            )
            
            products = result.get('products', [])
            if not products:
                break
            
            all_products.extend(products)
            
            # Vérifier si on a récupéré tous les produits disponibles
            total_count = result.get('count', 0)
            if len(all_products) >= total_count:
                break
            
            page += 1
            
            # Éviter de dépasser le maximum demandé
            if len(all_products) >= max_products:
                all_products = all_products[:max_products]
                break
        
        logger.info(f"Récupéré {len(all_products)} produits")
        
        # Convertir en DataFrame
        df = pd.DataFrame(all_products)
        
        # Nettoyer et renommer les colonnes
        if not df.empty:
            df = self._clean_dataframe(df)
        
        return df
    
    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Nettoie et standardise le DataFrame.
        
        Args:
            df: DataFrame brut
            
        Returns:
            DataFrame nettoyé
        """
        # Renommage des colonnes pour correspondre au format attendu
        column_mapping = {
            'product_name': 'product_name',
            'brands': 'brands',
            'nutriscore_grade': 'nutriscore_label',
            'nutriscore_score': 'nutriscore_score',
            'energy_100g': 'energy_100g',
            'saturated-fat_100g': 'saturated_fat_100g',
            'sugars_100g': 'sugars_100g',
            'sodium_100g': 'sodium_100g',
            'salt_100g': 'salt_100g',
            'proteins_100g': 'proteins_100g',
            'fiber_100g': 'fiber_100g',
            'fruits-vegetables-nuts_100g': 'fruits_veg_nuts_percent',
            'additives_n': 'additives_count'
        }
        
        # Renommer les colonnes existantes
        df = df.rename(columns={k: v for k, v in column_mapping.items() if k in df.columns})
        
        # Convertir le sel en sodium si nécessaire (1g sel = 400mg sodium)
        if 'salt_100g' in df.columns and 'sodium_100g' not in df.columns:
            df['sodium_100g'] = df['salt_100g'] * 400  # Conversion g de sel -> mg de sodium
        
        # Supprimer les colonnes inutiles
        if 'salt_100g' in df.columns:
            df = df.drop(columns=['salt_100g'])
        
        # Convertir le Nutri-Score en majuscules
        if 'nutriscore_label' in df.columns:
            df['nutriscore_label'] = df['nutriscore_label'].str.upper()
        
        return df


# Fonctions utilitaires pour l'interface Streamlit

def fetch_openfoodfacts_data(
    query: str = "",
    category: Optional[str] = None,
    max_products: int = 100,
    countries: str = "France"
) -> pd.DataFrame:
    """
    Fonction simplifiée pour récupérer des données depuis OpenFoodFacts.
    
    Args:
        query: Terme de recherche
        category: Catégorie de produits
        max_products: Nombre maximum de produits
        countries: Pays des produits
        
    Returns:
        DataFrame avec les produits
    """
    api = OpenFoodFactsAPI()
    return api.search_to_dataframe(
        query=query,
        category=category,
        max_products=max_products,
        countries=countries
    )


# Exemple d'utilisation
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Rechercher des céréales
    api = OpenFoodFactsAPI()
    df = api.search_to_dataframe(
        category="cereals",
        max_products=100,
        countries="France"
    )
    
    print(f"\nRécupéré {len(df)} produits")
    print("\nColonnes disponibles:")
    print(df.columns.tolist())
    
    if not df.empty:
        print("\nAperçu des données:")
        print(df.head())
        
        # Sauvegarder dans un fichier Excel
        output_file = "openfoodfacts_cereales.xlsx"
        df.to_excel(output_file, index=False)
        print(f"\nDonnées sauvegardées dans {output_file}")
