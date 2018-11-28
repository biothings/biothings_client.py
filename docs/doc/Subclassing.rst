Subclassing a Client
====================

The biothings_client **get_client** function generates settings for a biothings client on-the-fly.  However, sometimes a user may want to subclass an existing client.  This can be accomplished by use of the **instance** parameter in the **get_client** function.  Normally the **get_client** function returns an instantiated client object, however if **instance** is False, **get_client** returns the class itself (allowing it to be used as a parent class).  See the following code snippet for an example:

.. code-block:: python

    In [1]: class CustomMyGeneClient(get_client('gene', instance=False)):
       ...:     def getgene(self, _id, fields=None, **kwargs):
       ...:         ''' overridden gene function '''
       ...:         print('Custom Gene function')
       ...:         return super(CustomMyGeneClient, self).getgene(_id=_id, fields=fields, **kwargs)
       ...:

    In [2]: gene_client = CustomMyGeneClient()

    In [3]: gene_client.getgene('1017', fields='symbol,name')
    Custom Gene function
    Out[3]:
    {'_id': '1017',
     '_score': 13.409985,
     'name': 'cyclin dependent kinase 2',
     'symbol': 'CDK2'}

Here we overrode the normal functioning of the **getgene** function in the yGene client.
