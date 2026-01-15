#!/usr/bin/env python3
"""
Emparejamiento KD-Tree con filtrado por distancia mínima para garantizar
que cada punto de la lista menor solo se asigne al punto más cercano.
"""

import csv
from scipy.spatial import KDTree
from typing import List, Tuple, Union


class NodeLoader:
    """
    Clase encargada de cargar nodos desde archivos CSV.
    """

    @staticmethod
    def load_csv(file_path: str) -> List[List[Union[int, float]]]:
        """
        Carga nodos desde un archivo CSV.
        Cada nodo tiene el formato ID, x, y, z.
        """
        nodes = []
        with open(file_path, "r") as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # Ignora la cabecera
            for row in reader:
                node_id = int(row[0])  # ID del nodo
                coordinates = [float(row[1]), float(row[2]), float(row[3])]
                nodes.append([node_id] + coordinates)
        return nodes


class MatchSaver:
    """
    Clase encargada de guardar los emparejamientos en un archivo CSV.
    """

    @staticmethod
    def save_csv(file_path: str, matches: List[Tuple[int, int, float]]):
        """
        Guarda los emparejamientos (ID_A, ID_B, distancia) en un archivo CSV.
        """
        with open(file_path, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["ID_A", "ID_B", "Distance"])  # Cabecera
            writer.writerows(matches)


class KDTreeMatcher:
    """
    Clase responsable de construir el KD-Tree, realizar el emparejamiento
    y aplicar el filtrado para distancias mínimas.
    """

    def __init__(self, points_a: List[List[Union[int, float]]], points_b: List[List[Union[int, float]]]):
        """
        Inicializa las listas de puntos y determina la lista menor y mayor.
        """
        self.points_a = points_a
        self.points_b = points_b
        self.larger_set, self.smaller_set, self.reverse_output = self._identify_sets()
        self.kdtree = None

    def _identify_sets(self):
        """
        Identifica la lista mayor y menor, y marca si la salida necesita inversión.
        """
        if len(self.points_a) >= len(self.points_b):
            return self.points_a, self.points_b, False  # Mantener el orden ID_A -> ID_B
        else:
            return self.points_b, self.points_a, True  # Cambiar a ID_B -> ID_A

    def build_kdtree(self):
        """
        Construye el KD-Tree para la lista menor.
        """
        coordinates = [point[1:] for point in self.smaller_set]
        self.kdtree = KDTree(coordinates)

    def perform_initial_matching(self) -> List[Tuple[int, int, float]]:
        """
        Realiza el emparejamiento inicial sin restricciones de unicidad, es decir,
        un punto de la lista menor puede ser asignado a múltiples puntos de la lista mayor.
        """
        matches = []
        for point_large in self.larger_set:
            distance, index = self.kdtree.query(point_large[1:])
            neighbor_small = self.smaller_set[index]
            matches.append((point_large[0], neighbor_small[0], distance))  # (ID_A, ID_B, distancia)
        return matches

    def filter_minimum_distances(self, matches: List[Tuple[int, int, float]]) -> List[Tuple[int, int, float]]:
        """
        Filtra las asociaciones para garantizar que cada punto de la lista menor
        esté asignado únicamente al punto más cercano de la lista mayor.
        """
        matches_by_b = {}
        for id_a, id_b, distance in matches:
            # Mantiene el emparejamiento con la menor distancia
            if id_b not in matches_by_b or distance < matches_by_b[id_b][2]:
                matches_by_b[id_b] = (id_a, id_b, distance)

        # Retorna los emparejamientos únicos con las menores distancias
        return list(matches_by_b.values())

    def find_matches(self) -> List[Tuple[int, int, float]]:
        """
        Encuentra las asociaciones finales, asegurando la unicidad y el orden original.
        """
        # Paso 1: Realizar el emparejamiento inicial (no inyectivo)
        initial_matches = self.perform_initial_matching()

        # Paso 2: Filtrar los resultados por distancia mínima
        filtered_matches = self.filter_minimum_distances(initial_matches)

        # Paso 3: Ajustar el orden si las listas fueron invertidas
        if self.reverse_output:
            filtered_matches = [(m[1], m[0], m[2]) for m in filtered_matches]

        return filtered_matches


def main(input_a: str, input_b: str, output: str):
    """
    Función principal que coordina el flujo del script.
    """
    # Cargar los nodos desde los archivos CSV
    nodes_a = NodeLoader.load_csv(input_a)
    nodes_b = NodeLoader.load_csv(input_b)

    # Inicializar el KDTreeMatcher
    matcher = KDTreeMatcher(nodes_a, nodes_b)

    # Construir el KD-Tree utilizando la lista menor
    matcher.build_kdtree()

    # Encontrar las asociaciones finales
    matches = matcher.find_matches()

    # Guardar el resultado en un archivo CSV
    MatchSaver.save_csv(output, matches)

    print(f"Emparejamientos guardados en: {output}")


if __name__ == "__main__":
    import argparse

    # Configurar y parsear argumentos del script
    parser = argparse.ArgumentParser(description="Empareja dos listas utilizando un KD-Tree con filtrado por distancia mínima.")
    parser.add_argument("input_a", type=str, help="Archivo CSV para la lista A (formato: ID,x,y,z).")
    parser.add_argument("input_b", type=str, help="Archivo CSV para la lista B (formato: ID,x,y,z).")
    parser.add_argument("--output", type=str, default="output.csv", help="Archivo CSV de salida (por defecto 'output.csv').")
    args = parser.parse_args()

    # Ejecutar la función principal
    main(args.input_a, args.input_b, args.output)