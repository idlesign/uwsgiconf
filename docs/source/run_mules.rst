Mules
=====

.. code-block:: python

    from uwsgiconf.runtime.mules import Mule, Farm

    first_mule = Mule(1)

    @first_mule.offload()
    def for_mule(*args, **kwargs):
        # This function will be offloaded to and handled by mule 1.
        ...

    farm_two = Farm('two')

    @farm_two.offload()
    def for_farm(*args, **kwargs):
        # And this one will be offloaded to farm `two` and handled by any mule from that farm.
        ...


.. automodule:: uwsgiconf.runtime.mules
   :members:
