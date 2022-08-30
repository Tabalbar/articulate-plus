class TemporalUtils:
    @staticmethod
    def is_temporal_attribute(entity):
        return TemporalUtils.is_discrete_temporal_attribute(entity) or \
               TemporalUtils.is_continuous_temporal_attribute(entity)

    @staticmethod
    def is_discrete_temporal_attribute(entity):
        return entity in ['month', 'day', 'season', 'time', 'interval']

    @staticmethod
    def is_continuous_temporal_attribute(entity):
        return entity in ['year']

    @staticmethod
    def get_first_temporal_attribute(entities):
        for entity in entities:
            if TemporalUtils.is_temporal_attribute(entity):
                return entity
        return None
