from segmentation_metrics import SegmentationMetrics


def has_data_attrs(utterance):
    return utterance == 'd' or utterance == 'r'


def predict(utterances):
    predictions = []
    for utterance in utterances:
        if utterance == 'r':
            predictions.append('merged')
        else:
            predictions.append('notmerged')
    print("dialogue act prediction: utterances", utterances, "predictions", predictions)
    return predictions


def get_segments(stream):
    start = current_utterance_id = 0  # track current utterance
    segments = []  # final segments.
    processed = []  # running processed utterances.
    while current_utterance_id < len(stream):
        # start of a new context window.
        print("starting new context window...")
        current_utterance_id = start

        # start and end boundaries aligned with current utterance.
        boundary_start = boundary_end = current_utterance_id
        utterance = stream[current_utterance_id]
        print("boundary start", boundary_start,
              "boundary end", boundary_end,
              "utterance", utterance,
              "uttid", current_utterance_id)

        # listen to stream until a data attribrute has been detected.
        # start_window = ['u','u','u',...,'d'] or start_window = ['u','u','u',...,'r']
        print("adding utterances to start window, beginning with uttid", current_utterance_id)
        start_window = []
        while not has_data_attrs(utterance):
            start_window.append(utterance)
            current_utterance_id += 1

            if current_utterance_id >= len(stream):
                break

            utterance = stream[current_utterance_id]
        start_window.append(utterance)
        print("completed adding to start window", start_window, "ending with uttid", current_utterance_id)

        # predict da to determine if we are dealing with ['u','u','u','d'] or ['u','u','u','r'].
        # if start_window = ['u','u','u',...,'r'], it means setup+request = ['u,','u','u','r'].
        # if start_window = ['u','u','u',...,'d'], it means setup = ['d'] and adding
        # ['u','u','u'] as a separate segment.
        da = predict(utterances=[s[0] for s in start_window])[-1]
        processed += start_window
        if da != 'merged':
            print("start window contains data attribute so we need to ignore the start window and start extracting "
                  "setup as part of new context window.")

            # since start of new window, we need to add previous context window first, i.e.,
            # previous context window = ['u,'u','u'].
            boundary_end = current_utterance_id - 1
            segments.append((processed[boundary_start:boundary_end + 1]))
            boundary_start = current_utterance_id
            print("setup starts at the new data attribute (last thing in start_window) with boundary start",
                  boundary_start, " and boundary end", boundary_end)

            # now we are at start of new context window, i.e., setup. add to context until request is found, i.e.,
            # setup+request = ['d', ..., 'r'].
            print("now start adding to setup until a request is detected, starting with uttid", current_utterance_id)
            da = 'setup'
            while da != 'merged':
                current_utterance_id += 1

                if current_utterance_id >= len(stream):
                    break

                utterance = stream[current_utterance_id]
                processed.append(utterance)
                da = predict(utterances=[s[0] for s in processed[boundary_start:]])[-1]
        print("completed adding setup", processed[boundary_start:], "ending with uttid", current_utterance_id - 1)

        # now setup+request = ['u',,,'u','r'] or setup+request=['d',...,'r']
        # next compute the conclusion part of segment.
        print("now start adding to conclusion until a request or data attribute is detected, starting with uttid",
              current_utterance_id + 1)
        current_utterance_id += 1  # increment to start of conclusion.

        if current_utterance_id >= len(stream):
            continue

        # keep adding utterances as part of conclusion.
        utterance = stream[current_utterance_id]
        processed.append(utterance)
        da = predict(utterances=[s[0] for s in processed[boundary_start:]])[-1]
        while da is not 'merged' and not has_data_attrs(utterance):
            current_utterance_id += 1

            if current_utterance_id >= len(stream):
                break

            utterance = stream[current_utterance_id]
            processed.append(utterance)
            da = predict(utterances=[s[0] for s in processed[boundary_start:]])[-1]

        if current_utterance_id >= len(stream):
            continue

        print("now completed adding to conclusion", processed[boundary_start:], "ending with uttid",
              current_utterance_id)

        # context window is complete, however need to modify if request detected:
        # when context window = ['u,'u','u','r','u','u'...,'r'] then modify conclusion so that we add
        # segment = ['u','u','u','r','u',..,'u'] and start new context window = ['r'] (processing to start of loop).
        # when context window = ['d',...,'r','u','u',...,'d'] then just add the whole context window as a segment,
        # i.e., segment = ['d',...,'r','u','u',...,'d']
        if da == 'merged':
            print("last utterance in conclusion is a request, then modify the conclusion to not include the request "
                  "(i.e., backtrack by one utterance) and then add setup+request+concusion to segment")
            processed.pop()
            start = current_utterance_id
            boundary_end = current_utterance_id
            print("adding segment", processed[boundary_start:boundary_end + 1])
            segments.append(processed[boundary_start:boundary_end + 1])
        else:  # otherwise, it was a data attr utterance so include as is part of completed context window.
            print("last utterance in conclusion is data attribute, then add setup+request+concusion to segment")
            start = current_utterance_id + 1
            boundary_end = current_utterance_id
            segments.append(processed[boundary_start:boundary_end + 1])
            print("adding segment", processed[boundary_start:boundary_end + 1])
    return segments


'''
stream (i.e., the input to (simulated) incremental segmentation algorithm):
    u: utterance not containing data attribute.
    r: utterance is request. 
    d: utterance contaning data attribute but is not request.
'''
stream = [
    'u', 'u', 'u', 'r', 'u', 'd', 'u', 'd', 'u', 'u', 'r', 'r', 'r', 'u', 'u', 'd', 'u', 'r', 'd', 'u', 'u', 'd', 'r',
    'd', 'u', 'u', 'u', 'd', 'd', 'd', 'r', 'r', 'd', 'u'
]

'''
expected output of (simlulated) incremental segmentation algorithm.
'''
expected = [
    ['u', 'u', 'u', 'r', 'u', 'd'],
    ['u'],
    ['d', 'u', 'u', 'r'],
    ['r'],
    ['r', 'u', 'u', 'd'],
    ['u', 'r', 'd'],
    ['u', 'u'],
    ['d', 'r', 'd'],
    ['u', 'u', 'u'],
    ['d', 'd', 'd', 'r'],
    ['r', 'd'],
    ['u']
]

'''
actual output of (simulated) incremental segmentation algorithm.
'''
actual = get_segments(stream)

print("Comparing segments")

metrics = SegmentationMetrics(ytrue=expected, ypred=actual)

print("window size", metrics._k)
print("pk", metrics.pk(api='nltk'))
print("window_diff",metrics.pk(api='nltk'))
print("precision", metrics.precision())
print("recall", metrics.recall())
print("f1", metrics.f1())
print("boundary statistics", metrics.statistics())