import os
import rdflib

from rdflib import BNode
from pybedtools import BedTool

from askomics.libaskomics.File import File


class BedFile(File):
    """Bed File

    Attributes
    ----------
    public : bool
        Public or private dataset
    """

    def __init__(self, app, session, file_info, host_url=None, external_endpoint=None, custom_uri=None):
        """init

        Parameters
        ----------
        app : Flask
            Flask app
        session :
            AskOmics session
        file_info : dict
            file info
        host_url : None, optional
            AskOmics url
        """
        File.__init__(self, app, session, file_info, host_url, external_endpoint=external_endpoint, custom_uri=custom_uri)

        self.entity_name = ''
        self.category_values = {}
        self.attributes = {}
        self.attribute_abstraction = []
        self.faldo_entity = True

    def set_preview(self):
        """Set entity name preview"""
        self.entity_name = os.path.splitext(self.name)[0]

    def get_preview(self):
        """Get file preview

        Returns
        -------
        dict
            bed file preview
        """
        return {
            'type': self.type,
            'id': self.id,
            'name': self.name,
            "entity_name": self.entity_name
        }

    def integrate(self, entity_name, public=True):
        """Integrate BeD file

        Parameters
        ----------
        entities : List
            Entities to integrate
        public : bool, optional
            Insert in public dataset
        """
        self.public = public
        self.entity_name = entity_name

        File.integrate(self)

    def set_rdf_abstraction_domain_knowledge(self):
        """Set the abstraction and domain knowledge"""
        # Abstraction
        self.graph_abstraction_dk.add((self.askomics_prefix[self.format_uri(self.entity_name, remove_space=True)], rdflib.RDF.type, self.askomics_prefix[self.format_uri("entity")]))
        self.graph_abstraction_dk.add((self.askomics_prefix[self.format_uri(self.entity_name, remove_space=True)], rdflib.RDF.type, self.askomics_prefix[self.format_uri("startPoint")]))
        self.graph_abstraction_dk.add((self.askomics_prefix[self.format_uri(self.entity_name, remove_space=True)], rdflib.RDF.type, self.askomics_prefix[self.format_uri("faldo")]))

        self.graph_abstraction_dk.add((self.askomics_prefix[self.format_uri(self.entity_name, remove_space=True)], rdflib.RDF.type, rdflib.OWL["Class"]))
        self.graph_abstraction_dk.add((self.askomics_prefix[self.format_uri(self.entity_name, remove_space=True)], rdflib.RDFS.label, rdflib.Literal(self.entity_name)))

        for attribute in self.attribute_abstraction:
            for attr_type in attribute["type"]:
                self.graph_abstraction_dk.add((attribute["uri"], rdflib.RDF.type, attr_type))
            self.graph_abstraction_dk.add((attribute["uri"], rdflib.RDFS.label, attribute["label"]))
            self.graph_abstraction_dk.add((attribute["uri"], rdflib.RDFS.domain, attribute["domain"]))
            self.graph_abstraction_dk.add((attribute["uri"], rdflib.RDFS.range, attribute["range"]))

            # Domain Knowledge
            if "values" in attribute.keys():
                for value in attribute["values"]:
                    self.graph_abstraction_dk.add((self.askomics_prefix[self.format_uri(value)], rdflib.RDF.type, self.askomics_prefix[self.format_uri("{}CategoryValue".format(attribute["label"]))]))
                    self.graph_abstraction_dk.add((self.askomics_prefix[self.format_uri(value)], rdflib.RDFS.label, rdflib.Literal(value)))
                    self.graph_abstraction_dk.add((self.askomics_prefix[self.format_uri("{}Category".format(attribute["label"]))], self.askomics_namespace[self.format_uri("category")], self.askomics_prefix[self.format_uri(value)]))

                    if attribute["label"] == rdflib.Literal("strand"):
                        self.graph_abstraction_dk.add((self.askomics_prefix[self.format_uri(value)], rdflib.RDF.type, self.get_faldo_strand(value)))

        # Faldo:
        if self.faldo_entity:
            for key, value in self.faldo_abstraction.items():
                if value:
                    self.graph_abstraction_dk.add((value, rdflib.RDF.type, self.faldo_abstraction_eq[key]))

    def generate_rdf_content(self):
        """Generate RDF content of the BED file

        Yields
        ------
        Graph
            RDF content
        """
        bedfile = BedTool(self.path)

        count = 0
        attribute_list = []

        entity_type = self.askomics_prefix[self.format_uri(self.entity_name, remove_space=True)]

        for feature in bedfile:

            # Entity
            if feature.name != '.':
                entity_label = feature.name
            else:
                entity_label = "{}_{}".format(self.entity_name, str(count))
            count += 1
            entity = self.entity_prefix[self.format_uri(entity_label)]

            self.graph_chunk.add((entity, rdflib.RDF.type, entity_type))
            self.graph_chunk.add((entity, rdflib.RDFS.label, rdflib.Literal(entity_label)))

            # Faldo
            faldo_reference = None
            faldo_strand = None
            faldo_start = None
            faldo_end = None

            # Chromosome
            self.category_values["reference"] = {feature.chrom, }
            relation = self.askomics_prefix[self.format_uri("reference")]
            attribute = self.askomics_prefix[self.format_uri(feature.chrom)]
            faldo_reference = attribute
            self.faldo_abstraction["reference"] = relation
            self.graph_chunk.add((entity, relation, attribute))

            if "reference" not in attribute_list:
                attribute_list.append("reference")
                self.attribute_abstraction.append({
                    "uri": self.askomics_prefix[self.format_uri("reference")],
                    "label": rdflib.Literal("reference"),
                    "type": [self.askomics_prefix[self.format_uri("AskomicsCategory")], rdflib.OWL.ObjectProperty],
                    "domain": entity_type,
                    "range": self.askomics_prefix[self.format_uri("{}Category".format("reference"))],
                    "values": [feature.chrom]
                })
            else:
                # add the value
                for at in self.attribute_abstraction:
                    if at["uri"] == self.askomics_prefix[self.format_uri("reference")] and at["domain"] == entity_type and feature.chrom not in at["values"]:
                        at["values"].append(feature.chrom)

            # Start
            relation = self.askomics_prefix[self.format_uri("start")]
            attribute = rdflib.Literal(self.convert_type(feature.start + 1))  # +1 because bed is 0 based
            faldo_start = attribute
            self.faldo_abstraction["start"] = relation
            self.graph_chunk.add((entity, relation, attribute))

            if "start" not in attribute_list:
                attribute_list.append("start")
                self.attribute_abstraction.append({
                    "uri": self.askomics_prefix[self.format_uri("start")],
                    "label": rdflib.Literal("start"),
                    "type": [rdflib.OWL.DatatypeProperty],
                    "domain": entity_type,
                    "range": rdflib.XSD.decimal
                })

            # End
            relation = self.askomics_prefix[self.format_uri("end")]
            attribute = rdflib.Literal(self.convert_type(feature.end))
            faldo_end = attribute
            self.faldo_abstraction["end"] = relation
            self.graph_chunk.add((entity, relation, attribute))

            if "end" not in attribute_list:
                attribute_list.append("end")
                self.attribute_abstraction.append({
                    "uri": self.askomics_prefix[self.format_uri("end")],
                    "label": rdflib.Literal("end"),
                    "type": [rdflib.OWL.DatatypeProperty],
                    "domain": entity_type,
                    "range": rdflib.XSD.decimal
                })

            # Strand
            strand = False
            if feature.strand == "+":
                self.category_values["strand"] = {"+", }
                relation = self.askomics_prefix[self.format_uri("strand")]
                attribute = self.askomics_prefix[self.format_uri("+")]
                faldo_strand = self.get_faldo_strand("+")
                self.faldo_abstraction["strand"] = relation
                self.graph_chunk.add((entity, relation, attribute))
                strand = True
            elif feature.strand == "-":
                self.category_values["strand"] = {"-", }
                relation = self.askomics_prefix[self.format_uri("strand")]
                attribute = self.askomics_prefix[self.format_uri("-")]
                faldo_strand = self.get_faldo_strand("-")
                self.faldo_abstraction["strand"] = relation
                self.graph_chunk.add((entity, relation, attribute))
                strand = True

            if strand:
                if "strand" not in attribute_list:
                    attribute_list.append("strand")
                    self.attribute_abstraction.append({
                        "uri": self.askomics_prefix[self.format_uri("strand")],
                        "label": rdflib.Literal("strand"),
                        "type": [self.askomics_prefix[self.format_uri("AskomicsCategory")], rdflib.OWL.ObjectProperty],
                        "domain": entity_type,
                        "range": self.askomics_prefix[self.format_uri("{}Category".format("strand"))],
                        "values": ["+", "-"]
                    })

            # Score
            if feature.score != '.':
                relation = self.askomics_prefix[self.format_uri("score")]
                attribute = rdflib.Literal(self.convert_type(feature.score))
                self.graph_chunk.add((entity, relation, attribute))

                if "score" not in attribute_list:
                    attribute_list.append("score")
                    self.attribute_abstraction.append({
                        "uri": self.askomics_prefix[self.format_uri("score")],
                        "label": rdflib.Literal("score"),
                        "type": [rdflib.OWL.DatatypeProperty],
                        "domain": entity_type,
                        "range": rdflib.XSD.decimal
                    })

            location = BNode()
            begin = BNode()
            end = BNode()

            self.graph_chunk.add((entity, self.faldo.location, location))

            self.graph_chunk.add((location, rdflib.RDF.type, self.faldo.region))
            self.graph_chunk.add((location, self.faldo.begin, begin))
            self.graph_chunk.add((location, self.faldo.end, end))

            self.graph_chunk.add((begin, rdflib.RDF.type, self.faldo.ExactPosition))
            self.graph_chunk.add((begin, self.faldo.position, faldo_start))

            self.graph_chunk.add((end, rdflib.RDF.type, self.faldo.ExactPosition))
            self.graph_chunk.add((end, self.faldo.position, faldo_end))

            self.graph_chunk.add((begin, self.faldo.reference, faldo_reference))
            self.graph_chunk.add((end, self.faldo.reference, faldo_reference))

            if faldo_strand:
                self.graph_chunk.add((begin, rdflib.RDF.type, faldo_strand))
                self.graph_chunk.add((end, rdflib.RDF.type, faldo_strand))

            yield
