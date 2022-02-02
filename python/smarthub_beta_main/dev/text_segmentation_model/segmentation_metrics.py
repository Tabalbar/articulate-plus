import segeval


class SegmentationMetrics:
    def __init__(self, ytrue, ypred):
        self._ytrue = ytrue
        self._ypred = ypred

        self._ytrue_segments = SegmentationMetrics.get_segment_length_format(self._ytrue)
        self._ypred_segments = SegmentationMetrics.get_segment_length_format(self._ypred)

        self._ytrue_boundary_sets = SegmentationMetrics.get_boundary_set_format(self._ytrue)
        self._ypred_boundary_sets = SegmentationMetrics.get_boundary_set_format(self._ypred)

        self._ytrue_vec = SegmentationMetrics.get_binary_vector_string_format(self._ytrue)
        self._ypred_vec = SegmentationMetrics.get_binary_vector_string_format(self._ypred)

        self._k = SegmentationMetrics.get_average_segment_size(self._ytrue)

        self._confusion_matrix = segeval.boundary_confusion_matrix(self._ytrue_segments, self._ypred_segments)

    def _window_diff_nltk(self, boundary: str = "1", weighted: bool = False):
        """
        *** taken from nltk package ***
        Compute the windowdiff score for a pair of segmentations.  A
        segmentation is any sequence over a vocabulary of two items
        (e.g. "0", "1"), where the specified boundary value is used to
        mark the edge of a segmentation.

            #>>> s1 = "000100000010"
            #>>> s2 = "000010000100"
            #>>> s3 = "100000010000"
            #>>> '%.2f' % windowdiff(s1, s1, 3)
            '0.00'
            #>>> '%.2f' % windowdiff(s1, s2, 3)
            '0.30'
            #>>> '%.2f' % windowdiff(s2, s3, 3)
            '0.80'

        :param seg1: a segmentation
        :type seg1: str or list
        :param seg2: a segmentation
        :type seg2: str or list
        :param k: window width
        :type k: int
        :param boundary: boundary value
        :type boundary: str or int or bool
        :param weighted: use the weighted variant of windowdiff
        :type weighted: boolean
        :rtype: float
        """

        seg1, seg2 = self._ytrue_vec, self._ypred_vec
        k = self._k

        if len(seg1) != len(seg2):
            raise ValueError("Segmentations have unequal length")

        if k is None:
            k = int(round(len(seg1) / (seg1.count(boundary) * 2.0)))

        if k > len(seg1):
            raise ValueError(
                "Window width k should be smaller or equal than segmentation lengths"
            )
        wd = 0
        for i in range(len(seg1) - k + 1):
            ndiff = abs(seg1[i: i + k].count(boundary) - seg2[i: i + k].count(boundary))
            if weighted:
                wd += ndiff
            else:
                wd += min(1, ndiff)
        return float(wd / (len(seg1) - k + 1.0))

    def _pk_nltk(self, boundary="1"):
        """
        *** taken from nltk package ***
        Compute the Pk metric for a pair of segmentations A segmentation
        is any sequence over a vocabulary of two items (e.g. "0", "1"),
        where the specified boundary value is used to mark the edge of a
        segmentation.

        #>>> '%.2f' % pk('0100'*100, '1'*400, 2)
        '0.50'
        #>>> '%.2f' % pk('0100'*100, '0'*400, 2)
        '0.50'
        #>>> '%.2f' % pk('0100'*100, '0100'*100, 2)
        '0.00'

        :param ref: the reference segmentation
        :type ref: str or list
        :param hyp: the segmentation to evaluate
        :type hyp: str or list
        :param k: window size, if None, set to half of the average reference segment length
        :type boundary: str or int or bool
        :param boundary: boundary value
        :type boundary: str or int or bool
        :rtype: float
        """

        ref, hyp = self._ytrue_vec, self._ypred_vec
        k = self._k

        if k is None:
            k = int(round(len(ref) / (ref.count(boundary) * 2.0)))

        err = 0
        for i in range(len(ref) - k + 1):
            r = ref[i: i + k].count(boundary) > 0
            h = hyp[i: i + k].count(boundary) > 0
            if r != h:
                err += 1
        return float(err / (len(ref) - k + 1.0))

    def _pk_segeval(self) -> float:
        return float(segeval.pk(self._ytrue_segments, self._ypred_segments))

    def _window_diff_segeval(self) -> float:
        return float(segeval.window_diff(self._ytrue_segments, self._ypred_segments, window_size=self._k))

    def statistics(self) -> dict:
        statistics = {'near_misses': -1, 'full_misses': -1, 'boundary_matches': -1, 'boundaries': -1,
            'substitutions': -1, 'additions': -1}
        bs = segeval.boundary_statistics(self._ytrue_segments, self._ypred_segments)

        statistics['near_misses'] = len(bs['transpositions'])
        statistics['full_misses'] = len(bs['full_misses'])
        statistics['boundary_matches'] = len(bs['matches'])
        statistics['boundaries'] = bs['boundaries_all']
        statistics['additions'] = len(bs['additions'])
        statistics['substitutions'] = len(bs['substitutions'])

        return statistics

    def pk(self, api='segeval') -> float:
        if api == 'segeval':
            return self._pk_segeval()

        elif api == 'nltk':
            return self._pk_nltk()

    def window_diff(self, api='segeval') -> float:
        if api == 'segeval':
            return self._window_diff_segeval()

        elif api == 'nltk':
            return self._window_diff_nltk()

    def precision(self, average='macro'):
        if average == 'macro':
            return float(segeval.precision(self._confusion_matrix, version=segeval.Average.macro))
        elif average == 'micro':
            return float(segeval.precision(self._confusion_matrix, version=segeval.Average.micro))

    def recall(self, average='macro'):
        if average == 'macro':
            return float(segeval.recall(self._confusion_matrix, version=segeval.Average.macro))
        elif average == 'micro':
            return float(segeval.recall(self._confusion_matrix, version=segeval.Average.micro))

    def f1(self, average='macro'):
        if average == 'macro':
            return float(segeval.fmeasure(self._confusion_matrix, version=segeval.Average.macro))
        elif average == 'micro':
            return float(segeval.fmeasure(self._confusion_matrix, version=segeval.Average.micro))

    def boundary_similarity(self):
        return float(segeval.boundary_similarity(self._ytrue_segments, self._ypred_segments))

    def segmentation_similarity(self):
        return float(segeval.segmentation_similarity(self._ytrue_segments, self._ypred_segments))

    @staticmethod
    def _convert_to_segment_lengths(y: list) -> list:
        return [len(c) for c in y]

    @staticmethod
    def _convert_to_boundary_sets(y: list) -> tuple:
        return tuple(segeval.boundary_string_from_masses(y))

    @staticmethod
    def _convert_to_binary_vector_string(y: tuple) -> str:
        v = [list(x)[0] if len(list(x)) > 0 else 0 for x in y]
        return ''.join([str(c) for c in v])

    @staticmethod
    def get_average_segment_size(y: list) -> int:
        y_v = SegmentationMetrics.get_binary_vector_string_format(y)
        return int(round(len(y_v) / (y_v.count('1') * 2.0)))

    @staticmethod
    def get_segment_length_format(y: list) -> list:
        return SegmentationMetrics._convert_to_segment_lengths(y)

    @staticmethod
    def get_boundary_set_format(y: list) -> tuple:
        return SegmentationMetrics._convert_to_boundary_sets(
            tuple(SegmentationMetrics._convert_to_segment_lengths(y)))

    @staticmethod
    def get_binary_vector_string_format(y: list) -> str:
        return \
            SegmentationMetrics._convert_to_binary_vector_string(
                SegmentationMetrics._convert_to_boundary_sets(
                    SegmentationMetrics._convert_to_segment_lengths(y)))