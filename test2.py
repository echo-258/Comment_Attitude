import jieba

irrelevant_words = []
irlv_words_f = open("irrelevant_words.txt", "r", encoding='UTF-8')
for line in irlv_words_f:
    irrelevant_words.append(line.strip())
irlv_words_f.close()

fname = "外卖评论.csv"
cmt_f = open(fname, "r", encoding='UTF-8')
firstline = cmt_f.readline()
seg_data = []
cmt_lines = cmt_f.readlines()
for review in cmt_lines:
    review = review[2:-1]
    words = jieba.lcut(review)
    index = 0
    while (index < len(words)):
        if words[index] in irrelevant_words:
            del words[index]
            continue
        index += 1
    seg_data.append(words)
cmt_f.close

seg_data_res = open("seg_data_res.txt", "w+", encoding='UTF-8')
for words in seg_data:
    seg_data_res.write("/".join(words) + "\n")