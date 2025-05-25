import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import os
from typing import Dict, List, Union, Any

class DataAnalysisPlotter:
    """
    Clase para analizar y visualizar datos estadísticos de palabras.
    """
    
    def __init__(self, data: Dict[str, Dict[str, Any]]):
        """
        Inicializa el analizador de datos con los datos estadísticos.
        
        Args:
            data (Dict[str, Dict[str, Any]]): Diccionario con estadísticas de palabras.
                Formato esperado:
                {
                    'age_group': {
                        'adults': {
                            'total_words': int,
                            'iconic_words': dict,  # {palabra: {count, rating}}
                            'non_iconic_words': dict,  # {palabra: count}
                            'total_iconic_occurrences': int,
                            'total_non_iconic_occurrences': int,
                            'unique_iconic_words': set,
                            'unique_non_iconic_words': set
                        },
                        'children': {
                            # Misma estructura que adults
                        }
                    },
                    ...
                }
        """
        self.data = data
        # Configurar el estilo de las gráficas
        sns.set_theme(style="whitegrid")
        sns.set_palette("husl")
        
    def _validate_data(self) -> bool:
        """
        Valida que los datos tengan el formato correcto.
        
        Returns:
            bool: True si los datos son válidos, False en caso contrario.
        """
        if not isinstance(self.data, dict):
            return False
            
        for age_group, stats in self.data.items():
            if not isinstance(stats, dict):
                return False
            if 'adults' not in stats or 'children' not in stats:
                return False
                
            for group in ['adults', 'children']:
                group_stats = stats[group]
                required_fields = [
                    'total_words', 'iconic_words', 'non_iconic_words',
                    'total_iconic_occurrences', 'total_non_iconic_occurrences',
                    'unique_iconic_words', 'unique_non_iconic_words'
                ]
                if not all(field in group_stats for field in required_fields):
                    return False
                    
        return True

    def plot_iconic_vs_non_iconic_by_age(self, save_path: str = None):
        """
        Crea una gráfica de barras mostrando la proporción de palabras icónicas y no icónicas por grupo de edad, para niños y adultos.
        Sin mostrar porcentajes para mantener la gráfica limpia.
        
        Args:
            save_path (str, optional): Ruta donde guardar la gráfica. Si es None, la gráfica se muestra en pantalla.
        """
        age_groups = []
        iconic_children = []
        non_iconic_children = []
        iconic_adults = []
        non_iconic_adults = []
        
        for age_group, stats in sorted(self.data.items()):
            age_groups.append(age_group)
            
            # Calcular porcentajes para niños
            total_children = stats['children']['total_words']
            iconic_children_pct = (stats['children']['total_iconic_occurrences'] / total_children * 100) if total_children > 0 else 0
            non_iconic_children_pct = (stats['children']['total_non_iconic_occurrences'] / total_children * 100) if total_children > 0 else 0
            
            # Calcular porcentajes para adultos
            total_adults = stats['adults']['total_words']
            iconic_adults_pct = (stats['adults']['total_iconic_occurrences'] / total_adults * 100) if total_adults > 0 else 0
            non_iconic_adults_pct = (stats['adults']['total_non_iconic_occurrences'] / total_adults * 100) if total_adults > 0 else 0
            
            iconic_children.append(iconic_children_pct)
            non_iconic_children.append(non_iconic_children_pct)
            iconic_adults.append(iconic_adults_pct)
            non_iconic_adults.append(non_iconic_adults_pct)
        
        # Crear la gráfica
        fig, ax = plt.subplots(figsize=(12, 6))
        x = np.arange(len(age_groups))
        width = 0.2
        
        # Dibujar las barras
        ax.bar(x - 1.5*width, iconic_children, width, label='Niños - Icónicas')
        ax.bar(x - 0.5*width, non_iconic_children, width, label='Niños - No Icónicas')
        ax.bar(x + 0.5*width, iconic_adults, width, label='Adultos - Icónicas')
        ax.bar(x + 1.5*width, non_iconic_adults, width, label='Adultos - No Icónicas')
        
        # Configurar la gráfica
        ax.set_xlabel('Grupo de Edad')
        ax.set_ylabel('Porcentaje de Palabras (%)')
        ax.set_title('Proporción de Palabras Icónicas vs No Icónicas por Grupo de Edad')
        ax.set_xticks(x)
        ax.set_xticklabels(age_groups)
        ax.legend()
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path)
        else:
            plt.show()
        plt.close()

    def plot_iconic_vs_non_iconic_by_age_adults(self, save_path: str = None):
        """
        Crea una gráfica de barras mostrando la proporción de palabras icónicas y no icónicas por grupo de edad,
        solo para adultos, incluyendo los porcentajes.
        
        Args:
            save_path (str, optional): Ruta donde guardar la gráfica. Si es None, la gráfica se muestra en pantalla.
        """
        age_groups = []
        iconic_adults = []
        non_iconic_adults = []
        
        for age_group, stats in sorted(self.data.items()):
            age_groups.append(age_group)
            
            # Calcular porcentajes para adultos
            total_adults = stats['adults']['total_words']
            iconic_adults_pct = (stats['adults']['total_iconic_occurrences'] / total_adults * 100) if total_adults > 0 else 0
            non_iconic_adults_pct = (stats['adults']['total_non_iconic_occurrences'] / total_adults * 100) if total_adults > 0 else 0
            
            iconic_adults.append(iconic_adults_pct)
            non_iconic_adults.append(non_iconic_adults_pct)
        
        # Crear la gráfica
        fig, ax = plt.subplots(figsize=(12, 6))
        x = np.arange(len(age_groups))
        width = 0.35
        
        # Dibujar las barras
        bars1 = ax.bar(x - width/2, iconic_adults, width, label='Palabras Icónicas')
        bars2 = ax.bar(x + width/2, non_iconic_adults, width, label='Palabras No Icónicas')
        
        # Configurar la gráfica
        ax.set_xlabel('Grupo de Edad')
        ax.set_ylabel('Porcentaje de Palabras (%)')
        ax.set_title('Proporción de Palabras Icónicas vs No Icónicas por Grupo de Edad (Adultos)')
        ax.set_xticks(x)
        ax.set_xticklabels(age_groups)
        ax.legend()
        
        # Añadir valores sobre las barras
        def add_labels(bars):
            for bar in bars:
                height = bar.get_height()
                ax.annotate(f'{height:.1f}%',
                          xy=(bar.get_x() + bar.get_width() / 2, height),
                          xytext=(0, 3),
                          textcoords="offset points",
                          ha='center', va='bottom')
        
        add_labels(bars1)
        add_labels(bars2)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path)
        else:
            plt.show()
        plt.close()

    def plot_iconic_vs_non_iconic_by_age_children(self, save_path: str = None):
        """
        Crea una gráfica de barras mostrando la proporción de palabras icónicas y no icónicas por grupo de edad,
        solo para niños, incluyendo los porcentajes.
        
        Args:
            save_path (str, optional): Ruta donde guardar la gráfica. Si es None, la gráfica se muestra en pantalla.
        """
        age_groups = []
        iconic_children = []
        non_iconic_children = []
        
        for age_group, stats in sorted(self.data.items()):
            age_groups.append(age_group)
            
            # Calcular porcentajes para niños
            total_children = stats['children']['total_words']
            iconic_children_pct = (stats['children']['total_iconic_occurrences'] / total_children * 100) if total_children > 0 else 0
            non_iconic_children_pct = (stats['children']['total_non_iconic_occurrences'] / total_children * 100) if total_children > 0 else 0
            
            iconic_children.append(iconic_children_pct)
            non_iconic_children.append(non_iconic_children_pct)
        
        # Crear la gráfica
        fig, ax = plt.subplots(figsize=(12, 6))
        x = np.arange(len(age_groups))
        width = 0.35
        
        # Dibujar las barras
        bars1 = ax.bar(x - width/2, iconic_children, width, label='Palabras Icónicas')
        bars2 = ax.bar(x + width/2, non_iconic_children, width, label='Palabras No Icónicas')
        
        # Configurar la gráfica
        ax.set_xlabel('Grupo de Edad')
        ax.set_ylabel('Porcentaje de Palabras (%)')
        ax.set_title('Proporción de Palabras Icónicas vs No Icónicas por Grupo de Edad (Niños)')
        ax.set_xticks(x)
        ax.set_xticklabels(age_groups)
        ax.legend()
        
        # Añadir valores sobre las barras
        def add_labels(bars):
            for bar in bars:
                height = bar.get_height()
                ax.annotate(f'{height:.1f}%',
                          xy=(bar.get_x() + bar.get_width() / 2, height),
                          xytext=(0, 3),
                          textcoords="offset points",
                          ha='center', va='bottom')
        
        add_labels(bars1)
        add_labels(bars2)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path)
        else:
            plt.show()
        plt.close()

    def plot_iconicity_distribution_by_age_group(self, save_dir: str = None):
        """
        Genera gráficas de distribución acumulativa de iconicidad para cada grupo de edad,
        comparando niños y adultos. El eje Y representa el porcentaje acumulativo de ocurrencias
        de palabras hasta cada valor de iconicidad.
        
        Args:
            save_dir (str, optional): Directorio donde guardar las gráficas. Si es None, las gráficas se muestran en pantalla.
        """
        print_valid_words_statistics(self.data)

        for age_group, stats in sorted(self.data.items()):
            # Obtener las palabras con rating para adultos y niños
            adults_words_with_rating = stats['adults']['iconic_words']
            children_words_with_rating = stats['children']['iconic_words']

            # Verificar si hay datos para adultos y niños
            has_adult_data = len(adults_words_with_rating) > 0
            has_children_data = len(children_words_with_rating) > 0

            if not has_adult_data and not has_children_data:
                print(f"\nNo hay datos de iconicidad para el grupo de edad {age_group}")
                continue

            # Crear listas de (rating, count) para adultos y niños
            adults_ratings_counts = [(word_data['rating'], word_data['count']) 
                                   for word_data in adults_words_with_rating.values()]
            children_ratings_counts = [(word_data['rating'], word_data['count']) 
                                     for word_data in children_words_with_rating.values()]

            # Obtener total de palabras para adultos y niños
            total_adults = stats['adults']['total_iconic_occurrences']
            total_children = stats['children']['total_iconic_occurrences']

            # Obtener mínimo y máximo de iconicidad
            min_rating = float('inf')
            max_rating = float('-inf')

            if has_adult_data:
                min_rating = min(min_rating, min(r for r, _ in adults_ratings_counts))
                max_rating = max(max_rating, max(r for r, _ in adults_ratings_counts))

            if has_children_data:
                min_rating = min(min_rating, min(r for r, _ in children_ratings_counts))
                max_rating = max(max_rating, max(r for r, _ in children_ratings_counts))

            if min_rating == float('inf') or max_rating == float('-inf'):
                print(f"\nNo se pudieron calcular los rangos de iconicidad para el grupo de edad {age_group}")
                continue

            # Crear bins para la iconicidad
            x_axis = np.arange(min_rating, max_rating + 0.25, 0.25)
            
            # Ordenar las palabras por iconicidad
            sorted_adults = sorted(adults_ratings_counts, key=lambda x: x[0])
            sorted_children = sorted(children_ratings_counts, key=lambda x: x[0])

            # Crear listas para acumular ocurrencias
            adults_cumulative = np.zeros(len(x_axis))
            children_cumulative = np.zeros(len(x_axis))

            # Acumular ocurrencias para adultos
            if has_adult_data:
                current_count = 0
                current_bin = 0
                for rating, count in sorted_adults:
                    if current_bin < len(x_axis) and rating > x_axis[current_bin]:
                        adults_cumulative[current_bin] = current_count
                        current_bin += 1
                    current_count += count

                # Actualizar el último bin y los restantes
                for i in range(current_bin, len(x_axis)):
                    adults_cumulative[i] = current_count

            # Acumular ocurrencias para niños
            if has_children_data:
                current_count = 0
                current_bin = 0
                for rating, count in sorted_children:
                    if current_bin < len(x_axis) and rating > x_axis[current_bin]:
                        children_cumulative[current_bin] = current_count
                        current_bin += 1
                    current_count += count

                # Actualizar el último bin y los restantes
                for i in range(current_bin, len(x_axis)):
                    children_cumulative[i] = current_count

            # Crear la gráfica
            plt.figure(figsize=(10, 6))
            
            # Plotear datos de adultos si existen
            if has_adult_data:
                plt.plot(x_axis, adults_cumulative/total_adults * 100, label='Adultos', marker='o', markersize=4)
            
            # Plotear datos de niños si existen
            if has_children_data:
                plt.plot(x_axis, children_cumulative/total_children * 100, label='Niños', marker='s', markersize=4)
            
            plt.xlabel('Iconicidad')
            plt.ylabel('Porcentaje acumulado de palabras (%)')
            plt.title(f'Distribución acumulativa de iconicidad - Grupo {age_group}')
            plt.legend()
            plt.grid(True)
            
            # Guardar o mostrar la gráfica
            if save_dir:
                os.makedirs(save_dir, exist_ok=True)
                plt.savefig(os.path.join(save_dir, f'distribucion_iconicidad_{age_group}.png'), 
                           bbox_inches='tight', dpi=300)
                plt.close()
            else:
                plt.show()
                plt.close()

    def plot_all_adults_iconicity_distribution(self, save_path: str = None):
        """
        Genera una gráfica que muestra la distribución acumulativa de iconicidad para todos los grupos de edad
        de adultos superpuestos en una sola gráfica.
        
        Args:
            save_path (str, optional): Ruta donde guardar la gráfica. Si es None, la gráfica se muestra en pantalla.
        """
        plt.figure(figsize=(12, 8))
        
        # Obtener el rango global de iconicidad
        min_rating = float('inf')
        max_rating = float('-inf')
        
        # Primera pasada para obtener el rango global
        for age_group, stats in sorted(self.data.items()):
            adults_words_with_rating = stats['adults']['iconic_words']
            if adults_words_with_rating:
                ratings = [word_data['rating'] for word_data in adults_words_with_rating.values()]
                min_rating = min(min_rating, min(ratings))
                max_rating = max(max_rating, max(ratings))
        
        if min_rating == float('inf') or max_rating == float('-inf'):
            print("No hay datos de iconicidad para adultos en ningún grupo de edad")
            return
        
        # Crear bins para la iconicidad
        x_axis = np.arange(min_rating, max_rating + 0.25, 0.25)
        
        # Plotear cada grupo de edad
        for age_group, stats in sorted(self.data.items()):
            adults_words_with_rating = stats['adults']['iconic_words']
            if not adults_words_with_rating:
                continue
                
            # Crear lista de (rating, count) y ordenarla
            ratings_counts = [(word_data['rating'], word_data['count']) 
                            for word_data in adults_words_with_rating.values()]
            sorted_ratings = sorted(ratings_counts, key=lambda x: x[0])
            
            # Calcular distribución acumulativa
            total_words = sum(count for _, count in sorted_ratings)
            cumulative = np.zeros(len(x_axis))
            
            current_count = 0
            current_bin = 0
            for rating, count in sorted_ratings:
                while current_bin < len(x_axis) and rating > x_axis[current_bin]:
                    cumulative[current_bin] = current_count
                    current_bin += 1
                current_count += count
            
            # Actualizar el último bin y los restantes
            for i in range(current_bin, len(x_axis)):
                cumulative[i] = current_count
            
            # Plotear la línea para este grupo de edad
            plt.plot(x_axis, cumulative/total_words * 100, 
                    label=f'Grupo {age_group}', 
                    marker='o', 
                    markersize=4,
                    alpha=0.7)
        
        plt.xlabel('Iconicidad')
        plt.ylabel('Porcentaje acumulado de palabras (%)')
        plt.title('Distribución acumulativa de iconicidad para todos los grupos de edad (Adultos)')
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.grid(True)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, bbox_inches='tight', dpi=300)
        else:
            plt.show()
        plt.close()

    def plot_all_children_iconicity_distribution(self, save_path: str = None):
        """
        Genera una gráfica que muestra la distribución acumulativa de iconicidad para todos los grupos de edad
        de niños superpuestos en una sola gráfica.
        
        Args:
            save_path (str, optional): Ruta donde guardar la gráfica. Si es None, la gráfica se muestra en pantalla.
        """
        plt.figure(figsize=(12, 8))
        
        # Obtener el rango global de iconicidad
        min_rating = float('inf')
        max_rating = float('-inf')
        
        # Primera pasada para obtener el rango global
        for age_group, stats in sorted(self.data.items()):
            children_words_with_rating = stats['children']['iconic_words']
            if children_words_with_rating:
                ratings = [word_data['rating'] for word_data in children_words_with_rating.values()]
                min_rating = min(min_rating, min(ratings))
                max_rating = max(max_rating, max(ratings))
        
        if min_rating == float('inf') or max_rating == float('-inf'):
            print("No hay datos de iconicidad para niños en ningún grupo de edad")
            return
        
        # Crear bins para la iconicidad
        x_axis = np.arange(min_rating, max_rating + 0.25, 0.25)
        
        # Plotear cada grupo de edad
        for age_group, stats in sorted(self.data.items()):
            children_words_with_rating = stats['children']['iconic_words']
            if not children_words_with_rating:
                continue
                
            # Crear lista de (rating, count) y ordenarla
            ratings_counts = [(word_data['rating'], word_data['count']) 
                            for word_data in children_words_with_rating.values()]
            sorted_ratings = sorted(ratings_counts, key=lambda x: x[0])
            
            # Calcular distribución acumulativa
            total_words = sum(count for _, count in sorted_ratings)
            cumulative = np.zeros(len(x_axis))
            
            current_count = 0
            current_bin = 0
            for rating, count in sorted_ratings:
                while current_bin < len(x_axis) and rating > x_axis[current_bin]:
                    cumulative[current_bin] = current_count
                    current_bin += 1
                current_count += count
            
            # Actualizar el último bin y los restantes
            for i in range(current_bin, len(x_axis)):
                cumulative[i] = current_count
            
            # Plotear la línea para este grupo de edad
            plt.plot(x_axis, cumulative/total_words * 100, 
                    label=f'Grupo {age_group}', 
                    marker='o', 
                    markersize=4,
                    alpha=0.7)
        
        plt.xlabel('Iconicidad')
        plt.ylabel('Porcentaje acumulado de palabras (%)')
        plt.title('Distribución acumulativa de iconicidad para todos los grupos de edad (Niños)')
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.grid(True)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, bbox_inches='tight', dpi=300)
        else:
            plt.show()
        plt.close()



def print_valid_words_statistics(valid_words_stats):
    """
    Imprime las estadísticas de palabras válidas por grupo de edad.
    
    Args:
        valid_words_stats (dict): Estadísticas de palabras válidas por grupo de edad
    """
    for age_group, stats in sorted(valid_words_stats.items()):
        print(f"\n=== Grupo de edad {age_group} ===")
        
        # Estadísticas de adultos
        print("\nEstadísticas de adultos:")
        print(f"  Total de palabras: {stats['adults']['total_words']}")
        
        # Calcular totales de ocurrencias de palabras icónicas y no icónicas
        total_iconic_occurrences_adults = stats['adults']['total_iconic_occurrences']
        total_non_iconic_occurrences_adults = stats['adults']['total_non_iconic_occurrences']
        
        print(f"  Número total de ocurrencias de palabras icónicas: {total_iconic_occurrences_adults}")
        print(f"  Número total de ocurrencias de palabras no icónicas: {total_non_iconic_occurrences_adults}")
        print(f"  Número de palabras icónicas diferentes: {len(stats['adults']['iconic_words'])}")
        print(f"  Número de palabras no icónicas diferentes: {len(stats['adults']['non_iconic_words'])}")
        
        # Estadísticas de niños
        print("\nEstadísticas de niños:")
        print(f"  Total de palabras: {stats['children']['total_words']}")
        
        # Calcular totales de ocurrencias de palabras icónicas y no icónicas
        total_iconic_occurrences_children = stats['children']['total_iconic_occurrences']
        total_non_iconic_occurrences_children = stats['children']['total_non_iconic_occurrences']
        
        print(f"  Número total de ocurrencias de palabras icónicas: {total_iconic_occurrences_children}")
        print(f"  Número total de ocurrencias de palabras no icónicas: {total_non_iconic_occurrences_children}")
        print(f"  Número de palabras icónicas diferentes: {len(stats['children']['iconic_words'])}")
        print(f"  Número de palabras no icónicas diferentes: {len(stats['children']['non_iconic_words'])}")
