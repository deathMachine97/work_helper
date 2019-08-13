from dateparser import parse
import pyperclip
from urllib.parse import urlparse
import re
def get_int_input(var_name):
	while True:
		try:
			user_input = int(input("Введите "+str(var_name)+": "))
		except Exception as e:
			print("Ошибка при введении "+str(var_name)+": "+str(e)+"")
		else:
			return user_input

def get_str_input(var_name):
	while True:
		try:
			user_input = input("Введите "+str(var_name)+": ")
		except Exception as e:
			print("Ошибка при введении "+str(var_name)+": "+str(e)+"")
		else:
			return user_input

def get_bool_input(var_name):
	while True:
		try:
			user_input = input("Введите "+str(var_name)+" t/f: (f) ")
		except Exception as e:
			print("Ошибка при введении "+str(var_name)+": "+str(e)+"")
		else:
			return user_input in ["True","t","true"]

def get_str_date(var_name):
	while True:
		try:
			sUser_input = get_str_input(str(var_name)+". Формат Y.m.d H:M:S: ")
			oDate_time = parse(sUser_input)
			sDate = oDate_time.strftime("%Y-%m-%d %H:%M:%S")
		except Exception as e:
			print("Ошибка при парсинга даты: "+str(e)+"")
			continue
		else:
			return sDate

def get_sql_date_part(sSql_var_name):
	bShould_use_date = get_bool_input("Стоит ли использовать дату?")
	if bShould_use_date:
		sS_date = get_str_date("s_date")
		sF_date = get_str_date("f_date")
		sS_date_part = "AND "+str(sSql_var_name)+"date >= '%s'" % (sS_date)
		sF_date_part = "AND "+str(sSql_var_name)+"date <= '%s'" % (sF_date)
	else:
		sS_date_part = ""
		sF_date_part = ""	
	return sS_date_part,sF_date_part

def copy_to_buffer(sVar):
	pyperclip.copy(str(sVar))
	print("SQL запрос лежит в буфере обмена")

class Equalize_sentiment(object):
	def __init__(self):
		iSentiment_host_user_id = get_int_input("id пользователя, у которого вы будете брать sentiment")
		iProject_id = get_int_input("p_id")
		iProject_host_user_id = get_int_input("id владельца проекта")
		iChange_user_id = get_int_input("id пользователя, которому нужно поменять sentiment")
		sS_date_part,sF_date_part = get_sql_date_part("P.")
		print("""
			INSERT IGNORE INTO sentiment(smi_social, news_id, sentiment, sentiment_type, user_id)
			SELECT P.type as smi_social, P.item_id as news_id, S.sentiment, 'manual' as sentiment_type, %d as user_id   
			FROM project_items.project_items_%d P, imasv2.sentiment S  
			WHERE  P.item_id = S.news_id
			%s
			%s
			AND S.user_id = %d
			AND P.project_id IN(%d);
		""" % (iChange_user_id,iProject_host_user_id,sS_date_part,sF_date_part,iSentiment_host_user_id,iProject_id))

class Change_sentiment(object):
	def __init__(self):
		bKnow_project_host_user_id = get_bool_input("Вы знаете id владельца проекта?")
		iProject_id,iProject_host_user_id,iChange_user_id,iNew_sentiment,iOld_sentiment,sS_date_part,sF_date_part = self.get_variables(bKnow_project_host_user_id)
		copy_to_buffer("""
			SELECT P.type as smi_social, P.item_id as news_id, %d as sentiment, 'manual' as sentiment_type, %d as user_id
			FROM project_items.project_items_%d P, imasv2.sentiment S
			WHERE P.project_id = %d
			AND S.sentiment = %d
			AND P.item_id = S.news_id
			%s
			%s
		""" % (iNew_sentiment,iChange_user_id,iProject_host_user_id,iProject_id,iOld_sentiment,sS_date_part,sF_date_part))

	def get_variables(self,bKnow_project_host_user_id):
		iOld_sentiment = get_int_input("с какой тональности нужно поменять")
		iNew_sentiment = get_int_input("новую тональность")
		iProject_id = get_int_input("p_id")
		if bKnow_project_host_user_id:
			iProject_host_user_id = get_int_input("id владельца проекта")
		else:
			copy_to_buffer("SELECT user_id FROM imasv2.projects WHERE id=%d"%(iProject_id))
			iProject_host_user_id = get_int_input("id владельца проекта")
		iChange_user_id = get_int_input("id пользователя, которому нужно поменять sentiment")
		sS_date_part,sF_date_part = get_sql_date_part("P.")
		return iProject_id,iProject_host_user_id,iChange_user_id,iNew_sentiment,iOld_sentiment,sS_date_part,sF_date_part

class Search_item_in_base(object):
	def __init__(self):
		sUrls = get_str_input("url СМИ новостей")
		sUrls = sUrls.replace("'","")
		sUrls = sUrls.replace('"',"")
		url_combination = []
		for url in sUrls.split(" "):
			splitted = urlparse(url)
			cut_part = len(splitted.scheme+"://"+splitted.netloc)
			first_part = splitted.netloc
			second_part = url[cut_part:]
			match = re.search(r'^www\.', first_part)
			if match:
				first_part = first_part.replace('www.', '')
			url_combination.append("'https://"+first_part+second_part+"'")
			url_combination.append("'https://www."+first_part+second_part+"'")
			url_combination.append("'http://"+first_part+second_part+"'")
			url_combination.append("'http://www."+first_part+second_part+"'")
		print(url_combination)

def main():
	Search_item_in_base()
	# while True:
	# 	try:
	# 		user_choise = input("Введите команду: ").strip()
	# 	except Exception:
	# 		continue
	# 	else:
	# 		if(user_choise == "eq_s"):
	# 			Equalize_sentiment()
	# 		elif (user_choise == "ch_s"):
	# 			Change_sentiment()
	# 		break

main()