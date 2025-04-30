# -*- coding: utf-8 -*-

from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from radix_tree.radix_config import my_logger

@dataclass
class Container:
    """
    Container populated with data linked to a radic node
    """
    data: Any
    tag: Any = None
    previous: Optional['Container'] = None
    next: Optional['Container'] = None

    def __str__(self):
        return ("Container -> data: %s tag: %s" % (self.data, self.tag))


@dataclass
class Node:
    """
    A radix node
    """
    key: Any
    key_size: int
    data: Optional[Container] = None
    next: Dict = field(default_factory=dict)

    def __str__(self):
        p = hex(id(self))
        if self.data:
            return ("Node %s -> key: %s (%s) key_size: %d next: %s data %s" % (
            p, self.key[0:self.key_size], self.key[self.key_size + 1:], self.key_size, self.next, self.data))
        else:
            return ("Node %s -> key: %s (%s) key_size: %d next: %s" % (
            p, self.key[0:self.key_size], self.key[self.key_size + 1:], self.key_size, self.next))

class RadixTree(object):
    """
    A radix tree
    """

    def __init__(self):
        self._tree = None

    def root_node(self) -> Optional[Node]:
        """
        Return the root node of the radix tree
        :return: root node
        """
        return self._tree

    def insert_node(self, key, val, start_node=None):
        """
        Insert a node in radix tree with a string key
        :param key: string or int key
        :param val: data linked to the node
        :return: new node created
        """
        my_logger.debug(" RadixTree.insert_node() ".center(60, '-'))
        my_logger.debug(" key: %s " % key)

        if type(key) not in [str, bytes, bytearray]:
            key = bin(key).replace('0b', '')
            my_logger.debug("Key converted in string key: %s " % key)

        current = start_node if start_node else self.root_node()

        my_logger.info("Current node: %s " % current)

        if not current:
            """ the radix tree is empty """
            my_logger.debug("Radix tree empty")
            cont = Container(data=val, tag=0)
            node = Node(key=key, key_size=len(key), data=cont)
            self._tree = node
            my_logger.debug(node)
            return cont

        tested = 0
        while tested < current.key_size:
            if tested > len(key) - 1:
                #  Example
                #  key to insert AB
                #  tested = 2
                #  ┏━━━━━━━━━━━━┓B ┏━━━━━━━━━━━━┓
                #  ┃ current    ┃->┃ next node  ┃
                #  ┃ key=ABAB   ┃  ┃ key=ABABB  ┃
                #  ┃ len=4      ┃  ┃ len=5      ┃
                #  ┗━━━━━━━━━━━━┛  ┗━━━━━━━━━━━━┛
                #  Result :
                #  ┏━━━━━━━━━━━━┓A ┏━━━━━━━━━━━━┓B ┏━━━━━━━━━━━━┓
                #  ┃ current    ┃->┃ node1      ┃->┃ next node  ┃
                #  ┃ key=AB     ┃  ┃ key=ABAB   ┃  ┃ key=ABABB  ┃
                #  ┃ len=2      ┃  ┃ len=4      ┃  ┃ len=5      ┃
                #  ┗━━━━━━━━━━━━┛  ┗━━━━━━━━━━━━┛  ┗━━━━━━━━━━━━┛

                cont = Container(data=val, tag=0)
                node1 = Node(key=current.key, key_size=current.key_size, data=None)
                node1.next = current.next.copy()
                node1.data = current.data

                current.key_size = len(key)
                current.next[current.key[tested]] = node1
                current.key = key
                current.data = cont

                my_logger.debug(current)
                my_logger.debug(node1)

                return cont

            elif current.key[tested] != key[tested]:
                """
                Creation of two new nodes and one container for data
                """
                #  Example
                #  key to insert AC
                #  tested = 1
                #  ┏━━━━━━━━━━━━┓  ┏━━━━━━━━━━━━┓
                #  ┃ current    ┃->┃ next node  ┃
                #  ┃ key=ABAB   ┃  ┃ key=ABABB  ┃
                #  ┃ len=4      ┃  ┃ len=5      ┃
                #  ┗━━━━━━━━━━━━┛  ┗━━━━━━━━━━━━┛
                #  Result :
                #  ┏━━━━━━━━━━━━┓B ┏━━━━━━━━━━━━┓  ┏━━━━━━━━━━━━┓
                #  ┃ current    ┃->┃ node1      ┃->┃ next node  ┃
                #  ┃ key=A      ┃  ┃ key=ABAB   ┃  ┃ key=ABABB  ┃
                #  ┃ len=1      ┃  ┃ len=4      ┃  ┃ len=5      ┃
                #  ┗━━━━━━━━━━━━┛  ┗━━━━━━━━━━━━┛  ┗━━━━━━━━━━━━┛
                #        │ C       ┏━━━━━━━━━━━━┓
                #        +-------->┃ node2      ┃
                #                  ┃ key=AC     ┃
                #                  ┃ len=2      ┃
                #                  ┗━━━━━━━━━━━━┛
                cont = Container(data=val, tag=0)
                node1 = Node(key=current.key, key_size=current.key_size, data=None)
                node1.next = current.next.copy()
                node1.data = current.data
                node2 = Node(key=key, key_size=len(key), data=cont)

                current.key_size = tested
                # for k in current.next:
                #    del current.next[k]
                current.next = {}
                current.next[current.key[tested]] = node1
                current.next[key[tested]] = node2
                current.key = key[0:tested]
                current.data = None

                my_logger.debug(current)
                my_logger.debug(node1)
                my_logger.debug(node2)

                return cont
            tested += 1

        if tested == current.key_size:
            if tested < len(key):
                """Go to the next node"""
                if key[tested] in current.next:
                    current = current.next[key[tested]]
                    my_logger.debug("Go to the next node: %s" % current)
                    return self.insert_node(key, val, current)
                else:
                    """Create the new node"""
                    #  Example
                    #  key to insert ABABA
                    #  tested = 4
                    #  ┏━━━━━━━━━━━━┓B ┏━━━━━━━━━━━━┓
                    #  ┃ current    ┃->┃            ┃
                    #  ┃ key=ABAB   ┃  ┃ key=ABABB  ┃
                    #  ┃ len=4      ┃  ┃ len=5      ┃
                    #  ┗━━━━━━━━━━━━┛  ┗━━━━━━━━━━━━┛
                    #  Result :
                    #  ┏━━━━━━━━━━━━┓B ┏━━━━━━━━━━━━┓
                    #  ┃ current    ┃->┃            ┃
                    #  ┃ key=ABAB   ┃  ┃ key=ABABB  ┃
                    #  ┃ len=4      ┃  ┃ len=5      ┃
                    #  ┗━━━━━━━━━━━━┛  ┗━━━━━━━━━━━━┛
                    #        │ A       ┏━━━━━━━━━━━━┓
                    #        +-------->┃ node       ┃
                    #                  ┃ key=ABABA  ┃
                    #                  ┃ len=5      ┃
                    #                  ┗━━━━━━━━━━━━┛

                    cont = Container(data=val, tag=0)
                    node = Node(key=key, key_size=len(key), data=cont)
                    current.next[key[tested]] = node
                    my_logger.debug("Create the next node: %s" % node)
                    my_logger.debug("Modify the current node: %s" % current)
                    return cont
            else:
                """The leaf already exists, we have to update container"""
                my_logger.debug("The leaf already exists, we have to update container node: %s" % current)
                current.key = key
                current.key_size = len(key)
                cont = current.data
                if cont:
                    """Update container"""
                    cont.data = val
                    my_logger.debug("Node already exist. Update container: %s" % current)
                else:
                    """Create container"""
                    my_logger.debug("Node already exist. Create container: %s" % current)
                    cont = Container(data=val, tag=0)
                    current.data = cont
                return cont

    def get_node(self, key, start_node=None):
        """
        Get node in the radix tree beginning to <start_node> indexed by <key>
        :param start_node: first node of the radix tree to explore
        :param key: key to search
        :return: data linked to the node, if any. None otherwise
        """

        my_logger.debug(" RadixTree.get_node() ".center(60, '-'))

        if type(key) not in [str, bytes, bytearray]:
            key = bin(key).replace('0b', '')
            my_logger.debug("Key converted in string key: %s " % key)

        my_logger.debug("key: %s" % key)

        node = start_node if start_node else self.root_node()

        if node:
            my_logger.info("Current node: %s" % node)
            if node.key == key and node.key_size == len(node.key):
                my_logger.info("Node found -> key: %s key_size: %d data: %s" % (node.key, node.key_size, node.data))
                return node.data
            else:
                tested = 0
                while tested < node.key_size:
                    if tested > len(key) - 1:
                        my_logger.warning("Node not found -> key: %s" % key)
                        return None
                    else:
                        my_logger.debug("Searching node... current node: %s " % node)
                        my_logger.debug(
                            "Searching node... index: %d tested: %s - %s" % (tested, node.key[tested], key[tested]))
                        if node.key[tested] != key[tested]:
                            my_logger.warning("Node not found -> key: %s" % key)
                            return None
                        else:
                            tested += 1

                if tested == node.key_size:
                    if key[tested] in node.next:
                        node = node.next[key[tested]]
                        my_logger.info("2 Go to the next node -> next: %s node: %s" % (node.key[tested], node))
                        return self.get_node(key, node)
                    else:
                        my_logger.warning("Node not found -> key: %s" % key)
                        return None
        else:
            my_logger.info("Radix tree empty")
            return None

    def delete_node(self, key, start_node=None, prev_node=None):
        """
        Delete node in radix tree
        :param key: key of the node to delete
        :param start_node: first node of the radix tree or None to start from the beginning of radix tree
        :param prev_node: previous node
        :return: True if deleted. False otherwise.
        """

        my_logger.debug(" RadixTree.delete_node() ".center(60, '-'))

        if type(key) not in [str, bytes, bytearray]:
            key = bin(key).replace('0b', '')
            my_logger.debug("Key converted in string key: %s " % key)

        my_logger.debug(" Key : %s" % key)

        node = start_node if start_node else self.root_node()

        my_logger.info("Current node -> %s" % node)

        if node:
            if node.key == key:
                # Node to delete found
                my_logger.debug("Node to delete found -> %s" % node)
                if len(node.next) == 0:
                    if prev_node == None:
                        my_logger.debug("First node of tree deleted -> Radix tree empty")
                        del self._tree
                        self._tree = None
                        return True
                    else:
                        # Example
                        # Delete 'ABA'
                        # ┏━━━━━━━━━━━━┓A ┏━━━━━━━━━┓
                        # ┃ prev_node  ┃->┃ node    ┃
                        # ┃ key=AB     ┃  ┃ key=ABA ┃
                        # ┃ len=2      ┃  ┃ len=3   ┃
                        # ┗━━━━━━━━━━━━┛  ┗━━━━━━━━━┛
                        # Result :
                        # ┏━━━━━━━━━━━━┓
                        # ┃ prev_node  ┃
                        # ┃ key=AB     ┃
                        # ┃ len=2      ┃
                        # ┗━━━━━━━━━━━━┛

                        my_logger.debug("Node deleted %s " % node)
                        my_logger.debug("Previous link deleted %s " % prev_node)
                        del prev_node.next[node.key[prev_node.key_size]]
                        my_logger.debug("1. Previous node updated %s " % prev_node)

                        if len(prev_node.next) == 1 and prev_node.data == None:
                            # Example
                            # Delete 'ABB'
                            # ┏━━━━━━━━━━━━┓A ┏━━━━━━━━━┓
                            # ┃ prev_node  ┃->┃ node    ┃
                            # ┃ key=AB     ┃  ┃ key=ABA ┃
                            # ┃ len=2      ┃  ┃ len=3   ┃
                            # ┗━━━━━━━━━━━━┛  ┗━━━━━━━━━┛
                            #        │ B       ┏━━━━━━━━━━━━┓
                            #        +-------->┃ other node ┃
                            #                  ┃ key=ABB    ┃
                            #                  ┃ len=3      ┃
                            #                  ┗━━━━━━━━━━━━┛
                            # Result :
                            # ┏━━━━━━━━━━━━┓
                            # ┃ prev_node  ┃
                            # ┃ key=ABA    ┃
                            # ┃ len=3      ┃
                            # ┗━━━━━━━━━━━━┛
                            for k in prev_node.next:
                                prev_node.key = prev_node.next[k].key
                                prev_node.key_size = prev_node.next[k].key_size
                                prev_node.data = prev_node.next[k].data
                                prev_node.next = prev_node.next[k].next
                                my_logger.debug("2. Previous node updated %s " % prev_node)

                        return True
                else:
                    if len(node.next) == 1:
                        # Example
                        # Delete 'ABA'
                        # ┏━━━━━━━━━━━━┓A ┏━━━━━━━━━━━━┓B ┏━━━━━━━━━━━━┓
                        # ┃ prev_node  ┃->┃ node       ┃->┃ next_node  ┃
                        # ┃ key=AB     ┃  ┃ key=ABA    ┃  ┃ key=ABAB   ┃
                        # ┃ len=2      ┃  ┃ len=3      ┃  ┃ len=4      ┃
                        # ┗━━━━━━━━━━━━┛  ┗━━━━━━━━━━━━┛  ┗━━━━━━━━━━━━┛
                        # Result :
                        # ┏━━━━━━━━━━━━┓A ┏━━━━━━━━━━━━┓
                        # ┃ prev_node  ┃->┃ node       ┃
                        # ┃ key=AB     ┃  ┃ key=ABAB   ┃
                        # ┃ len=2      ┃  ┃ len=4      ┃
                        # ┗━━━━━━━━━━━━┛  ┗━━━━━━━━━━━━┛
                        for ke in node.next:
                            next_node = node.next[ke]
                        my_logger.info("Node to update %s " % node)
                        node.key = next_node.key
                        node.key_size = next_node.key_size
                        node.data = next_node.data
                        node.next = next_node.next.copy()
                        my_logger.info("Node updated %s " % node)
                        my_logger.info("Node deleted %s " % next_node)
                        return True
                    else:
                        # Example
                        # Delete 'ABA'
                        # ┏━━━━━━━━━━━━┓A ┏━━━━━━━━━━━━┓B ┏━━━━━━━━━━━━┓
                        # ┃ prev_node  ┃->┃ node       ┃->┃ next_node1 ┃
                        # ┃ key=AB     ┃  ┃ key=ABA    ┃  ┃ key=ABAB   ┃
                        # ┃ len=2      ┃  ┃ len=3      ┃  ┃ len=4      ┃
                        # ┗━━━━━━━━━━━━┛  ┗━━━━━━━━━━━━┛  ┗━━━━━━━━━━━━┛
                        #                       │ C       ┏━━━━━━━━━━━━┓
                        #                       +-------->┃ next_nodei ┃
                        #                                 ┃ key=ABAC   ┃
                        #                                 ┃ len=4      ┃
                        #                                 ┗━━━━━━━━━━━━┛
                        # Result :
                        # ┏━━━━━━━━━━━━┓A ┏━━━━━━━━━━━━┓B ┏━━━━━━━━━━━━┓
                        # ┃ prev_node  ┃->┃ node       ┃->┃ next_node1 ┃
                        # ┃ key=AB     ┃  ┃ key=ABA    ┃  ┃ key=ABAB   ┃
                        # ┃ len=2      ┃  ┃ len=3      ┃  ┃ len=4      ┃
                        # ┗━━━━━━━━━━━━┛  ┗━━━━━━━━━━━━┛  ┗━━━━━━━━━━━━┛
                        #                       │ C       ┏━━━━━━━━━━━━┓
                        #                       +-------->┃ next_nodei ┃
                        #                                 ┃ key=ABAC   ┃
                        #                                 ┃ len=4      ┃
                        #                                 ┗━━━━━━━━━━━━┛
                        # In this case, just delete data linked to the node
                        node.data = None
                        my_logger.info("Just delete data linked to the node %s " % node)
                        return True
            else:
                # Other node case
                tested = 0
                while tested < node.key_size:
                    if tested > len(key) - 1:
                        my_logger.warning("Node not found -> key: %s" % key)
                        return False
                    else:
                        my_logger.debug("Searching node... current node: %s " % node)
                        my_logger.debug(
                            "Searching node... index: %d tested: %s - %s" % (tested, node.key[tested], key[tested]))
                        if node.key[tested] != key[tested]:
                            my_logger.warning("Node not found -> key: %s" % key)
                            return False
                        else:
                            tested += 1

                if tested == node.key_size:
                    if key[tested] in node.next:
                        prev_node = node
                        node = node.next[key[tested]]
                        my_logger.info("Go to the next node -> next: %s node: %s" % (node.key[tested], node))
                        ret = self.delete_node(key, node, prev_node)
                        return ret
                    else:
                        my_logger.warning("Node not found -> key: %s" % key)
                        return False
        else:
            my_logger.info("Radix tree empty")
            return False

    def dump(self, node=None, st_next_line='', print_hex=False):
        """
        Display a radix node
        :param node: first node of the radix tree. If node = None dump the entire radix tree
        :param st_next_line: start of next line to display
        :return: None
        """

        my_logger.debug(" RadixTree.dump() ".center(60, '-'))

        if not node:
            """Dump the entire radix tree"""
            node = self.root_node()
            if not node:
                print("Radix tree empty")
                return
            if node.data:
                line = "■"
            else:
                line = "□"
            key = node.key if not print_hex or type(node.key) is str else bytes(node.key).hex()
            line += " key: %s key_len: %d next: %d" % (key, node.key_size, len(node.next))
            if node.data:
                line += " data: %s" % node.data
            print(line)
            cpt = len(node.next) - 1
            st_next_line = "│" * cpt
            for item in node.next:
                self.dump(node.next[item], st_next_line, print_hex)
                cpt -= 1
                st_next_line = st_next_line[0:cpt]
        else:
            """Intermediate node"""
            line = st_next_line
            if node.data:
                line += "└■"
            else:
                line += "└□"
            key = node.key if not print_hex or type(node.key) is str else bytes(node.key).hex()
            line += " key: %s key_len: %d next: %d" % (key, node.key_size, len(node.next))
            if node.data:
                line += " data: %s" % node.data
            print(line)
            cpt = len(node.next) - 1
            if cpt > 1:
                st_next_line = st_next_line + " │" + "│" * (cpt - 1)
            if cpt == 1:
                my_logger.debug("node with only one son: %s" % node)
                st_next_line = st_next_line + " │"

            for item in node.next:
                self.dump(node.next[item], st_next_line, print_hex)
                l = len(st_next_line) - 1
                st_next_line = st_next_line[0:l]
