#生成一个文件word_sta.txt，作为选择种子词和无关词的参考
import jieba

fname = "外卖评论.csv"
word_dict = dict()
cmt_f = open(fname, "r", encoding='UTF-8')
firstline = cmt_f.readline()        #读掉第一行
for review in cmt_f.readlines():
    review = review[2:-1]           #截取逗号之后的部分
    words = jieba.lcut(review)
    for word in words:              #统计词频
        if word in word_dict:
            word_dict[word] += 1
        else:
            word_dict[word] = 1
cmt_f.close

sta_f=open("word_sta.txt", "w+", encoding='UTF-8')
for item in sorted(word_dict.items(), key=lambda x: x[1], reverse=True):
    sta_f.write(item[0] + "\t" + str(item[1]) + "\n")