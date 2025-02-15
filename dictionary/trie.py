class TrieNode:
    def __init__(self, letter, is_end_of_word=False, max_child_depth=0):
        self.letter = letter
        self.is_end_of_word = is_end_of_word
        self.max_child_depth = max_child_depth
        self.child = None
        self.next = None

    def find_child(self, letter):
        current = self.child
        while current:
            if current.letter == letter:
                return current
            current = current.next
        return None

    def insert_child(self, letter, is_end_of_word, max_child_depth):
        new_node = TrieNode(letter, is_end_of_word, max_child_depth)
        if not self.child:
            self.child = new_node
        else:
            current = self.child
            while current.next:
                current = current.next
            current.next = new_node

    def each_word(self, prefix, cb):
        if self.is_end_of_word:
            cb(''.join(prefix))
        if self.child:
            self.child.each_word(prefix + [self.letter], cb)
        if self.next:
            self.next.each_word(prefix, cb)

    def same_subtrie(self, other):
        if not other or self.is_end_of_word != other.is_end_of_word:
            return False
        if self.letter != other.letter:
            return False
        if self.max_child_depth != other.max_child_depth:
            return False
        if self.child and not self.child.same_subtrie(other.child):
            return False
        if self.next and not self.next.same_subtrie(other.next):
            return False
        return True

    def prune(self):
        self.is_end_of_word = False
        return 1


class Trie:
    def __init__(self, lexicon, debug=None):
        self.number_of_words = 0
        self.number_of_nodes = 0
        self.max_word_len = 0
        self.min_word_len = float('inf')
        self.first = TrieNode(-1, False)
        self.debug = debug if debug else lambda x: None

        self.debug("\nConstruct Trie and fill from lexicon")
        for word in lexicon:
            self.add_word(word)

        self.debug(f"Trie of {self.number_of_nodes} nodes built from {self.number_of_words} words")

    def add_word(self, word):
        current = self.first
        n_new = 0
        self.max_word_len = max(self.max_word_len, len(word))
        self.min_word_len = min(self.min_word_len, len(word))
        for x in range(len(word)):
            hang_point = current.find_child(word[x]) if current.child else None
            if not hang_point:
                current.insert_child(word[x], x == len(word) - 1, len(word) - x - 1)
                n_new += 1
                current = current.find_child(word[x])
                for y in range(x + 1, len(word)):
                    current.insert_child(word[y], y == len(word) - 1, len(word) - y - 1)
                    n_new += 1
                    current = current.child
                break
            if hang_point.max_child_depth < len(word) - x - 1:
                hang_point.max_child_depth = len(word) - x - 1
            current = hang_point
            if x == len(word) - 1:
                self.debug(f"WARNING input not in alphabetical order {word}")
                current.is_end_of_word = True
        self.number_of_nodes += n_new
        self.number_of_words += 1

    def each_word(self, cb):
        self.first.each_word([], cb)

    def create_reduction_structure(self):
        self.debug("\nCreate reduction structure")

        counts = [0] * (self.max_word_len - self.min_word_len)
        red = []
        queue = []
        current = self.first.child
        while current:
            queue.append(current)
            current = current.next

        added = 0
        while queue:
            current = queue.pop(0)
            if len(red) <= current.max_child_depth:
                red.append([])
            red[current.max_child_depth].append(current)
            counts[current.max_child_depth] += 1
            added += 1
            current = current.child
            while current:
                queue.append(current)
                current = current.next

        for x in range(self.min_word_len, self.max_word_len):
            if counts[x] > 0:
                self.debug(f"{counts[x]} words of length {x}")

        self.debug(f"{added} nodes added to the reduction structure")

        return red

    def find_pruned_nodes(self, red):
        self.debug("\nMark redundant nodes as pruned")
        total_pruned = 0
        for y in range(len(red) - 1, -1, -1):
            number_pruned = 0
            nodes_at_depth = red[y]
            for w in range(len(nodes_at_depth) - 1):
                if nodes_at_depth[w].is_pruned:
                    continue
                for x in range(w + 1, len(nodes_at_depth)):
                    if not nodes_at_depth[x].is_pruned and nodes_at_depth[x].is_first_child:
                        if nodes_at_depth[w].same_subtrie(nodes_at_depth[x]):
                            number_pruned += nodes_at_depth[x].prune()
            self.debug(f"Pruned |{number_pruned}| nodes at depth |{y}|")
            total_pruned += number_pruned
        self.debug(f"Identified a total of {total_pruned} nodes for pruning")
        return total_pruned

    def assign_indices(self):
        self.debug("\nAssign node indices")

        # Clear down any pre-existing indices
        current = self.first.child
        while current:
            current.index = -1
            current = current.next

        queue = []
        node_list = []
        current = self.first.child
        while current:
            queue.append(current)
            current = current.next

        next_index = 0
        while queue:
            current = queue.pop(0)
            if current.index < 0:
                current.index = next_index
                next_index += 1
                node_list.append(current)
                current = current.child
                while current:
                    queue.append(current)
                    current = current.next

        self.debug(f"Assigned {next_index} node indexes")

        return node_list

    def generate_dawg(self):
        red = self.create_reduction_structure()
        pruneable = self.find_pruned_nodes(red)

        trimmed = self.first.child.replace_redundant_nodes(red)
        self.debug(f"Decoupled {trimmed} nodes to eliminate {pruneable} nodes")

        self.number_of_nodes -= pruneable

    def encode(self):
        self.debug("\nGenerate the unsigned integer array")

        nodelist = self.assign_indices()

        if len(nodelist) > 0x3FFFFFFF:
            raise ValueError("Too many nodes remain for integer encoding")

        self.debug(f"\t{len(nodelist)} nodes")
        len_ = 2 * len(nodelist) + 1
        dawg = bytearray(len_ * 4)
        offset = 0
        dawg[offset:offset + 4] = (len(nodelist)).to_bytes(4, 'big')
        offset += 4
        for node in nodelist:
            node_data = node.encode()
            dawg[offset:offset + 4] = node_data[0].to_bytes(4, 'big')
            offset += 4
            dawg[offset:offset + 4] = node_data[1].to_bytes(4, 'big')
            offset += 4

        self.debug(f"\t{len(dawg)} element Uint32Array generated")

        return dawg
