from uwsgiconf.config import Section, Configuration


print("this line won't print")

not_conf1 = lambda: []

not_conf2 = [1, 2]

configuration = [
    Configuration([
        Section('conf1_1'),
        Section('conf1_2').env('A', 'B')
    ]),
    Section('conf2_1'),
]
