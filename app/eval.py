"""
Module d'évaluation et comparaison entre Nutri-Score et ELECTRE TRI.
Génère matrices de confusion, métriques et rapports visuels.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import logging
from sklearn.metrics import confusion_matrix, accuracy_score, f1_score, mean_absolute_error
from typing import Dict, Tuple, List, Optional
from pathlib import Path

# Configuration du logging
logger = logging.getLogger(__name__)

# Configuration matplotlib pour les caractères français
plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

class NutriScoreElectreEvaluator:
    """Classe d'évaluation et comparaison Nutri-Score vs ELECTRE TRI."""
    
    def __init__(self):
        """Initialise l'évaluateur."""
        # Mapping des labels vers des valeurs numériques pour les métriques
        self.nutriscore_mapping = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'N/A': np.nan, 'ERROR': np.nan}
        self.electre_mapping = {'A\'': 1, 'B\'': 2, 'C\'': 3, 'D\'': 4, 'E\'': 5, 'N/A': np.nan, 'ERROR': np.nan}
        
        # Labels ordonnés
        self.nutriscore_labels = ['A', 'B', 'C', 'D', 'E']
        self.electre_labels = ['A\'', 'B\'', 'C\'', 'D\'', 'E\'']
    
    def _convert_labels_to_numeric(self, 
                                  labels: pd.Series, 
                                  mapping: Dict[str, int]) -> pd.Series:
        """
        Convertit les labels en valeurs numériques.
        
        Args:
            labels: Série avec les labels
            mapping: Dictionnaire de mapping
            
        Returns:
            Série avec valeurs numériques
        """
        return labels.map(mapping)
    
    def _clean_data_for_comparison(self, 
                                  df: pd.DataFrame, 
                                  nutriscore_col: str,
                                  electre_col: str) -> pd.DataFrame:
        """
        Nettoie les données pour la comparaison.
        
        Args:
            df: DataFrame avec les données
            nutriscore_col: Nom de la colonne Nutri-Score
            electre_col: Nom de la colonne ELECTRE
            
        Returns:
            DataFrame nettoyé
        """
        df_clean = df.copy()
        
        # Enlever les lignes avec des valeurs manquantes ou d'erreur
        invalid_values = ['N/A', 'ERROR', np.nan, None]
        
        mask = (
            ~df_clean[nutriscore_col].isin(invalid_values) & 
            ~df_clean[electre_col].isin(invalid_values) &
            df_clean[nutriscore_col].notna() & 
            df_clean[electre_col].notna()
        )
        
        df_filtered = df_clean[mask]
        
        removed_count = len(df_clean) - len(df_filtered)
        if removed_count > 0:
            logger.info(f"Lignes supprimées pour valeurs invalides : {removed_count}")
        
        return df_filtered
    
    def compute_confusion_matrix(self, 
                               df: pd.DataFrame,
                               nutriscore_col: str = 'ns_label_calc',
                               electre_col: str = 'electre_cat') -> Tuple[np.ndarray, Dict[str, any]]:
        """
        Calcule la matrice de confusion entre Nutri-Score et ELECTRE TRI.
        
        Args:
            df: DataFrame avec les prédictions
            nutriscore_col: Colonne Nutri-Score
            electre_col: Colonne ELECTRE TRI
            
        Returns:
            Tuple (matrice confusion, métadonnées)
        """
        # Nettoyer les données
        df_clean = self._clean_data_for_comparison(df, nutriscore_col, electre_col)
        
        if len(df_clean) == 0:
            logger.error("Aucune donnée valide pour la matrice de confusion")
            return np.array([]), {}
        
        logger.info(f"Calcul matrice de confusion sur {len(df_clean)} produits")
        
        # Récupérer les labels
        nutriscore_values = df_clean[nutriscore_col]
        electre_values = df_clean[electre_col]
        
        # Créer la matrice de confusion
        cm = confusion_matrix(
            nutriscore_values, 
            electre_values,
            labels=self.nutriscore_labels + [label for label in self.electre_labels if label not in nutriscore_values.unique()]
        )
        
        # Métadonnées
        metadata = {
            'nutriscore_labels': self.nutriscore_labels,
            'electre_labels': self.electre_labels,
            'total_samples': len(df_clean),
            'nutriscore_distribution': nutriscore_values.value_counts().to_dict(),
            'electre_distribution': electre_values.value_counts().to_dict()
        }
        
        return cm, metadata
    
    def compute_metrics(self, 
                       df: pd.DataFrame,
                       nutriscore_col: str = 'ns_label_calc',
                       electre_col: str = 'electre_cat') -> Dict[str, float]:
        """
        Calcule les métriques de comparaison.
        
        Args:
            df: DataFrame avec les prédictions
            nutriscore_col: Colonne Nutri-Score
            electre_col: Colonne ELECTRE TRI
            
        Returns:
            Dictionnaire avec les métriques
        """
        # Nettoyer les données
        df_clean = self._clean_data_for_comparison(df, nutriscore_col, electre_col)
        
        if len(df_clean) == 0:
            logger.error("Aucune donnée valide pour le calcul des métriques")
            return {}
        
        # Conversion en valeurs numériques
        nutriscore_numeric = self._convert_labels_to_numeric(
            df_clean[nutriscore_col], self.nutriscore_mapping
        )
        electre_numeric = self._convert_labels_to_numeric(
            df_clean[electre_col], self.electre_mapping
        )
        
        # Supprimer les valeurs manquantes après conversion
        valid_mask = nutriscore_numeric.notna() & electre_numeric.notna()
        nutriscore_clean = nutriscore_numeric[valid_mask]
        electre_clean = electre_numeric[valid_mask]
        
        if len(nutriscore_clean) == 0:
            return {}
        
        # Calcul des métriques
        metrics = {}
        
        try:
            # Accuracy (correspondance exacte)
            accuracy = accuracy_score(nutriscore_clean, electre_clean)
            metrics['accuracy'] = accuracy
            
            # F1-Score macro et weighted
            f1_macro = f1_score(nutriscore_clean, electre_clean, average='macro')
            f1_weighted = f1_score(nutriscore_clean, electre_clean, average='weighted')
            metrics['f1_macro'] = f1_macro
            metrics['f1_weighted'] = f1_weighted
            
            # MAE (Mean Absolute Error) sur les rangs
            mae = mean_absolute_error(nutriscore_clean, electre_clean)
            metrics['mae_rank'] = mae
            
            # Métriques supplémentaires
            
            # Concordance à ±1 rang (tolérance d'1 niveau)
            tolerance_1 = (np.abs(nutriscore_clean - electre_clean) <= 1).mean()
            metrics['accuracy_tolerance_1'] = tolerance_1
            
            # Concordance à ±2 rangs
            tolerance_2 = (np.abs(nutriscore_clean - electre_clean) <= 2).mean()
            metrics['accuracy_tolerance_2'] = tolerance_2
            
            # Corrélation de Spearman
            from scipy.stats import spearmanr
            correlation, p_value = spearmanr(nutriscore_clean, electre_clean)
            metrics['spearman_correlation'] = correlation
            metrics['spearman_p_value'] = p_value
            
            logger.info(f"Métriques calculées : Accuracy={accuracy:.3f}, F1_macro={f1_macro:.3f}, MAE={mae:.3f}")
            
        except Exception as e:
            logger.error(f"Erreur calcul métriques : {e}")
        
        return metrics
    
    def plot_confusion_matrix(self, 
                            confusion_mat: np.ndarray,
                            metadata: Dict[str, any],
                            save_path: Optional[str] = None,
                            title: str = "Matrice de Confusion : Nutri-Score vs ELECTRE TRI") -> plt.Figure:
        """
        Crée un graphique de la matrice de confusion.
        
        Args:
            confusion_mat: Matrice de confusion
            metadata: Métadonnées de la matrice
            save_path: Chemin de sauvegarde (optionnel)
            title: Titre du graphique
            
        Returns:
            Figure matplotlib
        """
        # Créer la figure
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Déterminer les labels pour les axes
        nutri_labels = metadata.get('nutriscore_labels', self.nutriscore_labels)
        electre_labels = metadata.get('electre_labels', self.electre_labels)
        
        # Adapter la matrice si nécessaire
        if confusion_mat.shape[0] != len(nutri_labels):
            # Ajuster selon les données disponibles
            actual_nutri_labels = nutri_labels[:confusion_mat.shape[0]]
            actual_electre_labels = electre_labels[:confusion_mat.shape[1]]
        else:
            actual_nutri_labels = nutri_labels
            actual_electre_labels = electre_labels
        
        # Créer la heatmap
        sns.heatmap(
            confusion_mat,
            annot=True,
            fmt='d',
            cmap='Blues',
            xticklabels=actual_electre_labels,
            yticklabels=actual_nutri_labels,
            ax=ax,
            cbar_kws={'label': 'Nombre de produits'}
        )
        
        # Personnalisation
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel('ELECTRE TRI (Prédictions)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Nutri-Score (Référence)', fontsize=12, fontweight='bold')
        
        # Rotation des labels
        plt.setp(ax.get_xticklabels(), rotation=0)
        plt.setp(ax.get_yticklabels(), rotation=0)
        
        # Ajouter des informations
        total_samples = metadata.get('total_samples', 0)
        ax.text(
            0.02, 0.98, 
            f'Total: {total_samples} produits', 
            transform=ax.transAxes,
            verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8)
        )
        
        plt.tight_layout()
        
        # Sauvegarde si demandée
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Matrice de confusion sauvegardée : {save_path}")
        
        return fig
    
    def plot_metrics_summary(self, 
                           metrics: Dict[str, float],
                           save_path: Optional[str] = None) -> plt.Figure:
        """
        Crée un graphique résumé des métriques.
        
        Args:
            metrics: Dictionnaire des métriques
            save_path: Chemin de sauvegarde
            
        Returns:
            Figure matplotlib
        """
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 10))
        
        # 1. Métriques principales
        main_metrics = {
            'Accuracy': metrics.get('accuracy', 0),
            'F1-Score\n(Macro)': metrics.get('f1_macro', 0),
            'F1-Score\n(Weighted)': metrics.get('f1_weighted', 0)
        }
        
        bars1 = ax1.bar(main_metrics.keys(), main_metrics.values(), 
                       color=['skyblue', 'lightgreen', 'salmon'])
        ax1.set_title('Métriques Principales', fontweight='bold')
        ax1.set_ylabel('Score')
        ax1.set_ylim(0, 1)
        
        # Ajouter les valeurs sur les barres
        for bar, value in zip(bars1, main_metrics.values()):
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                    f'{value:.3f}', ha='center', va='bottom')
        
        # 2. Tolérance
        tolerance_metrics = {
            'Exact': metrics.get('accuracy', 0),
            '±1 niveau': metrics.get('accuracy_tolerance_1', 0),
            '±2 niveaux': metrics.get('accuracy_tolerance_2', 0)
        }
        
        bars2 = ax2.bar(tolerance_metrics.keys(), tolerance_metrics.values(),
                       color=['red', 'orange', 'yellow'])
        ax2.set_title('Accuracy avec Tolérance', fontweight='bold')
        ax2.set_ylabel('Score')
        ax2.set_ylim(0, 1)
        
        for bar, value in zip(bars2, tolerance_metrics.values()):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                    f'{value:.3f}', ha='center', va='bottom')
        
        # 3. MAE
        mae_value = metrics.get('mae_rank', 0)
        ax3.bar(['MAE\n(Rang)'], [mae_value], color='lightcoral')
        ax3.set_title('Erreur Absolue Moyenne', fontweight='bold')
        ax3.set_ylabel('Erreur (niveaux)')
        ax3.text(0, mae_value + 0.05, f'{mae_value:.3f}', 
                ha='center', va='bottom', fontweight='bold')
        
        # 4. Corrélation
        corr_value = metrics.get('spearman_correlation', 0)
        color = 'lightgreen' if corr_value > 0.5 else 'yellow' if corr_value > 0.3 else 'lightcoral'
        ax4.bar(['Corrélation\nSpearman'], [abs(corr_value)], color=color)
        ax4.set_title('Corrélation des Rangs', fontweight='bold')
        ax4.set_ylabel('Coefficient')
        ax4.set_ylim(0, 1)
        ax4.text(0, abs(corr_value) + 0.02, f'{corr_value:.3f}', 
                ha='center', va='bottom', fontweight='bold')
        
        plt.suptitle('Résumé des Métriques de Comparaison', fontsize=16, fontweight='bold')
        plt.tight_layout()
        
        # Sauvegarde
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Résumé des métriques sauvegardé : {save_path}")
        
        return fig
    
    def generate_comparison_report(self, 
                                 df: pd.DataFrame,
                                 nutriscore_col: str = 'ns_label_calc',
                                 electre_col: str = 'electre_cat',
                                 output_dir: str = "outputs") -> Dict[str, any]:
        """
        Génère un rapport complet de comparaison.
        
        Args:
            df: DataFrame avec les données
            nutriscore_col: Colonne Nutri-Score
            electre_col: Colonne ELECTRE TRI
            output_dir: Répertoire de sortie
            
        Returns:
            Dictionnaire avec tous les résultats
        """
        logger.info("Génération du rapport de comparaison complet")
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # 1. Matrice de confusion
        cm, cm_metadata = self.compute_confusion_matrix(df, nutriscore_col, electre_col)
        
        # 2. Métriques
        metrics = self.compute_metrics(df, nutriscore_col, electre_col)
        
        # 3. Graphiques
        if len(cm) > 0:
            # Matrice de confusion
            confusion_fig = self.plot_confusion_matrix(
                cm, cm_metadata, 
                save_path=output_path / "reports" / "confusion_matrix.png"
            )
            plt.close(confusion_fig)
            
            # Résumé métriques si on a des métriques
            if metrics:
                metrics_fig = self.plot_metrics_summary(
                    metrics,
                    save_path=output_path / "reports" / "metrics_summary.png"
                )
                plt.close(metrics_fig)
        
        # 4. Export Excel des résultats
        excel_path = output_path / "excel" / "dataset_avec_preds.xlsx"
        excel_path.parent.mkdir(parents=True, exist_ok=True)
        
        df.to_excel(excel_path, index=False)
        logger.info(f"Dataset avec prédictions exporté : {excel_path}")
        
        # 5. Rapport textuel
        report = {
            'confusion_matrix': cm.tolist() if len(cm) > 0 else [],
            'confusion_metadata': cm_metadata,
            'metrics': metrics,
            'summary': {
                'total_products': len(df),
                'valid_comparisons': cm_metadata.get('total_samples', 0),
                'files_generated': {
                    'confusion_matrix': str(output_path / "reports" / "confusion_matrix.png"),
                    'metrics_summary': str(output_path / "reports" / "metrics_summary.png"),
                    'dataset_excel': str(excel_path)
                }
            }
        }
        
        logger.info("Rapport de comparaison généré avec succès")
        return report


def compare_nutriscore_electre(df: pd.DataFrame, 
                              nutriscore_col: str = 'ns_label_calc',
                              electre_col: str = 'electre_cat',
                              output_dir: str = "outputs") -> Dict[str, any]:
    """
    Fonction utilitaire pour comparer Nutri-Score et ELECTRE TRI.
    
    Args:
        df: DataFrame avec les données
        nutriscore_col: Colonne Nutri-Score
        electre_col: Colonne ELECTRE TRI
        output_dir: Répertoire de sortie
        
    Returns:
        Rapport de comparaison
    """
    evaluator = NutriScoreElectreEvaluator()
    return evaluator.generate_comparison_report(df, nutriscore_col, electre_col, output_dir)


if __name__ == "__main__":
    # Test du module
    print("=== Test du module d'évaluation ===")
    
    # Créer des données de test
    np.random.seed(42)
    n_samples = 100
    
    # Générer des labels avec une corrélation imparfaite
    nutri_labels = np.random.choice(['A', 'B', 'C', 'D', 'E'], n_samples)
    
    # ELECTRE avec un peu de variation
    electre_labels = []
    for label in nutri_labels:
        if np.random.rand() < 0.7:  # 70% de concordance exacte
            electre_labels.append(label + '\'')
        else:  # 30% de variation
            alternatives = [l + '\'' for l in ['A', 'B', 'C', 'D', 'E']]
            electre_labels.append(np.random.choice(alternatives))
    
    # DataFrame de test
    test_df = pd.DataFrame({
        'product_name': [f'Produit_{i}' for i in range(n_samples)],
        'ns_label_calc': nutri_labels,
        'electre_cat': electre_labels
    })
    
    print(f"Dataset de test créé : {len(test_df)} produits")
    
    try:
        # Test de la comparaison
        report = compare_nutriscore_electre(test_df, output_dir="outputs_test")
        
        print(f"\nRapport généré :")
        print(f"- Produits analysés : {report['summary']['total_products']}")
        print(f"- Comparaisons valides : {report['summary']['valid_comparisons']}")
        
        if report['metrics']:
            print(f"- Accuracy : {report['metrics'].get('accuracy', 0):.3f}")
            print(f"- F1-Score macro : {report['metrics'].get('f1_macro', 0):.3f}")
            print(f"- MAE : {report['metrics'].get('mae_rank', 0):.3f}")
        
        print("\nTest du module d'évaluation terminé avec succès !")
        
    except Exception as e:
        print(f"Erreur de test : {e}")
        import traceback
        traceback.print_exc()