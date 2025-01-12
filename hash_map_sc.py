# Name: Andrew Chi
# OSU Email: chia@oregonstate.edu
# Course: CS261 - Data Structures
# Assignment: 6
# Due Date: 06/06/2024
# Description: Separate Chaining Hash Map Implementation.


from a6_include import (DynamicArray, LinkedList,
                        hash_function_1, hash_function_2)


class HashMap:
    def __init__(self,
                 capacity: int = 11,
                 function: callable = hash_function_1) -> None:
        """
        Initialize new HashMap that uses
        separate chaining for collision resolution
        DO NOT CHANGE THIS METHOD IN ANY WAY
        """
        self._buckets = DynamicArray()

        # capacity must be a prime number
        self._capacity = self._next_prime(capacity)
        for _ in range(self._capacity):
            self._buckets.append(LinkedList())

        self._hash_function = function
        self._size = 0

    def __str__(self) -> str:
        """
        Override string method to provide more readable output
        DO NOT CHANGE THIS METHOD IN ANY WAY
        """
        out = ''
        for i in range(self._buckets.length()):
            out += str(i) + ': ' + str(self._buckets[i]) + '\n'
        return out

    def _next_prime(self, capacity: int) -> int:
        """
        Increment from given number and the find the closest prime number
        DO NOT CHANGE THIS METHOD IN ANY WAY
        """
        if capacity % 2 == 0:
            capacity += 1

        while not self._is_prime(capacity):
            capacity += 2

        return capacity

    @staticmethod
    def _is_prime(capacity: int) -> bool:
        """
        Determine if given integer is a prime number and return boolean
        DO NOT CHANGE THIS METHOD IN ANY WAY
        """
        if capacity == 2 or capacity == 3:
            return True

        if capacity == 1 or capacity % 2 == 0:
            return False

        factor = 3
        while factor ** 2 <= capacity:
            if capacity % factor == 0:
                return False
            factor += 2

        return True

    def get_size(self) -> int:
        """
        Return size of map
        DO NOT CHANGE THIS METHOD IN ANY WAY
        """
        return self._size

    def get_capacity(self) -> int:
        """
        Return capacity of map
        DO NOT CHANGE THIS METHOD IN ANY WAY
        """
        return self._capacity

    def get_bucket(self) -> DynamicArray:
        """Returns bucket DA."""
        return self._buckets

    # ------------------------------------------------------------------ #

    def put(self, key: str, value: object) -> None:
        """
        Puts a key/value pair into the array at the index the given hash function determines.
        """
        # Resizes table if necessary
        if self.table_load() >= 1:
            self.resize_table(self._capacity*2)

        hash = self._hash_function(key)
        # If index is empty
        if self._buckets.get_at_index(hash % self.get_capacity()).length() == 0:
            new_ll = hash % self.get_capacity()
            self._size += 1
            self._buckets.get_at_index(new_ll).insert(key, value)
        # If index is not empty
        elif self._buckets.get_at_index(hash % self.get_capacity()) is not None:
            node = self._buckets.get_at_index(hash % self.get_capacity())
            match_node = node.contains(key)
            # Either adds new key/value pair or replaces current key/value pair
            if match_node is not None:
                match_node.value = value
            else:
                self._size += 1
                node.insert(key, value)

    def resize_table(self, new_capacity: int) -> None:
        """
        Resizes the internal hash table. Rehashes all existing elements and duplicates.
        """
        if new_capacity >= 1:
            # If not prime, sets to closest prime
            if self._is_prime(new_capacity) is False:
                new_capacity = self._next_prime(new_capacity)
            # Creates new DA of size new_capacity
            old_capacity = self._capacity
            self._capacity = new_capacity
            self._size = 0
            new_da = DynamicArray()
            old_da = self._buckets
            self._buckets = new_da
            # Sets new DA of appropriate length with LinkedLists at all indexes
            for _ in range(new_capacity):
                new_da.append(LinkedList())
            # Iterates through _buckets, rehashing indexes and moving the elements to new index in new DA
            for _ in range(old_capacity):
                if old_da.get_at_index(_).length() > 0:
                    for _ in old_da.get_at_index(_):
                        current_node = _
                        self.put(current_node.key, current_node.value)

    def table_load(self) -> float:
        """
        Returns the load factor of the table.
        """
        load_factor = self._size / self._capacity
        return load_factor

    def empty_buckets(self) -> int:
        """
        Returns the number of empty buckets in the map.
        """
        caps = 0
        # Iterates through list to find empty buckets because self._size tracks total elements, not filled indexes.
        for _ in range(self._capacity):
            if self._buckets.get_at_index(_).length() == 0:
                caps += 1
        return caps

    def get(self, key: str):
        """
        Returns the value for a given key. If key is not in table, returns None.
        """
        hash = self._hash_function(key)
        # Hash to correct index, compares passed key with keys in linked list
        for _ in self._buckets.get_at_index(hash % self.get_capacity()):
            if _.key == key:
                return _.value
        return None

    def contains_key(self, key: str) -> bool:
        """
        Returns true if key is in map. Returns false otherwise.
        """
        if self.get(key) is not None:
            return True
        return False

    def hasher(self, key):
        """Calls hash function with passed key."""
        return self._hash_function(key) % self._capacity

    def remove(self, key: str) -> None:
        """
        If the key is in the map, removes the key/value pair associated.
        """
        hash = self._hash_function(key)
        if self._buckets.get_at_index(hash % self.get_capacity()).contains(key):
            self._buckets.get_at_index(hash % self.get_capacity()).remove(key)
            self._size -= 1

    def get_keys_and_values(self) -> DynamicArray:
        """
        Returns a list of tuples of the key/value pairs in _buckets.
        """
        new_da = DynamicArray()
        for _ in range(self.get_capacity()):
            if self._buckets.get_at_index(_).length() > 0:
                for x in self._buckets.get_at_index(_):
                    new_da.append((x.key, x.value))
        return new_da

    def clear(self) -> None:
        """
        Clears the contents of the hash map while keeping capacity.
        """
        self._size = 0
        new_da = DynamicArray()
        for _ in range(self._capacity):
            new_da.append(LinkedList())
        self._buckets = new_da


def find_mode(da: DynamicArray) -> tuple[DynamicArray, int]:
    """
    Returns the mode(s) and number of appearances of said mode(s) for the passed DA.
    """
    map = HashMap()
    new_da = DynamicArray()
    max_len = 0
    # Iterates through passed DA. If repeat values, updates key/value pairs to increase value += 1.
    # Very proud of how clean this ended up! Took lots of revision to get here
    for _ in range(da.length()):
        if map.get(da.get_at_index(_)) is None:
            map.put(da.get_at_index(_), 1)
        else:
            val = map.get(da.get_at_index(_))
            map.put(da.get_at_index(_), val+1)

    for _ in range(da.length()):
        key = da.get_at_index(_)
        hash = map.hasher(key)
        value = map.get(key)
        # If key is in map, checks if number of duplicate is > or == to current max_length
        if value is not None:
            # If greater, resets return DA, sets max_len to value, appends key
            if value > max_len:
                max_len = value
                new_da = DynamicArray()
                new_da.append(key)
            # If equal, just appends key
            elif value == max_len:
                new_da.append(key)
            # Removes node from map to avoid repeats
            map.get_bucket().get_at_index(hash).remove(key)
    return new_da, max_len

# ------------------- BASIC TESTING ---------------------------------------- #

if __name__ == "__main__":

    print("\nPDF - put example 1")
    print("-------------------")
    m = HashMap(53, hash_function_1)
    for i in range(150):
        m.put('str' + str(i), i * 100)
        if i % 25 == 24:
            print(m.empty_buckets(), round(m.table_load(), 2), m.get_size(), m.get_capacity())

    print("\nPDF - put example 2")
    print("-------------------")
    m = HashMap(41, hash_function_2)
    for i in range(50):
        m.put('str' + str(i // 3), i * 100)
        if i % 10 == 9:
            print(m.empty_buckets(), round(m.table_load(), 2), m.get_size(), m.get_capacity())

    print("\nPDF - resize example 1")
    print("----------------------")
    m = HashMap(20, hash_function_1)
    m.put('key1', 10)
    print(m.get_size(), m.get_capacity(), m.get('key1'), m.contains_key('key1'))
    m.resize_table(30)
    print(m.get_size(), m.get_capacity(), m.get('key1'), m.contains_key('key1'))

    print("\nPDF - resize example 2")
    print("----------------------")
    m = HashMap(75, hash_function_2)
    keys = [i for i in range(1, 1000, 13)]
    for key in keys:
        m.put(str(key), key * 42)
    print(m.get_size(), m.get_capacity())

    for capacity in range(111, 1000, 117):
        m.resize_table(capacity)

        m.put('some key', 'some value')
        result = m.contains_key('some key')
        m.remove('some key')

        for key in keys:
            # all inserted keys must be present
            result &= m.contains_key(str(key))
            # NOT inserted keys must be absent
            result &= not m.contains_key(str(key + 1))
        print(capacity, result, m.get_size(), m.get_capacity(), round(m.table_load(), 2))

    print("\nPDF - table_load example 1")
    print("--------------------------")
    m = HashMap(101, hash_function_1)
    print(round(m.table_load(), 2))
    m.put('key1', 10)
    print(round(m.table_load(), 2))
    m.put('key2', 20)
    print(round(m.table_load(), 2))
    m.put('key1', 30)
    print(round(m.table_load(), 2))

    print("\nPDF - table_load example 2")
    print("--------------------------")
    m = HashMap(53, hash_function_1)
    for i in range(50):
        m.put('key' + str(i), i * 100)
        if i % 10 == 0:
            print(round(m.table_load(), 2), m.get_size(), m.get_capacity())

    print("\nPDF - empty_buckets example 1")
    print("-----------------------------")
    m = HashMap(101, hash_function_1)
    print(m.empty_buckets(), m.get_size(), m.get_capacity())
    m.put('key1', 10)
    print(m.empty_buckets(), m.get_size(), m.get_capacity())
    m.put('key2', 20)
    print(m.empty_buckets(), m.get_size(), m.get_capacity())
    m.put('key1', 30)
    print(m.empty_buckets(), m.get_size(), m.get_capacity())
    m.put('key4', 40)
    print(m.empty_buckets(), m.get_size(), m.get_capacity())

    print("\nPDF - empty_buckets example 2")
    print("-----------------------------")
    m = HashMap(53, hash_function_1)
    for i in range(150):
        m.put('key' + str(i), i * 100)
        if i % 30 == 0:
            print(m.empty_buckets(), m.get_size(), m.get_capacity())

    print("\nPDF - get example 1")
    print("-------------------")
    m = HashMap(31, hash_function_1)
    print(m.get('key'))
    m.put('key1', 10)
    print(m.get('key1'))

    print("\nPDF - get example 2")
    print("-------------------")
    m = HashMap(151, hash_function_2)
    for i in range(200, 300, 7):
        m.put(str(i), i * 10)
    print(m.get_size(), m.get_capacity())
    for i in range(200, 300, 21):
        print(i, m.get(str(i)), m.get(str(i)) == i * 10)
        print(i + 1, m.get(str(i + 1)), m.get(str(i + 1)) == (i + 1) * 10)

    print("\nPDF - contains_key example 1")
    print("----------------------------")
    m = HashMap(53, hash_function_1)
    print(m.contains_key('key1'))
    m.put('key1', 10)
    m.put('key2', 20)
    m.put('key3', 30)
    print(m.contains_key('key1'))
    print(m.contains_key('key4'))
    print(m.contains_key('key2'))
    print(m.contains_key('key3'))
    m.remove('key3')
    print(m.contains_key('key3'))

    print("\nPDF - contains_key example 2")
    print("----------------------------")
    m = HashMap(79, hash_function_2)
    keys = [i for i in range(1, 1000, 20)]
    for key in keys:
        m.put(str(key), key * 42)
    print(m.get_size(), m.get_capacity())
    result = True
    for key in keys:
        # all inserted keys must be present
        result &= m.contains_key(str(key))
        # NOT inserted keys must be absent
        result &= not m.contains_key(str(key + 1))
    print(result)

    print("\nPDF - remove example 1")
    print("----------------------")
    m = HashMap(53, hash_function_1)
    print(m.get('key1'))
    m.put('key1', 10)
    print(m.get('key1'))
    m.remove('key1')
    print(m.get('key1'))
    m.remove('key4')

    print("\nPDF - get_keys_and_values example 1")
    print("------------------------")
    m = HashMap(11, hash_function_2)
    for i in range(1, 6):
        m.put(str(i), str(i * 10))
    print(m.get_keys_and_values())

    m.put('20', '200')
    m.remove('1')
    m.resize_table(2)
    print(m.get_keys_and_values())

    print("\nPDF - clear example 1")
    print("---------------------")
    m = HashMap(101, hash_function_1)
    print(m.get_size(), m.get_capacity())
    m.put('key1', 10)
    m.put('key2', 20)
    m.put('key1', 30)
    print(m.get_size(), m.get_capacity())
    m.clear()
    print(m.get_size(), m.get_capacity())

    print("\nPDF - clear example 2")
    print("---------------------")
    m = HashMap(53, hash_function_1)
    print(m.get_size(), m.get_capacity())
    m.put('key1', 10)
    print(m.get_size(), m.get_capacity())
    m.put('key2', 20)
    print(m.get_size(), m.get_capacity())
    m.resize_table(100)
    print(m.get_size(), m.get_capacity())
    m.clear()
    print(m.get_size(), m.get_capacity())

    print("\nPDF - find_mode example 1")
    print("-----------------------------")
    da = DynamicArray(["apple", "apple", "grape", "melon", "peach"])
    mode, frequency = find_mode(da)
    print(f"Input: {da}\nMode : {mode}, Frequency: {frequency}")

    print("\nPDF - find_mode example 2")
    print("-----------------------------")
    test_cases = (
        ["Arch", "Manjaro", "Manjaro", "Mint", "Mint", "Mint", "Ubuntu", "Ubuntu", "Ubuntu"],
        ["one", "two", "three", "four", "five"],
        ["2", "4", "2", "6", "8", "4", "1", "3", "4", "5", "7", "3", "3", "2"]
    )

    for case in test_cases:
        da = DynamicArray(case)
        mode, frequency = find_mode(da)
        print(f"Input: {da}\nMode : {mode}, Frequency: {frequency}\n")
