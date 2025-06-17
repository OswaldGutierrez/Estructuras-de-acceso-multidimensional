# rTree.py

import math

class Rectangle:
    """
    Representa un Rectángulo de Delimitación Mínima (MBR) con coordenadas
    (min_x, min_y, max_x, max_y).
    """
    def __init__(self, min_x, min_y, max_x, max_y):
        self.min_x = min_x
        self.min_y = min_y
        self.max_x = max_x
        self.max_y = max_y

    def area(self):
        """Calcula el área del rectángulo."""
        return (self.max_x - self.min_x) * (self.max_y - self.min_y)

    def contains_point(self, point):
        """Verifica si el rectángulo contiene un punto."""
        px, py = point
        return self.min_x <= px <= self.max_x and self.min_y <= py <= self.max_y

    def intersects(self, other_rect):
        """Verifica si este rectángulo se intersecta con otro."""
        return not (self.min_x > other_rect.max_x or
                    self.max_x < other_rect.min_x or
                    self.min_y > other_rect.max_y or
                    self.max_y < other_rect.min_y)

    def union(self, other_rect):
        """Calcula el MBR que abarca a este rectángulo y otro."""
        new_min_x = min(self.min_x, other_rect.min_x)
        new_min_y = min(self.min_y, other_rect.min_y)
        new_max_x = max(self.max_x, other_rect.max_x)
        new_max_y = max(self.max_y, other_rect.max_y)
        return Rectangle(new_min_x, new_min_y, new_max_x, new_max_y)

    def enlarge_amount(self, other_rect):
        """Calcula cuánto crecería el área si se uniera con otro rectángulo."""
        union_rect = self.union(other_rect)
        return union_rect.area() - self.area()

    def __repr__(self):
        return f"Rect({self.min_x:.1f},{self.min_y:.1f},{self.max_x:.1f},{self.max_y:.1f})"

class Entry:
    """
    Representa una entrada en un nodo del R-Tree.
    Puede ser un MBR de un nodo hijo o un punto de dato.
    """
    def __init__(self, mbr, child_node=None, point=None):
        self.mbr = mbr # Rectangle object
        self.child_node = child_node # None if it's a leaf entry (contains a point)
        self.point = point # None if it's an internal node entry (contains a child_node)

class Node:
    """
    Representa un nodo en el R-Tree.
    Puede ser una hoja (is_leaf = True) o un nodo interno.
    """
    def __init__(self, is_leaf=True):
        self.is_leaf = is_leaf
        self.entries = [] # List of Entry objects
        self.parent = None # Reference to parent node
        self.mbr = None # MBR of all entries in this node

    def add_entry(self, entry):
        self.entries.append(entry)
        # If the entry represents a child node, set its parent reference
        if entry.child_node:
            entry.child_node.parent = self
        self._update_mbr()

    def remove_entry(self, entry):
        # Ensure the entry is in the list before trying to remove
        if entry in self.entries:
            self.entries.remove(entry)
            # If the entry represented a child node, its parent reference is now invalid for that child
            # (since it's being removed from this node). This is usually handled implicitly
            # if the child node is re-added elsewhere or becomes part of a new node.
            self._update_mbr()

    def _update_mbr(self):
        if not self.entries:
            self.mbr = None
            return

        # Calcular el MBR que abarca todas las entradas del nodo
        first_mbr = self.entries[0].mbr
        min_x = first_mbr.min_x
        min_y = first_mbr.min_y
        max_x = first_mbr.max_x
        max_y = first_mbr.max_y

        for i in range(1, len(self.entries)):
            entry_mbr = self.entries[i].mbr
            min_x = min(min_x, entry_mbr.min_x)
            min_y = min(min_y, entry_mbr.min_y)
            max_x = max(max_x, entry_mbr.max_x)
            max_y = max(max_y, entry_mbr.max_y)
        
        self.mbr = Rectangle(min_x, min_y, max_x, max_y)


class RTree:
    """
    Implementación básica de un R-Tree.
    Basado en el algoritmo R-Tree original (Guttman, 1984).
    """
    def __init__(self, max_entries=4, min_entries=2):
        self.max_entries = max_entries # M
        self.min_entries = min_entries # m
        if self.min_entries > self.max_entries / 2:
            raise ValueError("min_entries must be less than or equal to max_entries / 2")
        self.root = Node(is_leaf=True)

    def insertar(self, point):
        # 1. Crear una entrada para el punto
        # Un punto es un MBR de sí mismo.
        point_mbr = Rectangle(point[0], point[1], point[0], point[1])
        new_entry = Entry(mbr=point_mbr, point=point)

        # 2. Encontrar la hoja donde insertar la entrada
        leaf_node = self._choose_subtree(self.root, new_entry)

        # 3. Añadir la entrada a la hoja
        leaf_node.add_entry(new_entry)

        # 4. Manejar el desbordamiento si es necesario y ajustar el árbol
        if len(leaf_node.entries) > self.max_entries:
            self._handle_overflow(leaf_node)
        else:
            self._adjust_tree(leaf_node) # No need to pass new_mbr, it's implicitly handled by _update_mbr

    def _choose_subtree(self, current_node, entry):
        """
        Elige el subárbol donde insertar la nueva entrada.
        Si current_node es una hoja, es el nodo final.
        Si es un nodo interno, elige la entrada que menos necesite agrandarse.
        """
        if current_node.is_leaf:
            return current_node

        # Iterar sobre las entradas del nodo actual (que son MBRs de nodos hijos)
        # y elegir el que minimice el agrandamiento del área
        min_enlargement = float('inf')
        best_child_entry = None
        
        # Guard against empty current_node.entries if called incorrectly, though it shouldn't be.
        if not current_node.entries:
            # Fallback: if somehow an internal node has no entries, treat it as a leaf or return a default.
            # This indicates an inconsistent tree. For a functional R-Tree, internal nodes must have entries.
            # For now, just return current_node to prevent a crash. The R-Tree structure would be compromised.
            return current_node


        for child_entry in current_node.entries:
            enlargement = child_entry.mbr.enlarge_amount(entry.mbr)
            if enlargement < min_enlargement:
                min_enlargement = enlargement
                best_child_entry = child_entry
            elif enlargement == min_enlargement:
                # Si el agrandamiento es el mismo, elegir el de menor área
                if child_entry.mbr.area() < best_child_entry.mbr.area():
                    best_child_entry = child_entry
        
        # It's possible best_child_entry is None if current_node.entries was empty,
        # but we added a guard above. If it's still None, it's an issue.
        if best_child_entry is None or best_child_entry.child_node is None:
            # This should not happen if current_node is not a leaf and has valid entries.
            # This suggests a corrupted internal node (entries without child_node).
            # For now, fallback to current_node to prevent crash, but this indicates a problem.
            return current_node

        return self._choose_subtree(best_child_entry.child_node, entry)

    def _handle_overflow(self, node):
        """
        Maneja el desbordamiento de un nodo, dividiéndolo si es necesario,
        y propagando el cambio hacia arriba.
        """
        node1, node2 = self._split_node(node)

        # Propagar la división
        if node is self.root:
            # Si el nodo dividido era la raíz, crear una nueva raíz
            new_root = Node(is_leaf=False)
            new_root.add_entry(Entry(node1.mbr, child_node=node1))
            new_root.add_entry(Entry(node2.mbr, child_node=node2))
            # The new nodes are now children of new_root. Their parent attribute is set via add_entry.
            self.root = new_root
            # No further propagation upwards from the new root.
        else:
            # Si el nodo dividido NO era la raíz
            parent = node.parent
            
            # Defensive check: if for some reason a non-root node has no parent, stop propagation.
            # This state indicates a broken tree structure.
            if parent is None:
                # This should ideally not happen.
                print(f"Warning: Node {node.mbr} (is_leaf={node.is_leaf}) has no parent but is not the root. Stopping overflow propagation for this branch.")
                return

            # Reconstruct the parent's entries: remove the old entry for 'node'
            # and add two new entries for 'node1' and 'node2'.
            new_parent_entries = []
            old_entry_replaced = False
            for entry in parent.entries:
                if entry.child_node == node: # Found the old entry pointing to 'node'
                    new_parent_entries.append(Entry(node1.mbr, child_node=node1))
                    new_parent_entries.append(Entry(node2.mbr, child_node=node2))
                    old_entry_replaced = True
                else:
                    new_parent_entries.append(entry)
            
            # If for some reason the old entry wasn't found (tree inconsistency)
            # still add the new entries, but it's a sign of a problem.
            if not old_entry_replaced:
                 print(f"Error: Parent node {parent.mbr} does not contain an entry for child node {node.mbr}. Appending new entries.")
                 new_parent_entries.append(Entry(node1.mbr, child_node=node1))
                 new_parent_entries.append(Entry(node2.mbr, child_node=node2))

            parent.entries = new_parent_entries # Update parent's entries list
            
            # Ensure the parent references are correctly set for the new nodes
            # (Node.add_entry should already do this, but explicitly re-setting can't hurt if issues persist)
            node1.parent = parent
            node2.parent = parent

            # Adjust parent's MBR right after its entries are modified.
            parent._update_mbr()

            # If the parent now overflows, handle its overflow recursively
            if len(parent.entries) > self.max_entries:
                self._handle_overflow(parent)
            else:
                # If the parent does not overflow, adjust its MBR upwards in the tree
                self._adjust_tree(parent)

    def _split_node(self, node):
        """
        Divide un nodo desbordado en dos nuevos nodos.
        Aquí implementaremos una estrategia de división cuadrática simple.
        """
        # 1. Elegir las semillas
        seed1, seed2 = self._pick_seeds(node.entries)
        
        # Crear los dos nuevos nodos
        node1 = Node(is_leaf=node.is_leaf)
        node2 = Node(is_leaf=node.is_leaf)

        # Añadir las semillas a los nuevos nodos
        node1.add_entry(seed1)
        node2.add_entry(seed2)

        remaining_entries = [e for e in node.entries if e != seed1 and e != seed2]

        # 2. Asignar las entradas restantes
        # Distribuir hasta que un nodo tenga MAX_ENTRIES - MIN_ENTRIES + 1 entradas,
        # o hasta que no queden entradas.
        while remaining_entries:
            # Check if one group needs to be filled to meet min_entries requirement
            # and the other still has capacity
            if len(node1.entries) + len(remaining_entries) < self.min_entries:
                # All remaining must go to node1 to meet its minimum
                node1.add_entry(remaining_entries.pop(0))
            elif len(node2.entries) + len(remaining_entries) < self.min_entries:
                # All remaining must go to node2 to meet its minimum
                node2.add_entry(remaining_entries.pop(0))
            else:
                # Normal distribution based on minimal enlargement
                entry_to_assign = self._pick_next(node1.mbr, node2.mbr, remaining_entries)
                
                enlargement1 = node1.mbr.enlarge_amount(entry_to_assign.mbr)
                enlargement2 = node2.mbr.enlarge_amount(entry_to_assign.mbr)

                if enlargement1 < enlargement2:
                    node1.add_entry(entry_to_assign)
                elif enlargement2 < enlargement1:
                    node2.add_entry(entry_to_assign)
                else: # If enlargements are equal, choose by area, then by count
                    if node1.mbr.area() < node2.mbr.area():
                        node1.add_entry(entry_to_assign)
                    elif node2.mbr.area() < node1.mbr.area():
                        node2.add_entry(entry_to_assign)
                    else: # If all equal, add to the node with fewer entries
                        if len(node1.entries) < len(node2.entries):
                            node1.add_entry(entry_to_assign)
                        else:
                            node2.add_entry(entry_to_assign)
                remaining_entries.remove(entry_to_assign)
        
        return node1, node2

    def _pick_seeds(self, entries):
        """
        Elige dos entradas para iniciar la división de un nodo.
        Estrategia: elegir las dos entradas que, si se ponen en grupos diferentes,
        resultarían en el MBR de unión más grande (mayor área "muerta" entre ellos).
        """
        max_waste = -1
        seed1 = None
        seed2 = None

        if len(entries) < 2: # Defensive check, should have at least 2 entries to pick seeds
            # This case means split_node was called on a node with < 2 entries, which is invalid for seeds.
            # Return arbitrary first two or raise error.
            # For the R-Tree algorithm, a node only overflows and splits if it exceeds max_entries,
            # so this list should always have at least max_entries + 1 elements.
            return entries[0], entries[1] # This is a fallback and assumes at least 2 entries.


        for i in range(len(entries)):
            for j in range(i + 1, len(entries)):
                e1 = entries[i]
                e2 = entries[j]
                
                union_rect = e1.mbr.union(e2.mbr)
                waste = union_rect.area() - e1.mbr.area() - e2.mbr.area()

                if waste > max_waste:
                    max_waste = waste
                    seed1 = e1
                    seed2 = e2
        
        return seed1, seed2

    def _pick_next(self, mbr1, mbr2, remaining_entries):
        """
        Elige la próxima entrada a asignar a uno de los dos grupos durante la división.
        Estrategia: la entrada cuya asignación maximice la diferencia de agrandamiento.
        """
        max_diff = -1
        best_entry = None

        if not remaining_entries: # Defensive check
            return None # Should not happen if called correctly

        for entry in remaining_entries:
            enlargement1 = mbr1.enlarge_amount(entry.mbr)
            enlargement2 = mbr2.enlarge_amount(entry.mbr)
            diff = abs(enlargement1 - enlargement2)

            if diff > max_diff:
                max_diff = diff
                best_entry = entry
            
        return best_entry

    def _adjust_tree(self, node):
        """
        Ajusta los MBRs de los nodos hacia arriba en el árbol después de una inserción o división.
        """
        current = node
        while current:
            # Recalcular el MBR del nodo actual basado en sus entradas
            current._update_mbr() 
            
            # If the current node is not the root, its updated MBR must be reflected in its parent's entry
            if current.parent:
                found_entry_in_parent = False
                for entry in current.parent.entries:
                    if entry.child_node == current:
                        entry.mbr = current.mbr # Update the MBR reference in the parent's entry
                        found_entry_in_parent = True
                        break
                # If for some reason the entry for current node is not found in its parent,
                # this indicates a tree integrity issue. Print a warning and stop propagation.
                if not found_entry_in_parent:
                    print(f"Warning: Node {current.mbr} has a parent {current.parent.mbr} but parent does not list it as a child entry. MBR propagation stopped for this branch.")
                    break # Stop propagation for this branch if inconsistency detected
            
            current = current.parent

    # --- Consultas ---
    def buscarEnRango(self, query_rect):
        """
        Busca todos los puntos dentro de un rectángulo de consulta dado.
        query_rect es un objeto Rectangle.
        """
        results = []
        self._search_recursive(self.root, query_rect, results)
        return results

    def _search_recursive(self, node, query_rect, results):
        """Función auxiliar recursiva para buscar en rango."""
        if node is None or node.mbr is None or not node.mbr.intersects(query_rect):
            return

        if node.is_leaf:
            # Si es una hoja, verifica los puntos directamente
            for entry in node.entries:
                if entry.point and query_rect.contains_point(entry.point):
                    results.append(entry.point)
        else:
            # Si es un nodo interno, recurre a los hijos cuyos MBRs se intersectan
            for entry in node.entries:
                # Make sure child_node exists before recursing
                if entry.child_node:
                    self._search_recursive(entry.child_node, query_rect, results)
    
    def buscarVecinoMasCercano(self, point_query):
        """
        Busca el vecino más cercano a un punto dado.
        Este es un algoritmo más complejo y podría requerir una cola de prioridad.
        Para una implementación inicial, haremos un escaneo completo si es demasiado complejo.
        Por ahora, una implementación simple de escaneo.
        """
        closest_point = None
        min_dist = float('inf')

        # If the tree is empty
        if not self.root or not self.root.entries:
            return None

        # Auxiliary function to traverse all points in the R-Tree
        def _get_all_points(node):
            all_points = []
            if node is None:
                return []
            
            if node.is_leaf:
                for entry in node.entries:
                    if entry.point:
                        all_points.append(entry.point)
            else:
                for entry in node.entries:
                    if entry.child_node: # Ensure child_node exists
                        all_points.extend(_get_all_points(entry.child_node))
            return all_points
        
        all_points_in_tree = _get_all_points(self.root)

        # Now, find the closest point among them
        if not all_points_in_tree:
            return None

        for p in all_points_in_tree:
            dist = math.dist(p, point_query)
            if dist < min_dist:
                min_dist = dist
                closest_point = p
        
        return closest_point

    def get_all_mbrs(self):
        """
        Obtiene todos los MBRs de los nodos en el árbol para visualización.
        Devuelve una lista de objetos Rectangle.
        """
        mbrs = []
        nodes_to_visit = [self.root]
        
        while nodes_to_visit:
            current_node = nodes_to_visit.pop(0) # Use pop(0) for BFS
            if current_node: # Ensure node is not None
                if current_node.mbr:
                    mbrs.append(current_node.mbr)
                if not current_node.is_leaf:
                    for entry in current_node.entries:
                        if entry.child_node: # Ensure child_node exists
                            nodes_to_visit.append(entry.child_node)
        return mbrs