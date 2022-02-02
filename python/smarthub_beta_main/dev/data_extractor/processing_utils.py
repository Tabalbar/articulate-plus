import itertools


class ProcessingUtils:
    @staticmethod
    def slice_work_chunks(work_per_process, iterable):
        it = iter(iterable)
        while True:
            chunk = tuple(itertools.islice(it, work_per_process))
            if not chunk:
                return
            yield chunk
