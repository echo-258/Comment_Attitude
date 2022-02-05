###############################################################
		# !/usr/bin/python
		# File Name: so_pmi.py
		# --coding:utf-8--
		# Created Time:Wed 28 Oct 2020 09:59:56 PM CST
		# Last Modified Time:2020-10-28 21:59:56
		# Author: QoQsay
################################################################


def collect_cowords(self, sentiment_path, seg_data):
	def check_words(sent):
		if set(sentiment_words).intersection(set(sent)):
			return True
		else:
			return False

	cowords_list = list()
	window_size = 5
	sentiment_words = [line.strip().split('\t')[0] for line in open(sentiment_path)]
	for sent in seg_data:  #这是一条评论里的所有分词  sent是一个list
		if check_words(sent):   #在该条评论里 出现种子词
			for index, word in enumerate(sent):  
				if index < window_size:   #每条评论的分析 只在当前分词的至多左右5个（共10个）分词中 查找是否出现 种子词的共现
					left = sent[:index]
				else :
					left = sent[index - window_size : index]
				if index + window_size > len(sent):
					right = sent[index + 1: ]
				else :
					right = sent[index + 1: window_size + index + 1]
				context = left + right + [word]
				if check_words(context):
					for index_pre in range(0, len(context)):
						if check_words([context[index_pre]]): #把该元素当作一个list传进去， 如果成立 则 它后面的词 都算作与该种子词发生了共现 这里的共现有重复（种子词后面相邻的n - 1个都会出现重复）
							for index_post in range(index_pre + 1, len(context)):
								cowords_list.append(context[index_pre] + '\t' + context[index_post])  
	
	return cowords_list #cowords_list里面存的是与种子词相关的共现对  格式为  种子词\t共现词

'''实际上做的工作就是根据种子词找出候选词 即so-pmi算法下共现度最高的一批候选词'''
def collect_candiwords(self, seg_data, cowords_list, sentiment_path) :
	'''计算 pmi'''
	def compute_pmi(p1, p2, p12) :
		return math.log2(p12) - math.log2(p1) - math.log2(p2)

	'''统计词频 计算p1, p2, p12 '''
	def collect_worddict(seg_data):
		word_dict = dict()
		num_of_allwords = 0
		for line in seg_data:
			for word in line:
				if word not in word_dict:
					word_dict[word] = 1
				else :
					word_dict[word] += 1
		num_of_allwords = sum(word_dict.values())

		return word_dict, num_of_allwords # word_dict 存储的是 word在所有文本中出现的总次数  num_of_allwords是文本中出现的所有词的个数（包括重复的） 都是分词以后的词
	
	def collect_cowordsdict(cowords_list):
		co_dict = dict()
		candi_words = list()
		for co_words in cowords_list:
			candi_words.extend(cowords.split('\t'))
			if co_words not in co_dict:
				co_dict[co_words] = 1
			else :
				co_dict[co_words] += 1

		return co_dict, candi_words # co_dict统计的是共现出现的次数  是用相当于string'种子词\t共现词'作为键值 但就像上面函数提到的 这种共现对会重复
									# 而candi_words 是所有的candi_words+种子词本身

	'''统计种子词'''
	def collect_sentiwords(sentiment_path, word_dict):
		pos_words = set([line.strip().split('\t')[0] for line in open(sentiment_path) if line.strip().split('\t')[1] == 'pos']).intersection(set(word_dict.keys()))
		neg_words = set([line.strip().split('\t')[0] for line in open(sentiment_path) if line.strip().split('\t')[1] == 'neg']).intersection(set(word_dict.keys()))

		return pos_words, neg_words #返回的是pos种子词 和 neg种子词的集合  疑问有必要和word_dict的键值取交集？

	'''计算每个词 的 so_pmi '''
	def compute_sopmi(candi_words, pos_words, neg_words, word_dict, cowords_dict, num_of_allwords) :
		pmi_dict = dict()
		for candi_word in set(candi_words):  #所有的p 都有了 这算pmi
			pos_sum = 0.0
			neg_sum = 0.0
			for pos_word in pos_words:
				p1 = word_dict[pos_word] / num_of_allwords
				p2 = word_dict[candi_word] / num_of_allwords
				pair = pos_word + '\t' + candi_word
				if pair not in co_dict:
					continue
				p12 = co_dict[pair] / num_of_allwords
				pos_sum += compute_pmi(p1, p2, p12)

		    for neg_word in neg_words:
                p1 = word_dict[neg_word] / num_of_allwords
                p2 = word_dict[candi_word] / num_of_allwords
                pair = neg_word + '\t' + candi_word
                if pair not in co_dict:
                    continue
                p12 = co_dict[pair] / num_of_allwords
                neg_sum += compute_pmi(p1, p2, p12)
		
			so_pmi = pos_sum - neg_sum
			pmi_dict[candi_word] = so_pmi
		#这里有点问题，这样倒是可以避免种子词共现本身了，但是会有种子词共现其他种子词的情况  不过按道理来说candi_words确实可以出现种子词

		return pmi_dict


	word_dict, num_of_allwords = collect_worddict(seg_data)
	co_dict, candi_words = collect_cowordsdict(cowords_list)
	pos_words, neg_words = collect_sentiwords(sentiment_path, word_dict)
	pmi_dict = compute_sopmi(candi_words, pos_words, neg_words, word_dict, co_dict, num_of_allwords)
	return pmi_dict
