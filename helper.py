from dateparser import parse
def get_int_input(var_name):
	while True:
		try:
			user_input = int(input("Введите "+var_name+": "))
		except Exception as e:
			print("Ошибка при введении "+var_name+": "+str(e)+"")
		else:
			return user_input

def get_str_input(var_name):
	while True:
		try:
			user_input = input("Введите"+var_name+": ")
		except Exception as e:
			print("Ошибка при введении "+var_name+": "+str(e)+"")
		else:
			return user_input

def get_bool_input(var_name):
	while True:
		try:
			user_input = input("Введите "+var_name+" t/f: (f)")
		except Exception as e:
			print("Ошибка при введении "+var_name+": "+str(e)+"")
		else:
			return user_input in ["True","t","true"]

def get_str_date(var_name):
	while True:
		try:
			sUser_input = get_str_input("Введите "+var_name+". Формат Y.m.d H:M:S: ")
			oDate_time = parse(sUser_input)
			sDate = oDate_time.strftime("%Y-%m-%d %H:%M:%S")
		except Exception as e:
			print("Ошибка при парсинга даты: "+str(e)+"")
			continue
		else:
			return sDate

def get_sql_part():
	bShould_use_date = get_bool_input("Стоит ли использовать дату?")
	if bShould_use_date:
		sS_date = get_str_date("s_date")
		sF_date = get_str_date("f_date")
		sS_date_part = "AND P.date >= '%s'" % (sS_date)
		sF_date_part = "AND P.date <= '%s'" % (sF_date)
	else:
		sS_date_part = ""
		sF_date_part = ""	
	return sS_date_part,sF_date_part

def equal_sentiment():
	iSentiment_host_user_id = get_int_input("id пользователя, у которого вы будете брать sentiment")
	iProject_id = get_int_input("p_id")
	iProject_host_user_id = get_int_input("id владельца проекта")
	iChange_user_id = get_int_input("id пользователя, которому нужно поменять sentiment")
	sS_date_part,sF_date_part = get_sql_part()
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


def main():
	while True:
		try:
			user_choise = input("Введите команду: ").strip()
		except Exception:
			continue
		else:
			if(user_choise == "s"):
				equal_sentiment()
			break

main()