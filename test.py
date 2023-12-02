#!/usr/bin/env python3


class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age


people = set()


people.add(Person("A", 10))
people.add(Person("B", 20))
people.add(Person("B", 20))
people.add(Person("C", 30))

for p in people:
    print(f"{p.name} {p.age}")