from askomics.libaskomics.Params import Params

import rdflib
import json


class PrefixManager(Params):
    """Manage sparql prefixes

    Attributes
    ----------
    namespace_internal : str
        askomics namespace, from config file
    namespace_data : str
        askomics prefix, from config file
    prefix : dict
        dict of all prefixes
    """

    def __init__(self, app, session):
        """init

        Parameters
        ----------
        app : Flask
            Flask app
        session :
            AskOmics session
        """
        Params.__init__(self, app, session)
        self.namespace_data = self.settings.get('triplestore', 'namespace_data')
        self.namespace_internal = self.settings.get('triplestore', 'namespace_internal')

        self.prefix = {
            ':': self.settings.get('triplestore', 'namespace_data'),
            'askomics:': self.settings.get('triplestore', 'namespace_internal'),
            'prov:': 'http://www.w3.org/ns/prov#',
            'dc:': 'http://purl.org/dc/elements/1.1/',
            'faldo:': "http://biohackathon.org/resource/faldo/",
            'rdf:': str(rdflib.RDF),
            'rdfs:': str(rdflib.RDFS),
            'owl:': str(rdflib.OWL),
            'xsd:': str(rdflib.XSD)
        }

    def get_prefix(self):
        """Get all prefixes

        Returns
        -------
        str
            prefixes
        """
        prefix_string = ''
        sorted_keys = sorted(self.prefix)  # We sort because python3.5 don't keep the dict order and it fail the unittest
        for prefix in sorted_keys:
            prefix_string += 'PREFIX {} <{}>\n'.format(prefix, self.prefix[prefix])

        return prefix_string

    def get_namespace(self, prefix):
        """Get a namespace from a prefix

        Parameters
        ----------
        prefix : string
            prefix

        Returns
        -------
        string
            The corresponding namespace
        """
        json_prefix_file = "askomics/libaskomics/prefix.cc.json"
        with open(json_prefix_file) as json_file:
            content = json_file.read()
        prefix_cc = json.loads(content)

        try:
            return prefix_cc[prefix]
        except Exception:
            return ""
