import sys
import csv
from collections import Counter
from math import log2

class Node:
    def __init__(self, feature, subtrees):
        self.feature = feature
        self.subtrees = subtrees

    def isLeaf(self):
        return False

class Leaf:
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return 'Leaf(' + self.value + ')'

    def isLeaf(self):
        return True

class ID3:
    def __init__(self, limit):
        self.root = None
        self.limit = limit

    def fit(self, train_set, features, features_V, depth):
        self.root = self.id3(train_set, train_set, features, features_V, depth)

    def id3(self, data, data_parents, features, features_V, depth):
        if not data:
            y = sorted([row[-1] for row in data_parents])
            c = Counter(y)
            value = c.most_common(1)[0][0]
            return Leaf(value)

        y = sorted([row[-1] for row in data])
        c = Counter(y)
        value, counter = c.most_common(1)[0]
        if not features or len(data) == counter:
            return Leaf(value)

        if self.limit is None or depth < self.limit:
            discriminative_feature = self.information_gain(data, features, features_V)
            subtrees = {}
            new_features = {items[0]: items[1] for items in features.items()}
            new_features.pop(discriminative_feature)
            for value in features_V[discriminative_feature]:
                data_for_value = [row for row in data if row[features[discriminative_feature]] == value]
                t = self.id3(data_for_value, data, new_features, features_V, depth + 1)
                subtrees[value] = t
            return Node(discriminative_feature, subtrees)
        else:
            y = sorted([row[-1] for row in data])
            c = Counter(y)
            value = c.most_common(1)[0][0]
            return Leaf(value)

    def information_gain(self, data, features, features_V):
        entropy = self.get_entropy(data)
        information_gains = dict()
        for feature in features.keys():
            sum = 0
            feature_values = features_V[feature]
            for value in feature_values:
                data_for_value = [row for row in data if row[features[feature]] == value]
                sum += len(data_for_value) / len(data) * self.get_entropy(data_for_value)
            information_gains[feature] = entropy - sum
            print('IG({}) = {:.5f}'.format(feature, information_gains[feature]), end=' ')
        print()
        max_value = max(information_gains.values())
        list_max = []
        for item in information_gains.items():
            if item[1] == max_value:
                list_max.append(item[0])
        feature_max = sorted(list_max)[0]
        return feature_max

    def get_entropy(self, data):
        class_values = [row[-1] for row in data]
        all_values = len(class_values)
        values_counter = dict()
        for value in class_values:
            counter = values_counter.get(value)
            if counter:
                counter += 1
            else:
                counter = 1
            values_counter[value] = counter
        entropy = 0
        for key in values_counter.keys():
            entropy -= values_counter[key] / all_values * log2(values_counter[key] / all_values)
        return entropy

    def ispis(self, root, depth, line):
        if root.isLeaf():
            print('{}{}'.format(line, root.value))
        else:
            for items in root.subtrees.items():
                self.ispis(items[1], depth + 1, line + '{}:{}={} '.format(depth, root.feature, items[0]))


    def predict(self, root, row, features, features_V, train_set, predictions):
        if root.isLeaf():
            predictions.append(root.value)
        else:
            idx = features[root.feature]
            if root.subtrees.get(row[idx]):
                new_train_set = [row_train for row_train in train_set if row_train[idx] == row[idx]]
                self.predict(root.subtrees[row[idx]], row, features, features_V, new_train_set, predictions)
            else:
                y = sorted([row_train[-1] for row_train in train_set])
                c = Counter(y)
                value = c.most_common(1)[0][0]
                predictions.append(value)

def main():
    arguments = []
    for s in sys.argv:
        arguments.append(s)

    train_set = []
    with open(arguments[1], 'r') as csv_file:
        csvreader = csv.reader(csv_file)
        header = next(csvreader)
        header = header[:-1]
        features = dict()
        i = 0
        for x in header:
            features[x] = i
            i += 1
        for row in csvreader:
            train_set.append(row)

        features_V = {x:set() for x in features}
        for x in features:
            for row in train_set:
                features_V[x].add(row[features[x]])
    print(train_set)
    print(features)
    print(features_V)
    limit = None
    if len(arguments) > 3:
        limit = int(arguments[3])
    model = ID3(limit)
    ##treniranje modela
    model.fit(train_set, features, features_V, depth=0)
    ##ispis BRANCHES
    print('[BRANCHES]:')
    model.ispis(model.root, 1, '')
    #testiranje modela/predikcija
    test_set = []
    with open(arguments[2], 'r') as csv_file:
        csvreader = csv.reader(csv_file)
        next(csvreader)
        for row in csvreader:
            test_set.append(row)

    print('[PREDICTIONS]:', end=' ')
    predictions = []
    for row in test_set:
        model.predict(model.root, row, features, features_V, train_set, predictions)
    print(" ".join(predictions))
    ##racunanje uspjesnosti
    true_classes = [row[-1] for row in test_set]
    counter = 0
    for i in range(len(predictions)):
        if predictions[i] == true_classes[i]:
            counter += 1
    print('[ACCURACY]: {:.5f}'.format(counter / len(true_classes)))
    #confusion matrix
    unique_classes = sorted(list(set(true_classes)))
    confusion_matrix = [[0 for i in range(len(unique_classes))] for j in range(len(unique_classes))]
    for i in range(len(true_classes)):
        confusion_matrix[unique_classes.index(true_classes[i])][unique_classes.index(predictions[i])] += 1
    print('[CONFUSION_MATRIX]:')
    for i in range(len(unique_classes)):
        for j in range(len(unique_classes)):
            print(confusion_matrix[i][j], end=' ')
        print()
    return


main()