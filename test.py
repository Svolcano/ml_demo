from sklearn.model_selection import train_test_split  #划分训练集和测试集
from sklearn.metrics import accuracy_score   ##判断准确度
from sklearn.tree import DecisionTreeClassifier   ##选取决策树
from sklearn.datasets import load_iris  ##选取数据集

#准备数据集
iris=load_iris()
# 获取特征集和分类标识
features = iris.data  #属性
labels = iris.target  #标签

#70%测试集，30%训练集
train_features, test_features, train_labels, test_labels = train_test_split(features,labels,test_size=0.3, random_state=0)
print(train_features)
#属性(训练+测试)+标签(训练+测试)   

# 创建 CART 分类树
cart = DecisionTreeClassifier(criterion='gini')   ##实例，一棵新的树
# 拟合构造 CART 分类树
cart = cart.fit(train_features, train_labels)      ##执行分类树的方法，做拟合
# 用 CART 分类树做预测
test_predict = cart.predict(test_features)        ##用测试集验证拟合的结果

# 预测结果与测试集结果作比对
score = accuracy_score(test_labels, test_predict)  #真实的标签和预测的标签
print("CART 分类树准确率 %.4lf" % score)