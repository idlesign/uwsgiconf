from uwsgiconf.config import Section, Configuration


print("this line won't print")

not_conf1 = lambda: []

not_conf2 = [1, 2]

configuration = [

    Configuration([
        Section(),
        Section('conf1_2').env('A', 'B')
    ], alias='uwsgicgf_test1'),

    Section().env('D', 'E'),
]
