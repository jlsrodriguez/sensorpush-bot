
auth_file = open('step2_auth_raw.txt','r')
content = auth_file.read()
auth_list = content.split(":")
fin_list = auth_list[1]
fin_list = fin_list[0:len(fin_list)-2]
auth_file.close()

with open(r'step2_trimmed_auth.txt','w') as fp:
    fp.write(fin_list)
