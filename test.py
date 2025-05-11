import random, string 

random_id = random.randint(1000, 9999) 
letters = ''.join(random.choices(string.ascii_uppercase, k=2))
new_file_id =  str(letters + str(random_id))

print(new_file_id)