# -*- coding: utf-8 -*-
"""Predict422Week2_Kun Yang.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1XlbgyQl_63qbjX6zZe-aIVM42EJOswC8
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt 
from google.colab import files

#test uploading csv file to google colab
uploaded = files.upload()

for fn in uploaded.keys():
  print('User uploaded file "{name}" with length {length} bytes'.format(
      name=fn, length=len(uploaded[fn])))

bank=pd.read_csv('bank.csv', sep = ';')

print(bank.shape)

bank.dropna()
print(bank.shape)

# use dictionary objects for mapping to 0/1 binary or category
response_to_binary = {'no' : 0, 'yes' : 1}
YESresponse = np.array(bank['response'].map(response_to_binary))

default_to_binary = {'no' : 0, 'yes' : 1}
YESdefault = np.array(bank['default'].map(default_to_binary))

housing_to_binary = {'no' : 0, 'yes' : 1}
YEShousing = np.array(bank['housing'].map(housing_to_binary))

loan_to_binary = {'no' : 0, 'yes' : 1}
YESloan = np.array(bank['loan'].map(loan_to_binary))

from sklearn.metrics import roc_auc_score

# specify the two classifiers being evaluated
from sklearn.naive_bayes import BernoulliNB
from sklearn.linear_model import LogisticRegression
names = ["Naive_Bayes", "Logistic_Regression"]
classifiers = [BernoulliNB(alpha=1.0, binarize=0.5, 
                           class_prior = [0.5, 0.5], fit_prior=False), 
               LogisticRegression()]

#select response variable the three binary explanatory variables
model_data = np.array([YESdefault,\
    YEShousing,\
    YESloan,\
    YESresponse]).T

RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)
np.random.shuffle(model_data)

print('\nData dimensions:', model_data.shape)

# specify the k-fold cross-validation design
from sklearn.model_selection import KFold

# ten-fold cross-validation employed here
N_FOLDS = 10

# set up numpy array for storing results
cv_results = np.zeros((N_FOLDS, len(names)))

print(cv_results.shape)

kf = KFold(n_splits = N_FOLDS, shuffle=False, random_state = RANDOM_SEED)

index_for_fold = 0  # fold count initialized 
for train_index, test_index in kf.split(model_data):
    print('\nFold index:', index_for_fold,
          '------------------------------------------')
#   note that 0:model_data.shape[1]-1 slices for explanatory variables
#   and model_data.shape[1]-1 is the index for the response variable    
    X_train = model_data[train_index, 0:model_data.shape[1]-1]
    X_test = model_data[test_index, 0:model_data.shape[1]-1]
    y_train = model_data[train_index, model_data.shape[1]-1]
    y_test = model_data[test_index, model_data.shape[1]-1]   
    print('\nShape of input data for this fold:',
          '\nData Set: (Observations, Variables)')
    print('X_train:', X_train.shape)
    print('X_test:',X_test.shape)
    print('y_train:', y_train.shape)
    print('y_test:',y_test.shape)

    index_for_method = 0  # initialize
    for name, clf in zip(names, classifiers):
        print('\nClassifier evaluation for:', name)
        print('  Scikit Learn method:', clf)
        clf.fit(X_train, y_train)  # fit on the train set for this fold
        # evaluate on the test set for this fold
        y_test_predict = clf.predict_proba(X_test)
        fold_method_result = roc_auc_score(y_test, y_test_predict[:,1]) 
        print('Area under ROC curve:', fold_method_result)
        cv_results[index_for_fold, index_for_method] = fold_method_result
        index_for_method += 1
  
    index_for_fold += 1

cv_results_df = pd.DataFrame(cv_results)
cv_results_df.columns = names

print('\n----------------------------------------------')
print('Average results from ', N_FOLDS, '-fold cross-validation\n',
      '\nMethod                 Area under ROC Curve', sep = '')     
print(cv_results_df.mean())

#from 10-fold cross validation result, we can see Logistic_regression has slightly larger area under ROC curve, so this is the method I recommend
print(cv_results_df)

#now test all 8 combination of three binary variables (default, housing, loan), compare predict vs actual using first the recommended model - logistical regression

my_default = np.array([1, 1, 1, 1, 0, 0, 0, 0], np.int32)
my_housing = np.array([1, 1, 0, 0, 1, 1, 0, 0], np.int32)
my_loan = np.array([1, 0, 1, 0, 1, 0, 1, 0], np.int32)

my_X_test = np.vstack([my_default, my_housing, my_loan]).T

# fit logistic regression to full data set
clf = LogisticRegression()
X_train = model_data[:, 0:model_data.shape[1]-1]
y_train = model_data[:, model_data.shape[1]-1]
clf.fit(X_train, y_train)

# predict specific test cases covering all situations
y_my_test_predict = clf.predict_proba(my_X_test)

# create DataFrame for displaying test cases and predicted probabilities
my_targeting_df = pd.DataFrame(np.hstack([my_X_test, y_my_test_predict]))
my_targeting_df.columns = ['default', 'housing', 'loan', 
                           'predict_NO', 'predict_YES']
print('\n\nLogistic regression model predictions for test cases:')
print(my_targeting_df)

"""group 3 & group 7 have largest predict_YES probability, so those are the best target marketing efforts

Group 3: default = true, housing = false, loan = false

Group 7, same as group 3 except default = false

So, basically if the customer does not have mortgage and loan, no matter his credit default history, it has around 16~18% probability getting a term deposit.

Out of curiosity, I want to take a look at the less preferred model: Naive Bayes classification to see what results it gets here...
"""

clf2=BernoulliNB(alpha=1.0, binarize=0.5, 
                           class_prior = [0.5, 0.5], fit_prior=False)

clf2.fit(X_train, y_train)

y_my_test_predict2 = clf2.predict_proba(my_X_test)

my_targeting_df2 = pd.DataFrame(np.hstack([my_X_test, y_my_test_predict2]))
my_targeting_df2.columns = ['default', 'housing', 'loan', 
                           'predict_NO', 'predict_YES']
print('\n\nNaive Bayes model predictions for test cases:')
print(my_targeting_df2)

"""Ok, so Naive Bayes model give the same suggestion as group 3 & group 7, however the predict_YES probability is largely overstated here.

below are just some practice.... I want to see if I just choose one binary variable here, default, what kind of performance/confusion matrix if I use that to predict whether client will subscribe term depoit.
"""

from sklearn.linear_model import SGDClassifier
sgd_clf=SGDClassifier(random_state=42)
sgd_clf.fit(model_data[:,0].reshape(-1,1),model_data[:,3])

from sklearn.model_selection import cross_val_predict
y_train_pred=cross_val_predict(sgd_clf,model_data[:,0].reshape(-1,1),model_data[:,3],cv=3)

from sklearn.metrics import confusion_matrix
confusion_matrix(model_data[:,3],y_train_pred)





"""I think since the customer with positive response to subscribe to term deposit  are very small part of the total population, that make the classification model (with three factors we chose) have very limited predict accuracy. we need to introduce more variable in order to improve the model here."""