from uwsgiconf.config import Section, Configuration, configure_uwsgi


print("this line won't print")


def get_config():

    configuration = [

        Configuration([
            Section(),
            Section('conf1_2').env('A', 'B')
        ], alias='uwsgicgf_test1'),

        Section().env('D', 'E'),
    ]
    return configuration


configure_uwsgi(get_config)
