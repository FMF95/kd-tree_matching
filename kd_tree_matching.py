#!/usr/bin/env python3
"""
Script para emparejar nodos entre dos listas en formato CSV utilizando un KD-Tree.
"""

import argparse
import csv
from typing import List, Union
from scipy.spatial import KDTree

def parse_args():
    """
    Configura los argumentos del script.
    """
    parser = argparse.ArgumentParser(description="Empareja dos listas de nodos en formato CSV utilizando un KD-Tree.")
    parser.add_argument(
        "input_a",
        type=str,
        help="Archivo de entrada para la lista A (CSV con formato ID, x, y, z).",
    )
    parser.add_argument(
        "input_b",
        type=str,
        help="Archivo de entrada para la lista B (CSV con formato ID, x, y, z).",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="output.csv",
        help="Archivo de salida para los emparejamientos (por defecto 'output.csv').",
    )
    return parser.parse_args()


def load_nodes_csv(file_path: str) -> List[List[Union[int, float]]]:
    """
    Carga nodos desde un archivo CSV, ignorando la cabecera (primera línea).
    El archivo debe contener líneas en el formato: ID, x, y, z.
    """
    nodes = []
    with open(file_path, "r") as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Ignora la cabecera (primera línea)
        for row in reader:
            node_id = int(row[0])  # ID del nodo
            coordinates = [float(row[1]), float(row[2]), float(row[3])]  # Coordenadas x, y, z
            nodes.append([node_id] + coordinates)
    return nodes


def create_kdtree(points: List[List[Union[int, float]]]) -> KDTree:
    """
    Crear un KD-Tree utilizando las coordenadas de una lista de nodos.
    Cada nodo tiene la forma [ID, x, y, z].
    """
    coordinates = [point[1:] for point in points]  # Extraer sólo las coordenadas x, y, z
    tree = KDTree(coordinates)
    return tree


def nearest_neighbor_matching(points_a, points_b):
    """
    Encuentra los vecinos más cercanos de forma inyectiva (sin reutilización de nodos).
    Incluye la distancia entre los nodos en el emparejamiento.
    """
    tree_b = create_kdtree(points_b)
    used_ids = set()  # IDs ya utilizados
    matches = []  # Lista de emparejamientos

    for point_a in points_a:
        distances, indices = tree_b.query(point_a[1:], k=len(points_b))

        # Buscar el vecino más cercano que no esté reutilizado
        for idx, distance in zip(indices, distances):
            neighbor = points_b[idx]
            if neighbor[0] not in used_ids:
                # Guardar la pareja con la distancia
                matches.append((point_a[0], neighbor[0], distance))  # (ID_A, ID_B, distancia)
                used_ids.add(neighbor[0])  # Marcar como utilizado el nodo de B
                break

    return matches


def save_matches_csv(matches, file_path):
    """
    Guarda los emparejamientos (ID_A, ID_B, distancia) en un archivo CSV.
    """
    with open(file_path, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["ID_A", "ID_B", "Distance"])  # Cabecera
        writer.writerows(matches)


def main():
    """
    Función principal del script.
    """
    args = parse_args()

    # Cargar las dos listas de nodos desde los archivos CSV
    points_a = load_nodes_csv(args.input_a)
    points_b = load_nodes_csv(args.input_b)

    # Realizar el emparejamiento
    matches = nearest_neighbor_matching(points_a, points_b)

    # Guardar resultados en el archivo de salida
    save_matches_csv(matches, args.output)
    print(f"Emparejamientos guardados en: {args.output}")


if __name__ == "__main__":
    main()