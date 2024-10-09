# Name: Andrew Chi
# OSU Email: chia@oregonstate.edu
# Course: CS261 - Data Structures
# Assignment: 6
# Due Date: 06/06/2024
# Description: Open Address Hash Map Implementation.

from a6_include import (DynamicArray, DynamicArrayException, HashEntry,
                        hash_function_1, hash_function_2)


class HashMap:
    def __init__(self, capacity: int, function) -> None:
        """
        Initialize new HashMap that uses
        quadratic probing for collision resolution
        DO NOT CHANGE THIS METHOD IN ANY WAY
        """
        self._buckets = DynamicArray()

        # capacity must be a prime number
        self._capacity = self._next_prime(capacity)
        for _ in range(self._capacity):
            self._buckets.append(None)

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
        Increment from given number to find the closest prime number
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

    # ------------------------------------------------------------------ #

    def put(self, key: str, value: object) -> None:
        """
        Puts element into hash map.
        """
        # Resizes table if necessary
        if self.table_load() >= 0.5:
            self.resize_table(self._capacity*2)

        base_hash, j = self._hash_function(key) % self.get_capacity(), 1
        hash = base_hash
        # If index is empty
        if self._buckets.get_at_index(base_hash) is None:
            self._buckets.set_at_index(base_hash, HashEntry(key, value))
            self._size += 1
        else:
            # If index is full, calls quadratic probe until spot is found
            for _ in range(self.get_capacity()):
                # If empty, insert
                if self._buckets.get_at_index(hash) is None:
                    self._buckets.set_at_index(hash, HashEntry(key, value))
                    self._size += 1
                    break
                # If keys are duplicates, replaces value
                if self._buckets.get_at_index(hash).key == key:
                    self._buckets.get_at_index(hash).value = value
                    if self._buckets.get_at_index(hash).is_tombstone is True:
                        self._size += 1
                        self._buckets.get_at_index(hash).is_tombstone = False
                    break
                # If marked _TS_, replaces values and marks is TS false
                if self._buckets.get_at_index(hash).is_tombstone is True:
                    self._buckets.get_at_index(hash).value = value
                    self._buckets.get_at_index(hash).key = key
                    self._buckets.get_at_index(hash).is_tombstone = False
                    break
                hash = self._rehash(base_hash, j)
                j += 1

    def _rehash(self, base_hash, j):
        """Uses quadratic probing to return new hash value when called."""
        return (base_hash + j ** 2) % self.get_capacity()

    def resize_table(self, new_capacity: int) -> None:
        """
        Resizes the internal hash table. Rehashes all existing elements to duplicate list.
        """
        if new_capacity > self.get_size():
            # Checks if prime, otherwise sets to the closest prime
            if self._is_prime(new_capacity) is False:
                new_capacity = self._next_prime(new_capacity)
            # Creates new DA of size new_capacity
            old_capacity = self._capacity
            self._capacity = new_capacity
            self._size = 0
            old_da = self._buckets
            new_da = DynamicArray()
            self._buckets = new_da
            # Sets new DA to length new_capacity by appending value None
            for _ in range(new_capacity):
                new_da.append(None)
            # Iterates through _buckets, rehashing indexes and moving the elements to new DA
            for _ in range(old_capacity):
                if old_da.get_at_index(_) is not None:
                    old_node = old_da.get_at_index(_)
                    self.put(old_node.key, old_node.value)
                    if old_node.is_tombstone is True:
                        hash = self._hash_function(old_node.key) % self.get_capacity()
                        self._buckets.get_at_index(hash).is_tombstone = True

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
        caps = self._capacity - self._size
        return caps

    def get(self, key: str) -> object:
        """
        Returns the value of an associated key.
        """
        base_hash, j = self._hash_function(key) % self.get_capacity(), 1
        # Hashes to correct index, checks for key/returns value if applicable
        hash = base_hash
        for _ in range(self._capacity):
            if self._buckets.get_at_index(hash) is not None:
                if self._buckets.get_at_index(hash).is_tombstone is True:
                    return None
                if self._buckets.get_at_index(hash).key == key:
                    return self._buckets.get_at_index(hash).value
            j += 1
            hash = self._rehash(base_hash, j)
        return None

    def contains_key(self, key: str) -> bool:
        """
        Returns true if key is in map. Returns false otherwise.
        """
        if self.get(key) is not None:
            return True
        return False

    def remove(self, key: str) -> None:
        """
        If key in list, removes element from list.
        """
        base_hash, j = self._hash_function(key) % self.get_capacity(), 1
        # Gets hash, probes quadratically until finds matching key or fails
        hash = base_hash
        for _ in range(self.get_capacity()):
            if self._buckets.get_at_index(hash) is not None:
                if self._buckets.get_at_index(hash).key == key:
                    if self._buckets.get_at_index(hash).is_tombstone is True:
                        break
                    hash_node = self._buckets.get_at_index(hash)
                    hash_node.is_tombstone = True
                    self._size -= 1
                    break
            j += 1
            hash = self._rehash(base_hash, j)

    def get_keys_and_values(self) -> DynamicArray:
        """
        Returns a list of tuples of the key/value pairs in _buckets.
        """
        new_da = DynamicArray()
        for _ in range(self._capacity):
            if self._buckets.get_at_index(_) is not None and self._buckets.get_at_index(_).is_tombstone is False:
                hash_node = self._buckets.get_at_index(_)
                new_da.append((hash_node.key, hash_node.value))
        return new_da

    def clear(self) -> None:
        """
        Clears the contents of the hash map while keeping capacity.
        """
        self._size = 0
        new_da = DynamicArray()
        for _ in range(self._capacity):
            new_da.append(None)
        self._buckets = new_da

    def __iter__(self):
        """
        Iterator for HashMap. Iterates self when called.
        """
        self._index = 0
        return self

    def __next__(self):
        """
        Advances the iterator.
        """
        try:
            value = self._buckets.get_at_index(self._index)
            while value is None:
                self._index += 1
                value = self._buckets.get_at_index(self._index)
            else:
                self._index += 1
        except DynamicArrayException:
            raise StopIteration

        return value


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
    keys = [i for i in range(25, 1000, 13)]
    for key in keys:
        m.put(str(key), key * 42)
    print(m.get_size(), m.get_capacity())

    for capacity in range(111, 1000, 117):
        m.resize_table(capacity)

        if m.table_load() > 0.5:
            print(f"Check that the load factor is acceptable after the call to resize_table().\n"
                  f"Your load factor is {round(m.table_load(), 2)} and should be less than or equal to 0.5")

        m.put('some key', 'some value')
        result = m.contains_key('some key')
        m.remove('some key')

        for key in keys:
            # all inserted keys must be present
            result &= m.contains_key(str(key))
            # NOT inserted keys must be absent`
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
    m = HashMap(11, hash_function_1)
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

    m.resize_table(2)
    print(m.get_keys_and_values())

    m.put('20', '200')
    m.remove('1')
    m.resize_table(12)
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

    print("\nPDF - __iter__(), __next__() example 1")
    print("---------------------")
    m = HashMap(10, hash_function_1)
    for i in range(5):
        m.put(str(i), str(i * 10))
    print(m)
    for item in m:
        print('K:', item.key, 'V:', item.value)

    print("\nPDF - __iter__(), __next__() example 2")
    print("---------------------")
    m = HashMap(10, hash_function_2)
    for i in range(5):
        m.put(str(i), str(i * 24))
    m.remove('0')
    m.remove('4')
    print(m)
    for item in m:
        print('K:', item.key, 'V:', item.value)
