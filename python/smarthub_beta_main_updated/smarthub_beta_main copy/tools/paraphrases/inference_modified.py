import tensorflow as tf
from embeddings import load_sentence_embeddings
from preprocess_data import preprocess_batch
from six.moves import input
from lstm_model import lstm_model
import numpy as np
from pprint import pprint as pp
import json
from nltk.tokenize import word_tokenize as wt

import os
os.environ["CUDA_VISIBLE_DEVICES"] = "0"

class Paraphraser(object):
    '''Heart of the paraphraser model.  This class loads the checkpoint
    into the Tensorflow runtime environment and is responsible for inference.
    Greedy and sampling based approaches are supported
    '''

    def __init__(self, checkpoint):
        """Constructor.  Load vocabulary index, start token, end token, unk id,
        mask_id.  Restore checkpoint.

        Args:
            checkpoint: A path to the checkpoint
        """
        self.word_to_id, self.idx_to_word, self.embedding, self.start_id, self.end_id, self.unk_id, self.mask_id = load_sentence_embeddings()
        self.checkpoint = checkpoint
        gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=0.5)
        self.sess = tf.Session(config=tf.ConfigProto(gpu_options=gpu_options))
        self.model = lstm_model(self.sess, 'infer', 300, self.embedding, self.start_id, self.end_id, self.mask_id)
        saver = tf.train.Saver()
        saver.restore(self.sess, checkpoint)

    def sample_paraphrase(self, sentence, sampling_temp=1.0, how_many=1):
        """Paraphrase by sampling a distribution

        Args:
            sentence (str): A sentence input that will be paraphrased by 
                sampling from distribution.
            sampling_temp (int) : A number between 0 an 1

        Returns:
            str: a candidate paraphrase of the `sentence`
        """

        return self.infer(1, sentence, self.idx_to_word, sampling_temp, how_many)

    def greedy_paraphrase(self, sentence):
        """Paraphrase using greedy sampler
    
        Args:
            sentence : The source sentence to be paraphrased.

        Returns:
            str : a candidate paraphrase of the `sentence`
        """

        return self.infer(0, sentence, self.idx_to_word, 0., 1)


    def infer(self, decoder, source_sent, id_to_vocab, temp, how_many):
        """ Perform inferencing.  In other words, generate a paraphrase
        for the source sentence.

        Args:
            decoder : 0 for greedy, 1 for sampling
            source_sent : source sentence to generate a paraphrase for
            id_to_vocab : dict of vocabulary index to word
            end_id : the end token
            temp : the sampling temperature to use when `decoder` is 1

        Returns:
            str : for the generated paraphrase
        """

        seq_source_words, seq_source_ids = preprocess_batch([ source_sent ] * how_many)
        #print(seq_source_words)
        #print(seq_source_ids)
        seq_source_len = [ len(seq_source) for seq_source in seq_source_ids ]
        #print(seq_source_len)

        feed_dict = {
            self.model['seq_source_ids']: seq_source_ids,
            self.model['seq_source_lengths']: seq_source_len,
            self.model['decoder_technique']: decoder,
            self.model['sampling_temperature']: temp
        }

        feeds = [
            self.model['predictions']
            #model['final_sequence_lengths']
        ]

        predictions = self.sess.run(feeds, feed_dict)[0]
        #print(predictions)
        return self.translate(predictions, decoder, id_to_vocab, seq_source_words[0])

    def translate(self, predictions, decoder, id_to_vocab, seq_source_words):
        """ Translate the vocabulary ids in `predictions` to actual words
        that compose the paraphrase.

        Args:
            predictions : arrays of vocabulary ids
            decoder : 0 for greedy, 1 for sample, 2 for beam
            id_to_vocab : dict of vocabulary index to word

        Returns:
            str : the paraphrase
        """
        translated_predictions = []
        #np_end = np.where(translated_predictions == end_id)
        for sent_pred in predictions:
            translated = []
            for pred in sent_pred:
                word = 'UUNNKK'
                if pred == self.end_id:
                    break
                if pred == self.unk_id:
                    # Search for rare word
                    for seq_source_word in seq_source_words:
                        if seq_source_word not in self.word_to_id:
                            word = seq_source_word
                else:
                    word = id_to_vocab[pred]
                translated.append(word)
            translated_predictions.append(' '.join(translated))
        return translated_predictions

def resolve_contractions(tokens):
    no_contractions = []
    index = 0
    for token in tokens:
        if token == "'s":
            if index-1 >= 0 and tokens[index-1] == 'let':
                no_contractions.append('us')
            else:
                no_contractions.append("is")
        elif token == "'m":
            no_contractions.append("am")
        elif token == "'d":
            no_contractions.append("would")
        elif token == "'ll":
            no_contractions.append("will")
        elif token == "n't":
            if index-1 >= 0 and tokens[index-1] == 'wo':
                no_contractions[len(no_contractions)-1] = 'will'
            if index-1 >= 0 and tokens[index-1] == 'ca':
                no_contractions[len(no_contractions)-1] = 'can'
            if index-1 >= 0 and tokens[index-1] == 'ai':
                no_contractions[len(no_contractions)-1] = 'am'
            no_contractions.append("not")
        elif token == "'ve":
            no_contractions.append("have")
        elif token == "'re":
            no_contractions.append("are")
        elif token == "'em":
            no_contractions.append("them")
        elif token == "na":
            if index-1 >= 0 and tokens[index-1] == 'gon':
                no_contractions[len(no_contractions)-1] = 'going'
            no_contractions.append('to')
        else:
            s = token.replace("'", "")
            if len(s) != 0:
                no_contractions.append(s)
        index += 1
    return no_contractions

def clean(paraphrase):
    paraphrase = paraphrase.replace(' , ',', ')
    paraphrase = paraphrase.replace(' . ','. ')
    paraphrase = paraphrase.replace(' ? ','? ')
    paraphrase = paraphrase.replace(' ! ','! ')
    paraphrase = paraphrase.replace(" ' ","'")
    paraphrase = paraphrase.replace(' ,',',')
    paraphrase = paraphrase.replace(' .','.')
    paraphrase = paraphrase.replace(' ?','?')
    paraphrase = paraphrase.replace(' !','!')
    paraphrase = paraphrase.replace(" '","'")
    paraphrase = ' '.join(resolve_contractions(wt(paraphrase)))

    return paraphrase

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--checkpoint', type=str, help='Checkpoint path')
    args = parser.parse_args()
    paraphraser = Paraphraser(args.checkpoint)

    with open('../../smarthub_beta_main/tools/paraphrases/utterances.txt','r') as f:
        source_sentences = f.read().split(';\n')
    #source_sentences=[]
    #paraphrases_file = open('paraphrases.txt','a+')
    paraphrases_map=dict()
    for idx,source_sentence in enumerate(source_sentences):
        #p = paraphraser.greedy_paraphrase(source_sentence)
        #print(p)
        paraphrases = paraphraser.sample_paraphrase(\
            source_sentence, sampling_temp=0.75, how_many=10)
        print(idx,"Generated",len(paraphrases),"Total phrases for",source_sentence)
        #for i, paraphrase in enumerate(paraphrases):
        #    print("Paraph #{}: {}".format(i, paraphrase))
        paraphrases_map[source_sentence]=[source_sentence]
        for paraphrase in paraphrases:
            paraphrases_map[source_sentence].append(clean(paraphrase))

    with open('../../smarthub_beta_main/tools/paraphrases/paraphrases.json','w') as f:
        json.dump(obj=paraphrases_map,fp=f,indent=4)

if __name__ == '__main__':
    main()

