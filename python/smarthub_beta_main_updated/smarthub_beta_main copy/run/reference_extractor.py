class ReferenceExtractor:
    def __init__(self, reference_component):
        super().__init__()
        self.reference_component = reference_component

    # get all references for a reference component.
    def extract_all_references(self):
        references = []
        for reference_idx, reference in enumerate(self.reference_component):
            data_pair = list(zip(*[(target_vis_id, plot_type) for target_vis_id, plot_type in
                                               zip(reference.get_targetvis_ids_attribute().split(','),
                                                   reference.get_targetvis_plottypes_attribute().split(',')) if
                                                '*' not in target_vis_id]))
            if not data_pair:
                continue

            target_vis_ids, plot_types = data_pair
            if not target_vis_ids:
                continue

            target_vis_id = target_vis_ids[0]
            plot_type = plot_types[0]

            source_vis_id = -1
            if reference.get_sourcevis_ids_attribute():
                source_vis_ids = sorted(
                    [v.strip() for v in reference.get_sourcevis_ids_attribute().split(',') if '*' not in v])

                if source_vis_ids:
                    source_vis_id = source_vis_ids[0]

            referring_expression_infos = []
            referring_expression_words_infos = []
            for referring_expression_info in reference.get_referringexpression_attribute():
                referring_expression_infos.append(referring_expression_info)

                referring_expression_words = referring_expression_info.words
                referring_expression_words = [w.lower() for w in referring_expression_words]
                referring_expression_words_infos.append(referring_expression_words)

            references.append((reference_idx, referring_expression_words_infos, source_vis_id, target_vis_id,
                               plot_type, referring_expression_infos, reference.get_properties_attribute()))

        return references

    # get referring expression info based on which_one.
    #   - if which_one == -1, choose reference corresponding to longest referring expression (i.e., # of words).
    #   - if which_one != -1, choose reference corresponding to position which_one.
    def extract_reference(self, which_one=-1):
        references = self.extract_all_references()

        if not references:
            return -1, None, -1, -1, None, None, None

        if which_one != -1:
            reference_idx, referring_expression_words_infos, source_vis_id, target_vis_id, plot_type, \
                referring_expression_infos, properties = references[which_one]
            return reference_idx, referring_expression_words_infos, source_vis_id, target_vis_id, plot_type, \
                referring_expression_infos, properties

        max_num_of_words = -1
        for idx, reference in enumerate(references):
            reference_idx, referring_expression_words_infos, source_vis_id, target_vis_id, plot_type, \
                referring_expression_infos, properties = reference

            for referring_expression_words_info in referring_expression_words_infos:
                if len(referring_expression_words_info) > max_num_of_words:
                    max_num_of_words = len(referring_expression_words_info)
                    which_one = idx

        reference_idx, referring_expression_words_infos, source_vis_id, target_vis_id, plot_type, \
            referring_expression_infos, properties = references[which_one]
        return reference_idx, referring_expression_words_infos, source_vis_id, target_vis_id, plot_type, \
            referring_expression_infos, properties
