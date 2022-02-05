import jieba
import math
import wordcloud
import time

class So_Pmi:
	def __init__(self):
		self.cmt_path = "外卖评论.csv"
		self.posword_path = "pos_words_without_irlv.txt"
		self.negword_path = "neg_words_without_irlv.txt"
		self.pos_pic_path = "pos_words_without_irlv.png"
		self.neg_pic_path = "neg_words_without_irlv.png"
		self.seed_path = "seed_words.txt"
		self.irlv_path = "irrelevant_words.txt"

	#分词
	def cut_words(self, irlv_path, cmt_path):
		irrelevant_words = []
		irlv_words_f = open(irlv_path, "r", encoding="UTF-8")	#无关词所在的文件
		for line in irlv_words_f:
			irrelevant_words.append(line.strip())				#将无关词读入，作为一个列表
		irlv_words_f.close()

		cmt_f = open(cmt_path, "r", encoding="UTF-8")
		cmt_f.readline()			#读掉第一行
		seg_data = []
		cmt_lines = cmt_f.readlines()
		for cmt in cmt_lines:
			cmt = cmt[2:-1]			#从逗号之后开始算作评论内容
			words = jieba.lcut(cmt)
			index = 0
			while (index < len(words)):
				if words[index] in irrelevant_words:
					del words[index]	#出现的无关词均剔除
					continue
				index += 1
			seg_data.append(words)		#每条评论中的分词构成一个列表，所有评论又构成一个列表
		cmt_f.close
		return seg_data

	#确定共现关系
	def collect_cowords(self, seed_path, seg_data):
		def check_words(_list):		#判断一个列表中是否有种子词
			if set(seed_words).intersection(set(_list)):		#看交集是否为空
				return True
			else:
				return False

		cowords_list = list()
		neighborhood_size = 5				#可根据情况自定
		seed_f = open(seed_path, "r", encoding="UTF-8")
		seed_words = [line.strip().split('\t')[0] for line in seed_f]
		seed_f.close
		for cmt in seg_data:  		#这是一条评论里的所有分词  cmt是一个list
			if check_words(cmt):   	#在该条评论里 出现种子词
				for index, word in enumerate(cmt):
					if word in seed_words:
						continue				#如果当前分词是种子词，则不考虑其共现情况
					if index < neighborhood_size:	#每条评论的分析 只在当前分词的至多左右5个（共10个）分词中 查找是否出现 种子词的共现
						left = cmt[:index]
					else :
						left = cmt[index - neighborhood_size : index]
					if index + neighborhood_size > len(cmt):
						right = cmt[index + 1: ]
					else :
						right = cmt[index + 1: neighborhood_size + index + 1]
					context = left + right		#当前分词的上下文。为一个列表
					if check_words(context):
						for word_test in context:
							if word_test in seed_words:
								#上下文中有种子词，则当前分词算作与该种子词发生了共现
								cowords_list.append(word_test + "\t" + word)		
		return cowords_list		#cowords_list里面存的是与种子词相关的共现对  格式为  种子词\t共现词

	#统计词频和共现频率
	def collect_frq(self, seg_data, cowords_list, seed_path):
		#统计所有词语的词频
		def collect_worddict(seg_data):
			word_dict = dict()
			num_of_allwords = 0
			for cmt in seg_data:
				for word in cmt:
					if word not in word_dict:
						word_dict[word] = 1
					else:
						word_dict[word] += 1
			num_of_allwords = sum(word_dict.values())
			return word_dict, num_of_allwords  	#word_dict 存储的是 word在所有文本中出现的总次数
												#num_of_allwords是文本中出现的所有词的个数（包括重复的） 都是分词以后的词
		
		#统计共现对的出现频率
		def collect_cowordsdict(cowords_list):
			co_dict = dict()
			candi_words = list()
			for co_words in cowords_list:
				candi_words.append(co_words.split('\t')[1])		#只把非种子词加入到候选词中去
				if co_words not in co_dict:
					co_dict[co_words] = 1
				else :
					co_dict[co_words] += 1
			return co_dict, candi_words # co_dict统计的是共现出现的次数  是用相当于string'种子词\t共现词'作为键值
										# 而candi_words 是所有的candi_words，且不包括种子词

		word_dict, num_of_allwords = collect_worddict(seg_data)
		co_dict, candi_words = collect_cowordsdict(cowords_list)
		return word_dict, num_of_allwords, co_dict, candi_words

	#计算候选词的pmi值并存储在pmi_dict中
	def get_pmi_dict(self, candi_words, seed_path, word_dict, co_dict, num_of_allwords):
		#pmi公式
		def compute_pmi(p1, p2, p12) :
			return math.log2(p12) - math.log2(p1) - math.log2(p2)

		#统计正向和负向的种子词集
		def collect_seedwords(seed_path):
			seed_f = open(seed_path, "r", encoding="UTF-8")
			pos_seed_words = []
			neg_seed_words = []
			for line in seed_f:
				word = line.strip().split("\t")[0]
				polarity = line.strip().split("\t")[1]
				if polarity == "pos":
					pos_seed_words.append(word)
				else:
					neg_seed_words.append(word)
			return pos_seed_words, neg_seed_words

		#以下计算每个词 的 so_pmi
		pmi_dict = dict()
		pos_seed_words, neg_seed_words = collect_seedwords(seed_path)
		v = len(word_dict)
		print(v)
		for candi_word in set(candi_words):  #用set去重，得到的是不含种子词的候选词
			pos_sum = 0.0
			neg_sum = 0.0
			for pos_word in pos_seed_words:
				# p1 = word_dict[pos_word] / num_of_allwords
				# p2 = word_dict[candi_word] / num_of_allwords
				p1 = (word_dict[pos_word] + 1) / (num_of_allwords + v)
				p2 = (word_dict[candi_word] + 1) / (num_of_allwords + v)	# +1平滑处理
				pair = pos_word + '\t' + candi_word
				if pair not in co_dict:		#判断是否与某个正向种子词有共现
					continue
				p12 = co_dict[pair] / num_of_allwords
				pos_sum += compute_pmi(p1, p2, p12)

			for neg_word in neg_seed_words:
				p1 = word_dict[neg_word] / num_of_allwords
				p2 = word_dict[candi_word] / num_of_allwords
				pair = neg_word + '\t' + candi_word
				if pair not in co_dict:
					continue
				p12 = co_dict[pair] / num_of_allwords
				neg_sum += compute_pmi(p1, p2, p12)
		
			so_pmi = pos_sum - neg_sum
			pmi_dict[candi_word] = so_pmi
		return pmi_dict

	#保存结果并对数据做可视化处理
	def save_res(self, pmi_dict, posword_path, negword_path, pos_pic_path, neg_pic_path):
		pos_dict = dict()
		neg_dict = dict()
		for word, pmi in pmi_dict.items():
			if pmi > 0:
				pos_dict[word] = pmi
			elif pmi < 0:
				neg_dict[word] = pmi
		
		pos_f = open(posword_path, "w+", encoding="UTF-8")
		neg_f = open(negword_path, "w+", encoding="UTF-8")
		sorted_pos = sorted(pos_dict.items(), key=lambda x: x[1], reverse=True)[:50]
		sorted_neg = sorted(neg_dict.items(), key=lambda x: x[1], reverse=False)[:50]
		for i in range(50):
			pos_f.write(str(i + 1) + "\t" + sorted_pos[i][0] + "\t" + str(sorted_pos[i][1]) + "\n")
			neg_f.write(str(i + 1) + "\t" + sorted_neg[i][0] + "\t" + str(sorted_neg[i][1]) + "\n")
		pos_f.close
		neg_f.close
		finish_txt = time.time()
		w_pos = wordcloud.WordCloud(background_color="white", font_path="msyh.ttc", width = 600, height = 400)
		w_neg = wordcloud.WordCloud(font_path="msyh.ttc", width = 600, height = 400)
		w_pos.fit_words(dict(sorted_pos))
		w_pos.to_file(pos_pic_path)
		w_neg.fit_words(dict(sorted_neg))
		w_neg.to_file(neg_pic_path)		#输出词云
		finish_png = time.time()
		return finish_txt, finish_png	#返回执行时间，作为运行参考

	def so_pmi(self):
		start_time = time.time()
		seg_data = self.cut_words(self.irlv_path, self.cmt_path)	#完成分词，舍去了出现率较高的标点和无倾向性的单字
		co_words = self.collect_cowords(self.seed_path, seg_data)	#完成与种子词有共现的词语统计，作为候选词
		word_dict, num_of_allwords, co_dict, candi_words = self.collect_frq(seg_data, co_words, self.seed_path)
						#统计词频和共现对的出现频数
		pmi_dict = self.get_pmi_dict(candi_words, self.seed_path, word_dict, co_dict, num_of_allwords)	#得到每个候选词的pmi值
		txt_end, png_end = self.save_res(pmi_dict, self.posword_path, self.negword_path, self.pos_pic_path, self.neg_pic_path)
						#排序并得出结果
		print("Without Irrelevant Words: Time of Finishing So_Pmi = {0}s".format(txt_end - start_time))
		print("time of drawing wordcloud = {0}s".format(png_end - txt_end))

instance = So_Pmi()
instance.so_pmi()