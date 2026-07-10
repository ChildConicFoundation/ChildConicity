import os
from typing import Dict, Any

import numpy as np

try:
    import matplotlib.pyplot as plt
except ModuleNotFoundError:
    plt = None

try:
    import seaborn as sns
except ModuleNotFoundError:
    sns = None

class DataAnalysisPlotter:
    """
    Class for analyzing and visualizing word statistics.
    """
    
    def __init__(self, data: Dict[str, Dict[str, Any]]):
        """
        Initializes the data analyzer with statistical data.
        
        Args:
            data (Dict[str, Dict[str, Any]]): Dictionary with word statistics.
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
        if sns is not None:
            sns.set_theme(style="whitegrid")
            sns.set_palette("husl")

    def _require_plotting_backend(self):
        if plt is None:
            raise ModuleNotFoundError(
                "matplotlib is not installed and is required to generate plots."
            )
        
    def _validate_data(self) -> bool:
        """
        Validates that data has the correct format.
        
        Returns:
            bool: True if the data is valid, False otherwise.
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
        Creates a bar plot showing the proportion of iconic and non-iconic words by age group, for children and adults.
        Without showing percentages to keep the plot clean.
        
        Args:
            save_path (str, optional): Path where the plot should be saved. If None, the plot is shown on screen.
        """
        self._require_plotting_backend()
        age_groups = []
        iconic_children = []
        non_iconic_children = []
        iconic_adults = []
        non_iconic_adults = []
        
        for age_group, stats in sorted(self.data.items()):
            age_groups.append(age_group)
            
            # Calculate percentages for children
            total_children = stats['children']['total_words']
            iconic_children_pct = (stats['children']['total_iconic_occurrences'] / total_children * 100) if total_children > 0 else 0
            non_iconic_children_pct = (stats['children']['total_non_iconic_occurrences'] / total_children * 100) if total_children > 0 else 0
            
            # Calculate percentages for adults
            total_adults = stats['adults']['total_words']
            iconic_adults_pct = (stats['adults']['total_iconic_occurrences'] / total_adults * 100) if total_adults > 0 else 0
            non_iconic_adults_pct = (stats['adults']['total_non_iconic_occurrences'] / total_adults * 100) if total_adults > 0 else 0
            
            iconic_children.append(iconic_children_pct)
            non_iconic_children.append(non_iconic_children_pct)
            iconic_adults.append(iconic_adults_pct)
            non_iconic_adults.append(non_iconic_adults_pct)
        
        # Create the plot
        fig, ax = plt.subplots(figsize=(12, 6))
        x = np.arange(len(age_groups))
        width = 0.2
        
        # Draw bars
        ax.bar(x - 1.5*width, iconic_children, width, label='Children - Iconic')
        ax.bar(x - 0.5*width, non_iconic_children, width, label='Children - Non-iconic')
        ax.bar(x + 0.5*width, iconic_adults, width, label='Adults - Iconic')
        ax.bar(x + 1.5*width, non_iconic_adults, width, label='Adults - Non-iconic')
        
        # Configure the plot
        ax.set_xlabel('Age Group')
        ax.set_ylabel('Word Percentage (%)')
        ax.set_title('Proportion of Iconic vs Non-iconic Words by Age Group')
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
        Creates a bar plot showing the proportion of iconic and non-iconic words by age group,
        for adults only, including percentages.
        
        Args:
            save_path (str, optional): Path where the plot should be saved. If None, the plot is shown on screen.
        """
        self._require_plotting_backend()
        age_groups = []
        iconic_adults = []
        non_iconic_adults = []
        
        for age_group, stats in sorted(self.data.items()):
            age_groups.append(age_group)
            
            # Calculate percentages for adults
            total_adults = stats['adults']['total_words']
            iconic_adults_pct = (stats['adults']['total_iconic_occurrences'] / total_adults * 100) if total_adults > 0 else 0
            non_iconic_adults_pct = (stats['adults']['total_non_iconic_occurrences'] / total_adults * 100) if total_adults > 0 else 0
            
            iconic_adults.append(iconic_adults_pct)
            non_iconic_adults.append(non_iconic_adults_pct)
        
        # Create the plot
        fig, ax = plt.subplots(figsize=(12, 6))
        x = np.arange(len(age_groups))
        width = 0.35
        
        # Draw bars
        bars1 = ax.bar(x - width/2, iconic_adults, width, label='Iconic Words')
        bars2 = ax.bar(x + width/2, non_iconic_adults, width, label='Non-iconic Words')
        
        # Configure the plot
        ax.set_xlabel('Age Group')
        ax.set_ylabel('Word Percentage (%)')
        ax.set_title('Proportion of Iconic vs Non-iconic Words by Age Group (Adults)')
        ax.set_xticks(x)
        ax.set_xticklabels(age_groups)
        ax.legend()
        
        # Add values above the bars
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
        Creates a bar plot showing the proportion of iconic and non-iconic words by age group,
        for children only, including percentages.
        
        Args:
            save_path (str, optional): Path where the plot should be saved. If None, the plot is shown on screen.
        """
        self._require_plotting_backend()
        age_groups = []
        iconic_children = []
        non_iconic_children = []
        
        for age_group, stats in sorted(self.data.items()):
            age_groups.append(age_group)
            
            # Calculate percentages for children
            total_children = stats['children']['total_words']
            iconic_children_pct = (stats['children']['total_iconic_occurrences'] / total_children * 100) if total_children > 0 else 0
            non_iconic_children_pct = (stats['children']['total_non_iconic_occurrences'] / total_children * 100) if total_children > 0 else 0
            
            iconic_children.append(iconic_children_pct)
            non_iconic_children.append(non_iconic_children_pct)
        
        # Create the plot
        fig, ax = plt.subplots(figsize=(12, 6))
        x = np.arange(len(age_groups))
        width = 0.35
        
        # Draw bars
        bars1 = ax.bar(x - width/2, iconic_children, width, label='Iconic Words')
        bars2 = ax.bar(x + width/2, non_iconic_children, width, label='Non-iconic Words')
        
        # Configure the plot
        ax.set_xlabel('Age Group')
        ax.set_ylabel('Word Percentage (%)')
        ax.set_title('Proportion of Iconic vs Non-iconic Words by Age Group (Children)')
        ax.set_xticks(x)
        ax.set_xticklabels(age_groups)
        ax.legend()
        
        # Add values above the bars
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

    def plot_iconicity_distribution_by_age_group(
        self,
        save_dir: str = None,
        filename_prefix: str = "iconicity_distribution",
        title_suffix: str = "",
        print_statistics: bool = True,
        print_warnings: bool = True,
    ):
        """
        Generates cumulative iconicity distribution plots for each age group,
        comparing children and adults. The Y axis represents the cumulative percentage of occurrences
        of words up to each iconicity value.
        
        Args:
            save_dir (str, optional): Directory where plots should be saved. If None, plots are shown on screen.
            filename_prefix (str, optional): Prefix for generated files.
            title_suffix (str, optional): Text to distinguish the plotted data set.
            print_statistics (bool, optional): If True, prints the summary used by the plots.
            print_warnings (bool, optional): If True, warns when a group has no data.
        """
        self._require_plotting_backend()
        if print_statistics:
            print_valid_words_statistics(self.data)

        generated_paths = []

        for age_group, stats in sorted(self.data.items()):
            # Get words with ratings for adults and children
            adults_words_with_rating = stats['adults']['iconic_words']
            children_words_with_rating = stats['children']['iconic_words']

            # Check whether adult and child data exists
            has_adult_data = len(adults_words_with_rating) > 0
            has_children_data = len(children_words_with_rating) > 0

            if not has_adult_data and not has_children_data:
                if print_warnings:
                    print(f"\nNo iconicity data for age group {age_group}")
                continue

            # Create (rating, count) lists for adults and children
            adults_ratings_counts = [(word_data['rating'], word_data['count']) 
                                   for word_data in adults_words_with_rating.values()]
            children_ratings_counts = [(word_data['rating'], word_data['count']) 
                                     for word_data in children_words_with_rating.values()]

            # Get total word counts for adults and children
            total_adults = stats['adults']['total_iconic_occurrences']
            total_children = stats['children']['total_iconic_occurrences']

            # Get minimum and maximum iconicity
            min_rating = float('inf')
            max_rating = float('-inf')

            if has_adult_data:
                min_rating = min(min_rating, min(r for r, _ in adults_ratings_counts))
                max_rating = max(max_rating, max(r for r, _ in adults_ratings_counts))

            if has_children_data:
                min_rating = min(min_rating, min(r for r, _ in children_ratings_counts))
                max_rating = max(max_rating, max(r for r, _ in children_ratings_counts))

            if min_rating == float('inf') or max_rating == float('-inf'):
                if print_warnings:
                    print(f"\nCould not compute iconicity ranges for age group {age_group}")
                continue

            # Create bins for iconicity
            x_axis = np.arange(min_rating, max_rating + 0.25, 0.25)
            
            # Sort words by iconicity
            sorted_adults = sorted(adults_ratings_counts, key=lambda x: x[0])
            sorted_children = sorted(children_ratings_counts, key=lambda x: x[0])

            adults_cumulative = self._calculate_cumulative_counts(
                sorted_adults,
                x_axis,
            )
            children_cumulative = self._calculate_cumulative_counts(
                sorted_children,
                x_axis,
            )

            # Create the plot
            plt.figure(figsize=(10, 6))
            
            # Plot adult data if present
            if has_adult_data:
                plt.plot(x_axis, adults_cumulative/total_adults * 100, label='Adults', marker='o', markersize=4)
            
            # Plot child data if present
            if has_children_data:
                plt.plot(x_axis, children_cumulative/total_children * 100, label='Children', marker='s', markersize=4)
            
            plt.xlabel('Iconicity')
            plt.ylabel('Cumulative word percentage (%)')
            plt.title(f'Cumulative iconicity distribution{title_suffix} - Group {age_group}')
            plt.legend()
            plt.grid(True)
            
            # Save or show the plot
            if save_dir:
                os.makedirs(save_dir, exist_ok=True)
                save_path = os.path.join(save_dir, f'{filename_prefix}_{age_group}.png')
                plt.savefig(save_path, bbox_inches='tight', dpi=300)
                generated_paths.append(save_path)
                plt.close()
            else:
                plt.show()
                plt.close()

        return generated_paths

    def plot_iconicity_distribution_scopes_by_age_group(
        self,
        stats_by_scope: Dict[str, Dict[str, Dict[str, Any]]],
        save_dir: str = None,
        filename_prefix: str = "iconicity_distribution",
        title_suffix: str = "",
        speaker_groups_to_plot=None,
        print_progress: bool = False,
        print_warnings: bool = True,
    ):
        """
        Generates one image per age with several overlaid curves.

        Args:
            stats_by_scope (dict): Map from label to data with the same format
                consumed by DataAnalysisPlotter.
            save_dir (str, optional): Directory where plots should be saved.
            filename_prefix (str, optional): Prefix for generated files.
            title_suffix (str, optional): Text to distinguish the data set.
            speaker_groups_to_plot (iterable, optional): Speaker groups that
                should be drawn. By default draws adults and children.
            print_warnings (bool, optional): If True, warns when a group has no data.
        """
        self._require_plotting_backend()
        generated_paths = []
        age_groups = sorted(
            {
                age_group
                for scoped_stats in stats_by_scope.values()
                for age_group in scoped_stats
            }
        )

        for index, age_group in enumerate(age_groups, start=1):
            if print_progress:
                print(
                    "Rendering plot "
                    f"{index}/{len(age_groups)}: {age_group}"
                )
            series = self._build_iconicity_distribution_series_for_age_group(
                stats_by_scope,
                age_group,
                speaker_groups_to_plot=speaker_groups_to_plot,
            )

            if not series:
                if print_warnings:
                    print(f"\nNo iconicity data for age group {age_group}")
                continue

            min_rating = min(
                rating
                for serie in series
                for rating, _ in serie["ratings_counts"]
            )
            max_rating = max(
                rating
                for serie in series
                for rating, _ in serie["ratings_counts"]
            )
            x_axis = np.arange(min_rating, max_rating + 0.25, 0.25)

            plt.figure(figsize=(12, 8))
            for serie in series:
                cumulative = self._calculate_cumulative_counts(
                    serie["ratings_counts"],
                    x_axis,
                )
                plt.plot(
                    x_axis,
                    cumulative / serie["denominator"] * 100,
                    label=serie["label"],
                    marker=serie["marker"],
                    markersize=3,
                    linewidth=serie["linewidth"],
                    alpha=serie["alpha"],
                )

            plt.xlabel('Iconicity')
            plt.ylabel('Cumulative word percentage (%)')
            plt.title(f'Cumulative iconicity distribution{title_suffix} - Group {age_group}')
            plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            plt.grid(True)
            plt.tight_layout()

            if save_dir:
                os.makedirs(save_dir, exist_ok=True)
                save_path = os.path.join(save_dir, f'{filename_prefix}_{age_group}.png')
                plt.savefig(save_path, bbox_inches='tight', dpi=300)
                generated_paths.append(save_path)
                plt.close()
            else:
                plt.show()
                plt.close()

        return generated_paths

    def _build_iconicity_distribution_series_for_age_group(
        self,
        stats_by_scope,
        age_group,
        speaker_groups_to_plot=None,
    ):
        series = []
        denominators = self._get_total_scope_denominators(stats_by_scope, age_group)
        speaker_groups = self._get_speaker_groups_to_plot(speaker_groups_to_plot)

        for scope_name, scoped_stats in stats_by_scope.items():
            age_stats = scoped_stats.get(age_group)
            if not age_stats:
                continue

            for speaker_group, speaker_label, marker in speaker_groups:
                group_stats = age_stats.get(speaker_group)
                if not group_stats or not group_stats["iconic_words"]:
                    continue

                ratings_counts = [
                    (word_data["rating"], word_data["count"])
                    for word_data in group_stats["iconic_words"].values()
                ]
                total_words = sum(count for _, count in ratings_counts)
                if total_words <= 0:
                    continue

                is_total = scope_name == "total"
                denominator = denominators.get(speaker_group, total_words)
                if denominator <= 0:
                    continue

                series.append(
                    {
                        "label": f"{speaker_label} - {scope_name}",
                        "ratings_counts": ratings_counts,
                        "total_words": total_words,
                        "denominator": denominator,
                        "marker": marker,
                        "linewidth": 2.4 if is_total else 1.3,
                        "alpha": 0.95 if is_total else 0.65,
                    }
                )

        return series

    def _get_speaker_groups_to_plot(self, speaker_groups_to_plot):
        all_speaker_groups = {
            "adults": ("adults", "Adults", "o"),
            "children": ("children", "Children", "s"),
        }

        if speaker_groups_to_plot is None:
            return [
                all_speaker_groups["adults"],
                all_speaker_groups["children"],
            ]

        return [
            all_speaker_groups[speaker_group]
            for speaker_group in speaker_groups_to_plot
            if speaker_group in all_speaker_groups
        ]

    def _get_total_scope_denominators(self, stats_by_scope, age_group):
        total_age_stats = stats_by_scope.get("total", {}).get(age_group, {})
        denominators = {}

        for speaker_group in ("adults", "children"):
            group_stats = total_age_stats.get(speaker_group, {})
            denominators[speaker_group] = group_stats.get(
                "total_iconic_occurrences",
                0,
            )

        return denominators

    def _calculate_cumulative_counts(self, ratings_counts, x_axis):
        sorted_ratings = sorted(ratings_counts, key=lambda x: x[0])
        cumulative = np.zeros(len(x_axis))
        current_count = 0
        current_bin = 0

        for rating, count in sorted_ratings:
            while current_bin < len(x_axis) and rating > x_axis[current_bin]:
                cumulative[current_bin] = current_count
                current_bin += 1
            current_count += count

        for index in range(current_bin, len(x_axis)):
            cumulative[index] = current_count

        return cumulative

    def plot_all_adults_iconicity_distribution(self, save_path: str = None):
        """
        Generates a plot showing the cumulative iconicity distribution for all age groups
        for adults overlaid in a single plot.
        
        Args:
            save_path (str, optional): Path where the plot should be saved. If None, the plot is shown on screen.
        """
        self._require_plotting_backend()
        plt.figure(figsize=(12, 8))
        
        # Get the global iconicity range
        min_rating = float('inf')
        max_rating = float('-inf')
        
        # First pass to get the global range
        for age_group, stats in sorted(self.data.items()):
            adults_words_with_rating = stats['adults']['iconic_words']
            if adults_words_with_rating:
                ratings = [word_data['rating'] for word_data in adults_words_with_rating.values()]
                min_rating = min(min_rating, min(ratings))
                max_rating = max(max_rating, max(ratings))
        
        if min_rating == float('inf') or max_rating == float('-inf'):
            print("No iconicity data for adults in any age group")
            return
        
        # Create bins for iconicity
        x_axis = np.arange(min_rating, max_rating + 0.25, 0.25)
        
        # Plotear cada grupo de edad
        for age_group, stats in sorted(self.data.items()):
            adults_words_with_rating = stats['adults']['iconic_words']
            if not adults_words_with_rating:
                continue
                
            # Create and sort a (rating, count) list
            ratings_counts = [(word_data['rating'], word_data['count']) 
                            for word_data in adults_words_with_rating.values()]
            sorted_ratings = sorted(ratings_counts, key=lambda x: x[0])

            total_words = sum(count for _, count in sorted_ratings)
            cumulative = self._calculate_cumulative_counts(sorted_ratings, x_axis)
            
            # Plot the line for this age group
            plt.plot(x_axis, cumulative/total_words * 100, 
                    label=f'Group {age_group}', 
                    marker='o', 
                    markersize=4,
                    alpha=0.7)
        
        plt.xlabel('Iconicity')
        plt.ylabel('Cumulative word percentage (%)')
        plt.title('Cumulative iconicity distribution for all age groups (Adults)')
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
        Generates a plot showing the cumulative iconicity distribution for all age groups
        for children overlaid in a single plot.
        
        Args:
            save_path (str, optional): Path where the plot should be saved. If None, the plot is shown on screen.
        """
        self._require_plotting_backend()
        plt.figure(figsize=(12, 8))
        
        # Get the global iconicity range
        min_rating = float('inf')
        max_rating = float('-inf')
        
        # First pass to get the global range
        for age_group, stats in sorted(self.data.items()):
            children_words_with_rating = stats['children']['iconic_words']
            if children_words_with_rating:
                ratings = [word_data['rating'] for word_data in children_words_with_rating.values()]
                min_rating = min(min_rating, min(ratings))
                max_rating = max(max_rating, max(ratings))
        
        if min_rating == float('inf') or max_rating == float('-inf'):
            print("No iconicity data for children in any age group")
            return
        
        # Create bins for iconicity
        x_axis = np.arange(min_rating, max_rating + 0.25, 0.25)
        
        # Plotear cada grupo de edad
        for age_group, stats in sorted(self.data.items()):
            children_words_with_rating = stats['children']['iconic_words']
            if not children_words_with_rating:
                continue
                
            # Create and sort a (rating, count) list
            ratings_counts = [(word_data['rating'], word_data['count']) 
                            for word_data in children_words_with_rating.values()]
            sorted_ratings = sorted(ratings_counts, key=lambda x: x[0])

            total_words = sum(count for _, count in sorted_ratings)
            cumulative = self._calculate_cumulative_counts(sorted_ratings, x_axis)
            
            # Plot the line for this age group
            plt.plot(x_axis, cumulative/total_words * 100, 
                    label=f'Group {age_group}', 
                    marker='o', 
                    markersize=4,
                    alpha=0.7)
        
        plt.xlabel('Iconicity')
        plt.ylabel('Cumulative word percentage (%)')
        plt.title('Cumulative iconicity distribution for all age groups (Children)')
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
    Prints valid word statistics by age group.
    
    Args:
        valid_words_stats (dict): Valid word statistics by age group
    """
    for age_group, stats in sorted(valid_words_stats.items()):
        print(f"\n=== Age group {age_group} ===")
        
        # Adult statistics
        print("\nAdult statistics:")
        print(f"  Total words: {stats['adults']['total_words']}")
        
        # Calculate total occurrences of iconic and non-iconic words
        total_iconic_occurrences_adults = stats['adults']['total_iconic_occurrences']
        total_non_iconic_occurrences_adults = stats['adults']['total_non_iconic_occurrences']
        
        print(f"  Total iconic word occurrences: {total_iconic_occurrences_adults}")
        print(f"  Total non-iconic word occurrences: {total_non_iconic_occurrences_adults}")
        print(f"  Unique iconic words: {len(stats['adults']['iconic_words'])}")
        print(f"  Unique non-iconic words: {len(stats['adults']['non_iconic_words'])}")
        
        # Child statistics
        print("\nChildren statistics:")
        print(f"  Total words: {stats['children']['total_words']}")
        
        # Calculate total occurrences of iconic and non-iconic words
        total_iconic_occurrences_children = stats['children']['total_iconic_occurrences']
        total_non_iconic_occurrences_children = stats['children']['total_non_iconic_occurrences']
        
        print(f"  Total iconic word occurrences: {total_iconic_occurrences_children}")
        print(f"  Total non-iconic word occurrences: {total_non_iconic_occurrences_children}")
        print(f"  Unique iconic words: {len(stats['children']['iconic_words'])}")
        print(f"  Unique non-iconic words: {len(stats['children']['non_iconic_words'])}")
