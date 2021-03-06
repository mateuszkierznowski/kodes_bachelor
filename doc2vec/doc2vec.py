from gensim.models.doc2vec import Doc2Vec
from nltk import word_tokenize
import gensim
import pickle
import random
import math
import pandas as pd
from xgboost import XGBClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble.gradient_boosting import GradientBoostingClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.model_selection import cross_validate
import numpy as np
from sklearn.metrics import recall_score
from sklearn.metrics import precision_score
from sklearn.metrics import f1_score
from sklearn.metrics import accuracy_score




sv = SVC()
RFC = RandomForestClassifier()
GaussianN = GaussianNB()
KNC = KNeighborsClassifier(n_neighbors=20)
xgboost = XGBClassifier()
gradientboost = GradientBoostingClassifier()

with open('objects/lematized_sentences', 'rb') as f:
    lematized_sentences = pickle.load(f)

df_full = pd.read_csv('dataframes/full_csv', index_col=[0])

with open('objects/lematized_part_sentences', 'rb') as f:
    lematized_part_sentences = pickle.load(f)

df = pd.read_csv('dataframes/binary_cls.csv')

sv_dict = {'prec':[], 'recall': [], 'f1': [], 'acc': []}
rfr_dict = {'prec':[], 'recall': [], 'f1': [], 'acc': []}
gn_dict = {'prec':[], 'recall': [], 'f1': [], 'acc': []}
knn_dict = {'prec':[], 'recall': [], 'f1': [], 'acc': []}


def doc2v(korp, data_frame):
    np.random.seed(42)
    lemtized_part_sentences = [word_tokenize(sen) for sen in korp]

    klasy = data_frame['klasa']

    train_documnets = []
    test_documents = []


    for number, sen in enumerate(lemtized_part_sentences):
        tagged_doc = gensim.models.doc2vec.TaggedDocument(sen, list(str(klasy[number])))
        train_documnets.append(tagged_doc)

    train_documnets = random.sample(train_documnets, len(train_documnets))

    proc = math.ceil(len(train_documnets)/10)

    test_documents = train_documnets[0:proc]
    train_documnets = train_documnets[proc:len(train_documnets)]
    #creating doc2vec model based on train documents
    np.random.seed(42)
    model = gensim.models.doc2vec.Doc2Vec(vector_size=50, min_count=1, epochs=20)
    model.build_vocab(train_documnets)
    model.train(train_documnets, total_examples=model.corpus_count, epochs=model.epochs)

    def vector_for_learning(model, input_docs):
        sents = input_docs
        targets, feature_vectors = zip(*[(doc.tags[0], model.infer_vector(doc.words, steps=20)) for doc in sents])
        return targets, feature_vectors

    y_train, X_train = vector_for_learning(model, train_documnets)
    y_test, X_test = vector_for_learning(model, test_documents)

    np.random.seed(42)
    sv.fit(X_train, y_train)
    sv.predict(X_test)
    pred = sv.predict(X_test)
    sv_dict['recall'].append(recall_score(pred, y_test, average='macro'))
    sv_dict['prec'].append(precision_score(pred, y_test, average='macro'))
    sv_dict['f1'].append(f1_score(pred, y_test, average='macro'))
    sv_dict['acc'].append(accuracy_score(pred, y_test))

    # acc 0.7330210772833724%
    RFC.fit(X_train, y_train)
    RFC.predict(X_test)
    pred = RFC.predict(X_test)
    rfr_dict['recall'].append(recall_score(pred, y_test, average='macro'))
    rfr_dict['prec'].append(precision_score(pred, y_test, average='macro'))
    rfr_dict['f1'].append(f1_score(pred, y_test, average='macro'))
    rfr_dict['acc'].append(accuracy_score(pred, y_test))
    # acc 0.7412177985948478

    GaussianN.fit(X_train, y_train)
    pred = GaussianN.predict(X_test)
    gn_dict['recall'].append(recall_score(pred, y_test, average='macro'))
    gn_dict['prec'].append(precision_score(pred, y_test, average='macro'))
    gn_dict['f1'].append(f1_score(pred, y_test, average='macro'))
    gn_dict['acc'].append(accuracy_score(pred, y_test))
    # acc 0.7037470725995316
    KNC.fit(X_train, y_train)
    pred = KNC.predict(X_test)
    knn_dict['recall'].append(recall_score(pred, y_test, average='macro'))
    knn_dict['prec'].append(precision_score(pred, y_test, average='macro'))
    knn_dict['f1'].append(f1_score(pred, y_test, average='macro'))
    knn_dict['acc'].append(accuracy_score(pred, y_test))


for i in range(5):
    doc2v(lematized_sentences, df_full)

sv_dict = {key: np.mean(value) for key, value in sv_dict.items()}
rfr_dict = {key: np.mean(value) for key, value in rfr_dict.items()}
gn_dict = {key: np.mean(value) for key, value in gn_dict.items()}
knn_dict = {key: np.mean(value) for key, value in knn_dict.items()}
