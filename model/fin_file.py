import pickle
import nltk
from nltk.corpus import stopwords

STANDARD_MODEL_FILENAME = 'top2vec_new.sav'
STANDARD_MODEL = pickle.load(open(STANDARD_MODEL_FILENAME, 'rb'))


class Classifier:
    def __init__(self, user=None):
        self.user = user

    def __enter__(self):
        if(self.user and self.user.model):
            self.model = pickle.loads(self.user.model)
        else:
            self.model = STANDARD_MODEL
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.user.model = pickle.dumps(self.model)

    # def top_words_cluster(self):
    #     topic_sizes , topic_nums = self.model.get_topic_sizes()
    #     topic_words , word_scores , topic_numbers = self.model.get_topics(max(topic_nums))
    #     top_words = [words[:5] for words in topic_words]
    #     return(topic_nums,topic_sizes)

    def add_document(self, text):
        self.model.add_documents([text])
        new_topic_sizes, new_topic_nums = self.model.get_topic_sizes()
        return len(self.model.documents)-1

    def delete_document(self, id):
        self.model.delete_documents([id])

    def search_by_keywords(self, text):
        tokens = nltk.word_tokenize(text)
        stop_words = set(stopwords.words('english'))
        filtered_sentence = [w for w in tokens if not w in stop_words]
        documents, document_scores, document_ids = self.model.search_documents_by_keywords(
            keywords=filtered_sentence, num_docs=len(self.model.documents))
        docs = []
        for i, j in zip(documents, document_ids):
            docs.append({
                "doc": i,
                "idx": int(j)
            })
        return docs
